import logging
import os
import re
import tempfile
from difflib import SequenceMatcher

from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from app.schemas import EvaluationResult, MaxScores
from fastapi.responses import JSONResponse
from app.services.openai_client import (
    _get_openai_client,
    evaluate_against_text,
    evaluate_against_image
)
import json
from app.core.uploads import read_audio_upload

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/evaluate-short-answer")
async def evaluate_answer(
    audio: UploadFile,
    question: str = Form(...)
):
    """
    Evaluate whether the spoken response (audio) correctly answers a given question.
    """
    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is required")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(await read_audio_upload(audio))
            tmp_file_path = tmp_file.name

        transcription = _get_openai_client().audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_file_path, "rb")
        )
        user_answer = transcription.text.strip()

        evaluation_prompt = f"""
        You are an intelligent evaluator. Analyze whether the user's spoken response correctly answers the question.

        ### Question:
        "{question}"

        ### Transcribed Answer:
        "{user_answer}"

        Evaluate the answer on:
        - **Relevance (0–100)**: Does the answer address the question meaningfully?
        - **Accuracy (0–100)**: Is the answer factually and logically correct?
        - **Completeness (0–100)**: Does it cover key points expected in a good answer?

        Respond ONLY in the following JSON format:

        {{
            "scores": {{
                "Relevance": <0–100>,
                "Accuracy": <0–100>,
                "Completeness": <0–100>
            }},
            "is_answer_correct": true/false,
            "feedback": "<brief feedback>",
            "improvements": [
                "<suggestion 1>",
                "<suggestion 2>",
                "<suggestion 3>"
            ],
            "overallSummary": "<short summary>"
        }}
        """

        # STEP 3: Ask GPT to evaluate
        gpt_response = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise and fair evaluator for spoken answers."},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )

        llm_json = json.loads(gpt_response.choices[0].message.content)

        result = {
            "question": question,
            "transcribed_answer": user_answer,
            "evaluation": llm_json,
            "scores": {
                "final": {
                    "Relevance": llm_json["scores"].get("Relevance"),
                    "Accuracy": llm_json["scores"].get("Accuracy"),
                    "Completeness": llm_json["scores"].get("Completeness"),
                }
            },
            "is_answer_correct": llm_json.get("is_answer_correct", False),
            "feedback": llm_json.get("feedback", ""),
            "improvements": llm_json.get("improvements", []),
            "overallSummary": llm_json.get("overallSummary", "")
        }
        os.remove(tmp_file_path)
        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Short-answer evaluation request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception:
                pass

