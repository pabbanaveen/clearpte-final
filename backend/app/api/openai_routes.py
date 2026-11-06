import logging
from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile, os, re
from difflib import SequenceMatcher
from typing import List, Dict, Optional
from app.services.openai_client import _get_openai_client
from app.core.uploads import read_audio_upload

router = APIRouter()
logger = logging.getLogger(__name__)

def normalize_token(tok: str) -> str:
    return re.sub(r"[^\w']+", "", tok).lower().strip()

def tokenize(text: str) -> List[str]:
    # basic tokenizer: words including apostrophes (it's)
    if not text:
        return []
    return re.findall(r"[A-Za-z0-9']+", text)

def try_import_inflect():
    try:
        import inflect
        return inflect.engine()
    except Exception:
        return None

INFLECT_ENGINE = try_import_inflect()

def is_plural_singular_mismatch(a: str, b: str) -> bool:
    """Return True when a/b look like plural<->singular of each other."""
    if not a or not b:
        return False
    a_l = a.lower()
    b_l = b.lower()
    if a_l == b_l:
        return False
    # naive suffix checks
    if a_l.endswith('s') and a_l[:-1] == b_l:
        return True
    if b_l.endswith('s') and b_l[:-1] == a_l:
        return True
    if a_l.endswith('es') and a_l[:-2] == b_l:
        return True
    if b_l.endswith('es') and b_l[:-2] == a_l:
        return True
    # try inflect for irregular plurals (children -> child etc.)
    if INFLECT_ENGINE:
        try:
            # inflect.singular_noun(x) returns singular for plural input, otherwise False
            if INFLECT_ENGINE.singular_noun(a_l) and INFLECT_ENGINE.singular_noun(a_l) == b_l:
                return True
            if INFLECT_ENGINE.singular_noun(b_l) and INFLECT_ENGINE.singular_noun(b_l) == a_l:
                return True
        except Exception:
            pass
    return False

def build_token_analysis(ref_tokens: List[str], trans_tokens: List[str]) -> Dict:
    """Run a diff and return detailed token alignment + plural/singular flags."""
    matcher = SequenceMatcher(None, ref_tokens, trans_tokens)
    analysis = []
    ref_count = len(ref_tokens)
    trans_count = len(trans_tokens)
    matches = 0
    substitutions = 0
    missing = 0
    extras = 0
    plural_mismatches = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for ri, tj in zip(range(i1, i2), range(j1, j2)):
                ref_tok = ref_tokens[ri]
                trans_tok = trans_tokens[tj]
                analysis.append({
                    "ref_index": ri,
                    "ref_token": ref_tok,
                    "trans_index": tj,
                    "trans_token": trans_tok,
                    "status": "match",
                    "plural_singular_mismatch": False
                })
                matches += 1
        elif tag == "replace":
            # map pairwise where possible, leftover are substitutions/missing/extra
            ref_slice = ref_tokens[i1:i2]
            trans_slice = trans_tokens[j1:j2]
            minlen = min(len(ref_slice), len(trans_slice))
            # pairwise substitutions
            for k in range(minlen):
                ri = i1 + k
                tj = j1 + k
                ref_tok = ref_slice[k]
                trans_tok = trans_slice[k]
                plural_flag = is_plural_singular_mismatch(ref_tok, trans_tok)
                if plural_flag:
                    plural_mismatches += 1
                substitutions += 1
                analysis.append({
                    "ref_index": ri,
                    "ref_token": ref_tok,
                    "trans_index": tj,
                    "trans_token": trans_tok,
                    "status": "substitution",
                    "plural_singular_mismatch": plural_flag
                })
            # leftover reference tokens = missing
            for k in range(minlen, len(ref_slice)):
                ri = i1 + k
                ref_tok = ref_slice[k]
                missing += 1
                analysis.append({
                    "ref_index": ri,
                    "ref_token": ref_tok,
                    "trans_index": None,
                    "trans_token": None,
                    "status": "missing",
                    "plural_singular_mismatch": False
                })
            # leftover trans tokens = extra
            for k in range(minlen, len(trans_slice)):
                tj = j1 + k
                trans_tok = trans_slice[k]
                extras += 1
                analysis.append({
                    "ref_index": None,
                    "ref_token": None,
                    "trans_index": tj,
                    "trans_token": trans_tok,
                    "status": "extra",
                    "plural_singular_mismatch": False
                })
        elif tag == "delete":
            for ri in range(i1, i2):
                ref_tok = ref_tokens[ri]
                missing += 1
                analysis.append({
                    "ref_index": ri,
                    "ref_token": ref_tok,
                    "trans_index": None,
                    "trans_token": None,
                    "status": "missing",
                    "plural_singular_mismatch": False
                })
        elif tag == "insert":
            for tj in range(j1, j2):
                trans_tok = trans_tokens[tj]
                extras += 1
                analysis.append({
                    "ref_index": None,
                    "ref_token": None,
                    "trans_index": tj,
                    "trans_token": trans_tok,
                    "status": "extra",
                    "plural_singular_mismatch": False
                })

    stats = {
        "ref_tokens": ref_count,
        "trans_tokens": trans_count,
        "matches": matches,
        "substitutions": substitutions,
        "missing": missing,
        "extra": extras,
        "plural_mismatches": plural_mismatches,
    }
    return {"analysis": analysis, "stats": stats}

