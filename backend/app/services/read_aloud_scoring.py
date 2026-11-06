"""Bounded, typed Read Aloud evaluation through the server-side OpenAI client."""

import json
from io import BytesIO
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.openai_client import _get_openai_client

READ_ALOUD_RUBRIC_VERSION = "read-aloud-v1"
TRANSCRIPTION_MODEL = "whisper-1"
SCORING_MODEL = "gpt-4o-mini"


class ReadAloudScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: int = Field(ge=0, le=90, alias="Content")
    fluency: int = Field(ge=0, le=90, alias="Fluency")
    pronunciation: int = Field(ge=0, le=90, alias="Pronunciation")
    overall: int = Field(ge=0, le=90, alias="Overall")


class ReadAloudEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: ReadAloudScores
    corrections: list[str] = Field(min_length=1, max_length=20)
    feedback: list[str] = Field(min_length=1, max_length=20)


class ScoringUnavailableError(Exception):
    """The configured scoring provider failed or returned invalid data."""


def score_read_aloud(audio_bytes: bytes, filename: str, reference_text: str) -> dict[str, Any]:
    """Transcribe and score audio; callers should never persist audio or transcript by default."""
    client = _get_openai_client()
    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    try:
        transcription = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
        )
        transcript = getattr(transcription, "text", None)
        if not isinstance(transcript, str) or not transcript.strip():
            raise ScoringUnavailableError("Transcription provider returned no usable text.")

        scoring_prompt = f"""
Evaluate this PTE Read Aloud practice response. This is practice feedback, not an official PTE score.
Score content, oral fluency, and pronunciation from 0 to 90. Return only a JSON object matching:
{{"scores": {{"Content": 0, "Fluency": 0, "Pronunciation": 0, "Overall": 0}},
  "corrections": ["..."], "feedback": ["..."]}}
Do not include the full reference passage in feedback.

Reference passage:\n{reference_text[:5000]}

Transcription:\n{transcript[:5000]}
"""
        completion = client.chat.completions.create(
            model=SCORING_MODEL,
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0,
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        if not content:
            raise ScoringUnavailableError("Scoring provider returned an empty response.")
        parsed = json.loads(content)
        evaluation = ReadAloudEvaluation.model_validate(parsed)
        return evaluation.model_dump(by_alias=True)
    except ScoringUnavailableError:
        raise
    except (ValidationError, json.JSONDecodeError, IndexError, AttributeError, KeyError) as exc:
        raise ScoringUnavailableError("Scoring provider returned an invalid response.") from exc
    except Exception as exc:
        raise ScoringUnavailableError("Scoring provider is unavailable.") from exc
    finally:
        audio_file.close()
