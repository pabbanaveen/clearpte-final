"""Authenticated persisted practice and scoring endpoints."""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.deps import get_db
from app.database.models import PracticeAttempt, ReadAloudQuestion
from app.services.identity_service import (
    IdentityEmailConflict,
    get_or_create_firebase_identity,
)
from app.services.question_responses import serialize_question
from app.services.read_aloud_scoring import (
    READ_ALOUD_RUBRIC_VERSION,
    SCORING_MODEL,
    TRANSCRIPTION_MODEL,
    ScoringUnavailableError,
    score_read_aloud,
)

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_READ_ALOUD_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {
    "audio/webm", "audio/wav", "audio/x-wav", "audio/mpeg",
    "audio/mp4", "audio/ogg", "audio/aac",
}


class PracticeAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_type: str
    question_id: int
    scores: dict[str, Any]
    corrections: list[str]
    feedback: list[str]
    rubric_version: str
    transcription_model: str
    scoring_model: str
    created_at: datetime


@router.get("/read-aloud/{question_id}")
def get_read_aloud_prompt(
    question_id: int,
    db: Session = Depends(get_db),
    identity: dict = Depends(get_current_user),
) -> dict:
    del identity  # Route-level auth ensures prompt access is limited to verified learners.
    question = db.query(ReadAloudQuestion).filter(ReadAloudQuestion.id == question_id).one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return serialize_question(question)


@router.post(
    "/read-aloud/{question_id}/attempts",
    response_model=PracticeAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_read_aloud_attempt(
    question_id: int,
    audio: UploadFile = File(...),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    identity: dict = Depends(get_current_user),
) -> PracticeAttempt:
    try:
        get_or_create_firebase_identity(db, identity)
    except IdentityEmailConflict:
        raise HTTPException(
            status_code=409,
            detail="This email is already linked to a different account. Contact support.",
        )

    try:
        normalized_idempotency_key = str(UUID(idempotency_key))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Idempotency-Key must be a UUID")

    previous_attempt = (
        db.query(PracticeAttempt)
        .filter(
            PracticeAttempt.firebase_uid == identity["uid"],
            PracticeAttempt.idempotency_key == normalized_idempotency_key,
        )
        .one_or_none()
    )
    if previous_attempt is not None:
        await audio.close()
        if previous_attempt.question_id != question_id:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used")
        return previous_attempt

    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio type")

    question = db.query(ReadAloudQuestion).filter(ReadAloudQuestion.id == question_id).one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    audio_bytes = await audio.read(MAX_READ_ALOUD_AUDIO_BYTES + 1)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    if len(audio_bytes) > MAX_READ_ALOUD_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 10 MB limit")

    try:
        result = score_read_aloud(audio_bytes, audio.filename or "answer.webm", question.text)
    except ScoringUnavailableError:
        logger.warning("Read Aloud scoring provider failed for question_id=%s", question_id)
        raise HTTPException(
            status_code=502,
            detail="Scoring is temporarily unavailable. Please try again later.",
        )
    finally:
        await audio.close()

    attempt = PracticeAttempt(
        firebase_uid=identity["uid"],
        idempotency_key=normalized_idempotency_key,
        task_type="read_aloud",
        question_id=question.id,
        scores=result["scores"],
        corrections=result["corrections"],
        feedback=result["feedback"],
        rubric_version=READ_ALOUD_RUBRIC_VERSION,
        transcription_model=TRANSCRIPTION_MODEL,
        scoring_model=SCORING_MODEL,
    )
    try:
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    except Exception:
        db.rollback()
        logger.exception("Read Aloud attempt persistence failed for question_id=%s", question_id)
        raise HTTPException(
            status_code=503,
            detail="The result could not be saved. Please try again later.",
        )
    return attempt


@router.get("/attempts", response_model=list[PracticeAttemptResponse])
def list_my_practice_attempts(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    identity: dict = Depends(get_current_user),
) -> list[PracticeAttempt]:
    if limit < 1 or limit > 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")
    return (
        db.query(PracticeAttempt)
        .filter(PracticeAttempt.firebase_uid == identity["uid"])
        .order_by(PracticeAttempt.created_at.desc(), PracticeAttempt.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