def compute_content_score_from_stats(stats: Dict) -> int:
    if stats["ref_tokens"] == 0:
        return 0
    matched = stats["matches"]
    # simple metric: match rate as percent
    score = int(round(100.0 * matched / stats["ref_tokens"]))
    return max(0, min(100, score))

def compute_fluency_from_text(transcribed_text: str) -> int:
    """Very simple heuristic: penalize for filler words. This is only a rough indicator."""
    fillers = {"um", "uh", "hmm", "erm", "mm", "uhm", "ah"}
    toks = [t.lower() for t in tokenize(transcribed_text)]
    filler_count = sum(1 for t in toks if t in fillers)
    # each filler reduces score by 5 points, up to 30 points total
    penalty = min(30, filler_count * 5)
    base = 100 - penalty
    return max(0, min(100, base))

import re
def parse_scores_from_llm(text: str) -> Dict[str, Optional[int]]:
    results = {"Content": None, "Fluency": None, "Pronunciation": None}
    for k in results.keys():
        # patterns: "Content - 90", "Content: 90", "Content 90"
        m = re.search(rf"{k}\s*[-:]*\s*(\d{{1,3}})", text, flags=re.I)
        if m:
            try:
                val = int(m.group(1))
                results[k] = max(0, min(100, val))
            except:
                results[k] = None
        else:
            results[k] = None
    return results

def combine_scores(computed: Optional[int], llm: Optional[int]) -> Optional[int]:
    if llm is None and computed is None:
        return None
    if llm is None:
        return computed
    if computed is None:
        return llm
    return int(round((computed + llm) / 2))

