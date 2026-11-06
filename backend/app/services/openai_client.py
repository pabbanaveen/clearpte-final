import openai
from app.schemas import EvaluationScore
import base64
import os
from dotenv import load_dotenv


load_dotenv()

_api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=_api_key, timeout=60, max_retries=1) if _api_key else None


def _get_openai_client():
    if openai_client is None:
        raise RuntimeError("Set OPENAI_API_KEY to use AI evaluation features.")
    return openai_client


def similarity_score(a: str, b: str) -> float:
    a_words = a.lower().split()
    b_words = b.lower().split()
    intersection = [word for word in a_words if word in b_words]
    return (len(intersection) / max(len(a_words), len(b_words))) * 100


def evaluate_against_text(reference_text: str, user_text: str, max_scores: dict) -> EvaluationScore:
    content_score = similarity_score(reference_text, user_text)
    
    prompt = f"""
    Evaluate the following spoken response against the reference text.
    Give scores only (0 to {max_scores['fluency']} and {max_scores['pronunciation']}):
    
    Reference: "{reference_text}"
    Spoken: "{user_text}"

    Respond in JSON:
    {{
      "fluency": <score>,
      "pronunciation": <score>
    }}
    """

    response = _get_openai_client().chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        parsed = eval(response.choices[0].message.content)
    except Exception:
        parsed = {"fluency": 0, "pronunciation": 0}

    return EvaluationScore(
        content=min(content_score, max_scores['content']),
        fluency=min(parsed.get("fluency", 0), max_scores['fluency']),
        pronunciation=min(parsed.get("pronunciation", 0), max_scores['pronunciation']),
    )


def evaluate_against_image(image_path: str, user_text: str, max_scores: dict) -> EvaluationScore:
    with open(image_path, "rb") as img_file:
        base64_img = base64.b64encode(img_file.read()).decode("utf-8")

    prompt = f"""
    Evaluate the user's spoken description against the image.
    Assign scores (0 to {max_scores['content']}, {max_scores['fluency']}, {max_scores['pronunciation']})

    Spoken: "{user_text}"

    Respond in JSON:
    {{
      "content": <score>,
      "fluency": <score>,
      "pronunciation": <score>
    }}
    """

    response = _get_openai_client().chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                ]
            }
        ],
        max_tokens=300
    )

    try:
        parsed = eval(response.choices[0].message.content)
    except Exception:
        parsed = {"content": 0, "fluency": 0, "pronunciation": 0}

    return EvaluationScore(
        content=min(parsed.get("content", 0), max_scores['content']),
        fluency=min(parsed.get("fluency", 0), max_scores['fluency']),
        pronunciation=min(parsed.get("pronunciation", 0), max_scores['pronunciation']),
    )



# import os
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(OPENAI_API_KEY)
# # assert OPENAI_API_KEY, "Set OPENAI_API_KEY in environment"



# HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}


# # Transcribe audio file (path) using OpenAI's audio transcription endpoint (whisper)
# def transcribe_audio(file_path: str) -> str:
#   url = "https://api.openai.com/v1/audio/transcriptions"
#   with open(file_path, "rb") as f:
#     files = {"file": f}
#     data = {"model": "whisper-1"}
#     resp = requests.post(url, headers=HEADERS, files=files, data=data, timeout=120)
#     resp.raise_for_status()
#     return resp.json().get("text", "")


# # Get embedding for a piece of text using OpenAI embeddings API
# def get_text_embedding(text: str) -> list:
#   url = "https://api.openai.com/v1/embeddings"
#   payload = {"model": "text-embedding-3-small", "input": text}
#   resp = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=30)
#   resp.raise_for_status()
#   data = resp.json()
#   return data["data"][0]["embedding"]