@router.post("/evaluate-from-image")
async def evaluate_from_image(
    audio: UploadFile = File(...),
    image_url: str = Form(...),
    referenceDescription: str = Form(...)
):
    tmp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as audio_tmp:
            audio_tmp.write(await read_audio_upload(audio))
            tmp_audio_path = audio_tmp.name

        transcription = _get_openai_client().audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_audio_path, "rb")
        )
        user_speech = getattr(transcription, "text", None) or transcription.get("text") or ""

        image_analysis_prompt = """
You are an expert visual analyst. Analyze this image and summarize its visual meaning and key elements in 2-3 sentences.
Focus on what it shows and its general context.
"""
        image_analysis_resp = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": image_analysis_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                }
            ],
            temperature=0
        )
        image_summary = image_analysis_resp.choices[0].message.content.strip()

        evaluation_prompt = f"""
        You are a PTE Describe Image evaluator.

        Do NOT provide a model answer. The user has already spoken.
        Your job is to evaluate their spoken description in a friendly, lenient, and supportive manner.

        You are given:
        - The analyzed image context: "{image_summary}"
        - The correct description: "{referenceDescription}"
        - The student's spoken description (transcribed): "{user_speech}"

        Evaluate how well the student described the image compared to the important elements in the image and the reference description.

        Scoring rules (lenient):
        - Content /90 (be generous; reward effort and partial information)
        - Fluency /90 (focus on smoothness; do not judge minor pauses)
        - Pronunciation /90 (be kind; only reduce score for major clarity issues)
        - Scores should generally lean higher unless the response is extremely short.
        - Higher marks for effort
        - Encourage improvement
        - Do not judge harsh mistakes
        - Only give short correction suggestions (2–3 points)
        - Tell me 1 sentence on how to improve next time


        Provide supportive feedback:
        - Highlight strengths.
        - Give 2–3 short, simple improvement suggestions.
        - Add one friendly “next time” tip.

        Return STRICT JSON with:
        {{
        "scores": {{
            "Content": [0-90],
            "Fluency": [0-90],
            "Pronunciation": [0-90]
        }},
        "feedback": [
            "positive comment 1",
            "positive comment 2"
        ],
        "improvements": [
            "improvement tip 1",
            "improvement tip 2",
            "next-time friendly guidance"
        ]
        }}

        Rules:
        - Be friendly, encouraging, and positive.
        - Do NOT rewrite the description.
        - Do NOT add explanations.
        - Only output valid JSON and nothing else.
        """


        llm_resp = _get_openai_client().chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": evaluation_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                }
            ],
            temperature=0,
            max_tokens=500
        )

        llm_text = llm_resp.choices[0].message.content.strip()

        try:
            clean_json = re.sub(r"^```(?:json)?", "", llm_text, flags=re.IGNORECASE | re.MULTILINE)
            clean_json = re.sub(r"```$", "", clean_json, flags=re.MULTILINE).strip()
            llm_json = json.loads(clean_json)
        except json.JSONDecodeError:
            llm_json = {
                "scores": {"Content": None, "Fluency": None, "Pronunciation": None},
                "feedback": [],
                "improvements": []
            }

        result = {
            "transcribed_text": user_speech,
            "referenceDescription": referenceDescription,
            "image_summary": image_summary,
            "evaluation": llm_json,
            "scores": {
                "Content": llm_json["scores"].get("Content"),
                "Fluency": llm_json["scores"].get("Fluency"),
                "Pronunciation": llm_json["scores"].get("Pronunciation"),
            },
            "feedback": llm_json.get("feedback", []),
            "corrections": llm_json.get("improvements", [])
        }

        return JSONResponse(result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Describe-image evaluation request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")

    finally:
        if tmp_audio_path and os.path.exists(tmp_audio_path):
            try:
                os.remove(tmp_audio_path)
            except Exception:
                pass

@router.post("/evaluate-retell")
async def evaluate_retell(
    audio: UploadFile = File(...),
    referenceDescription: str = Form(...)
):

    if not audio:
        raise HTTPException(status_code=400, detail="Audio file is required")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
            tmp_file.write(await read_audio_upload(audio))
            tmp_file_path = tmp_file.name

        transcription = _get_openai_client().audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_file_path, "rb")
        )
        user_speech = transcription.text.strip()

        evaluation_prompt = f"""
        You are a PTE Speaking evaluator.  
        Use an easy-mode, supportive, gentle scoring style.

        ### Lecture Summary:
        "{referenceDescription}"

        ### Student's Retelling (Transcribed):
        "{user_speech}"

        Evaluate ONLY:
        • Content (main idea + key points) — score out of 90  
        • Pronunciation (clarity, stress, intonation) — score out of 90  
        • Fluency (flow, pace, hesitation control) — score out of 90  

        Be positive. Do NOT penalize heavily for grammar.  
        Keep feedback simple, friendly, and encouraging.

        Respond ONLY in the JSON structure below:

        {{
            "scores": {{
                "Content": <0–90>,
                "Fluency": <0–90>,
                "Pronunciation": <0–90>
            }},
            "feedback": {
                "Content": "<friendly feedback>",
                "Fluency": "<friendly feedback>",
                "Pronunciation": "<friendly feedback>"
            },
            "improvements": [
                "<simple suggestion 1>",
                "<simple suggestion 2>",
                "<simple suggestion 3>"
            ],
            "overallSummary": "<brief, positive summary>"
        }}

        Rules:
        • Keep tone soft, supportive, and motivating  
        • Suggestions must be light and easy  
        • No negative or harsh language  
        • Focus on encouragement and clarity  
        """

        gpt_response = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fair and constructive English speech examiner."},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )

        llm_json = json.loads(gpt_response.choices[0].message.content)

        result = {
            "transcribed_text": user_speech,
            "referenceDescription": referenceDescription,
            "evaluation": llm_json,
            "scores": {
                "final": {
                    "Content": llm_json["scores"].get("Content"),
                    "Fluency": llm_json["scores"].get("Fluency"),
                    "Pronunciation": llm_json["scores"].get("Pronunciation")
                }
            },
            "feedback": llm_json.get("feedback", {}),
            "improvements": llm_json.get("improvements", [])
        }
        os.remove(tmp_file_path)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception:
        logger.error("Retell evaluation request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")
    