@router.post("/read-aloud")
async def compare_audio(
    audio: UploadFile,
    referenceText: str = Form(...)
):
    if not referenceText:
        raise HTTPException(status_code=400, detail="Reference text is required")
    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is required")

    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(await read_audio_upload(audio))
            tmp_file_path = tmp_file.name

        transcription = _get_openai_client().audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_file_path, "rb")
        )
        transcribed_text = getattr(transcription, "text", None) or transcription.get("text") or ""

        ref_tokens = tokenize(referenceText)
        trans_tokens = tokenize(transcribed_text)
        token_report = build_token_analysis(ref_tokens, trans_tokens)
        analysis_prompt = f"""
        You are a strict PTE Speaking evaluator. Score the user's Read Aloud response.

        Evaluation criteria:
        - Content (0–90): Accuracy of words spoken compared to the reference text.
        - Oral Fluency (0–90): Smoothness, rhythm, pacing, and natural flow.
        - Pronunciation (0–90): Clarity, stress, phonemes, and intelligibility.

        Reference Text:
        "{referenceText}"

        Transcription:
        "{transcribed_text}"

        Token diff summary:
        {token_report["analysis"][:50]}

        Return STRICT JSON with the following structure.
        ALL fields are mandatory — do NOT leave any blank or omit any key:

        {{
            "scores": {{
                "Content": [0-90],
                "Fluency": [0-90],
                "Pronunciation": [0-90],
                "Overall": [0-90]
            }},
            "corrections": [
                "Highlight incorrect, missing, or changed words.",
                "Highlight unclear or mispronounced words.",
            ],
            "feedback":[
                "Give detailed but concise feedback to improve fluency & pronunciation.",
                "Provide word-specific pronunciation guidance.",
            ]
        }}

        Rules:
        - DO NOT rewrite the passage.
        - DO NOT add explanations.
        - Provide strict scoring like a PTE examiner.
        - Only output valid JSON. No additional text outside the JSON.
        """


        llm_resp = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0,
            max_tokens=400
        )

        llm_text = llm_resp.choices[0].message.content.strip()

        import json
        try:
            llm_json = json.loads(llm_text)
        except Exception:
            raise HTTPException(status_code=500, detail="LLM returned invalid JSON")

        result = {
            "transcribedText": transcribed_text,
            "referenceText": referenceText,
            "scores": llm_json.get("scores", {}),
            "corrections": llm_json.get("corrections", {}),
            "feedback": llm_json.get("feedback", {})
        }

        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Read Aloud comparison request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")
    finally:
        try:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        except Exception:
            pass

@router.post("/repeat-sentence")
async def compare_audio(
    audio: UploadFile,
    referenceText: str = Form(...)
):
    if not referenceText:
        raise HTTPException(status_code=400, detail="Reference text is required")
    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is required")

    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(await read_audio_upload(audio))
            tmp_file_path = tmp_file.name
        transcription = _get_openai_client().audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_file_path, "rb")
        )
        transcribed_text = getattr(transcription, "text", None) or transcription.get("text") or ""

        ref_tokens = tokenize(referenceText)
        trans_tokens = tokenize(transcribed_text)
        token_report = build_token_analysis(ref_tokens, trans_tokens)
        repeat_sentence_prompt = f"""
        You are a strict PTE “Repeat Sentence” grader. Compare an Original sentence to a User sentence and produce counts only.

        Rules
        • Compare words in order (case-insensitive; ignore punctuation).
        • Good = exact word match in form/meaning.
        • Average = small form variation (plural/singular, simple morphology).
        • Bad/Missed = wrong word, synonym, or omitted.
        • Extra user words count as Bad/Missed.
        • No percentages, no JSON, no explanations.
        • Output EXACTLY these four lines:

        Original: "{referenceText}"
        User: "{transcribed_text}"

        Total: {{X}} words
        Good: {{Y}} words
        Average: {{Z}} word(s)
        Bad/Missed: {{W}} word(s)
        """

        rs_resp = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": repeat_sentence_prompt}],
            temperature=0,
            max_tokens=100
        )

        repeat_sentence_result = rs_resp.choices[0].message.content.strip()

        scoring_prompt = f"""
        You are a strict PTE Speaking evaluator. Score the user's Repeat Sentence response.

        Reference Text:
        "{referenceText}"

        User Response:
        "{transcribed_text}"

        Return STRICT JSON only:
        {{
            "Content": [0-90],
            "Fluency": [0-90],
            "Pronunciation": [0-90],
            "Overall": [0-90]
        }}
        """

        score_resp = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0,
            max_tokens=100
        )

        import json
        try:
            score_json = json.loads(score_resp.choices[0].message.content.strip())
        except:
            raise HTTPException(status_code=500, detail="LLM returned invalid JSON for scoring")

        result = {
            "transcribedText": transcribed_text,
            "referenceText": referenceText,
            "singleLineFeedback": repeat_sentence_result,
            "scores": score_json
        }

        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Repeat Sentence comparison request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")
    finally:
        try:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
        except:
            pass