@router.post("/evaluate-summary")
async def evaluate_summary(
    original_text: str = Form(...),
    student_summary: str = Form(...)
):
    """
    Evaluate student's text summary for content and fluency.
    Ensures that the student's summary does not just copy or reorder words
    from the original text.
    """

    if not original_text or not student_summary:
        raise HTTPException(status_code=400, detail="Both original_text and student_summary are required.")

    try:
        # STEP 1 — Preprocess text
        def normalize_text(text):
            text = text.lower()
            text = re.sub(r"[^a-z0-9\s]", "", text)
            return text.strip()

        orig_norm = normalize_text(original_text)
        summ_norm = normalize_text(student_summary)

        # STEP 2 — Check word-order similarity
        seq_ratio = SequenceMatcher(None, orig_norm, summ_norm).ratio()

        if seq_ratio > 0.7:
            return JSONResponse(content={
                "error": "The student's summary is too similar to the original text.",
                "similarity_score": seq_ratio,
                "message": "Please rephrase the content in your own words instead of copying or reordering phrases."
            })

        # STEP 3 — Build evaluation prompt
        evaluation_prompt = f"""
        You are an expert English writing evaluator.
        Evaluate the student's summary against the original text.

        ### Original Text:
        "{original_text}"

        ### Student's Summary:
        "{student_summary}"

        Important rule:
        - Do NOT reward summaries that copy sentences or maintain the same word order as the original.
        - Reward paraphrasing, summarization skill, and clarity in the student's own words.

        Evaluate on these criteria:
        1. **Content (0–100)** – Accuracy, relevance, and coverage of key ideas.
        2. **Fluency (0–100)** – Grammar, clarity, sentence flow, and coherence.

        Provide JSON in the following exact format:

        {{
            "scores": {{
                "Content": <0–100>,
                "Fluency": <0–100>
            }},
            "feedback": {{
                "Content": "<feedback>",
                "Fluency": "<feedback>"
            }},
            "improvements": [
                "<suggestion 1>",
                "<suggestion 2>",
                "<suggestion 3>"
            ],
            "overallSummary": "<brief overall evaluation>"
        }}
        """

        # STEP 4 — Get GPT evaluation
        gpt_response = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fair and constructive English writing evaluator."},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )

        llm_json = json.loads(gpt_response.choices[0].message.content)

        # STEP 5 — Construct final structured response
        result = {
            "original_text": original_text,
            "student_summary": student_summary,
            "similarity_score": round(seq_ratio, 3),
            "evaluation": llm_json,
            "scores": {
                "final": {
                    "Content": llm_json["scores"].get("Content"),
                    "Fluency": llm_json["scores"].get("Fluency")
                }
            },
            "feedback": llm_json.get("feedback", {}),
            "improvements": llm_json.get("improvements", []),
            "overallSummary": llm_json.get("overallSummary", "")
        }

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Summary evaluation request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")
    
@router.post("/evaluate-essay")
async def evaluate_essay(
    question: str = Form(...),
    student_essay: str = Form(...)
):
    """
    Evaluate a student's essay for a given question prompt.
    Returns structured JSON scores for relevance, coherence, grammar, and creativity.
    """

    if not question or not student_essay:
        raise HTTPException(status_code=400, detail="Both question and student_essay are required.")

    try:
        # STEP 1 — Normalize text to detect copying or word-order matching
        def normalize(text: str) -> str:
            text = text.lower()
            text = re.sub(r"[^a-z0-9\s]", "", text)
            return text.strip()

        question_norm = normalize(question)
        essay_norm = normalize(student_essay)

        similarity_ratio = SequenceMatcher(None, question_norm, essay_norm).ratio()

        # STEP 2 — Penalize if essay copies from the question itself
        if similarity_ratio > 0.7:
            return JSONResponse(
                content={
                    "error": "Essay appears to be too similar to the question prompt.",
                    "similarity_score": similarity_ratio,
                    "message": "Write an original essay in your own words."
                },
                status_code=400
            )

        # STEP 3 — Build GPT evaluation prompt
        evaluation_prompt = f"""
        You are an expert English writing examiner. 
        Evaluate the student's essay based on the given question.

        ### Question:
        "{question}"

        ### Student's Essay:
        "{student_essay}"

        You must evaluate on the following criteria (each scored 0–100):

        1. **Relevance** – How well the essay addresses the question.
        2. **Coherence** – Logical flow, structure, and clarity of ideas.
        3. **Grammar** – Grammar, punctuation, and sentence construction.
        4. **Creativity** – Originality, tone, and engagement.

        Do not reward essays that merely copy or restate the question.

        Provide JSON in the following format exactly:

        {{
            "scores": {{
                "Relevance": <0–100>,
                "Coherence": <0–100>,
                "Grammar": <0–100>,
                "Creativity": <0–100>
            }},
            "feedback": {{
                "Relevance": "<feedback>",
                "Coherence": "<feedback>",
                "Grammar": "<feedback>",
                "Creativity": "<feedback>"
            }},
            "improvements": [
                "<suggestion 1>",
                "<suggestion 2>",
                "<suggestion 3>"
            ],
            "overallSummary": "<brief overall evaluation>"
        }}
        """

        # STEP 4 — Query OpenAI model
        gpt_response = _get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fair and constructive essay evaluator."},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )

        llm_json = json.loads(gpt_response.choices[0].message.content)

        # STEP 5 — Calculate final score (weighted average)
        scores = llm_json["scores"]
        final_score = round(
            (scores["Relevance"] * 0.35) +
            (scores["Coherence"] * 0.25) +
            (scores["Grammar"] * 0.2) +
            (scores["Creativity"] * 0.2)
        )

        # STEP 6 — Construct structured result
        result = {
            "question": question,
            "student_essay": student_essay,
            "similarity_score": round(similarity_ratio, 3),
            "evaluation": llm_json,
            "scores": {
                "final": final_score,
                "details": scores
            },
            "feedback": llm_json.get("feedback", {}),
            "improvements": llm_json.get("improvements", []),
            "overallSummary": llm_json.get("overallSummary", "")
        }

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception:
        logger.error("Essay evaluation request failed")
        raise HTTPException(status_code=502, detail="Evaluation service is temporarily unavailable")