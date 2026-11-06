"""Bounded validation helpers for uploaded learner audio."""

from fastapi import HTTPException, UploadFile

MAX_AUDIO_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_AUDIO_CONTENT_TYPES = {
    "audio/webm",
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/aac",
}


async def read_audio_upload(audio: UploadFile) -> bytes:
    """Read an audio file up to the limit, rejecting unsupported/empty payloads."""
    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported audio type")

    content = await audio.read(MAX_AUDIO_UPLOAD_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    if len(content) > MAX_AUDIO_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 10 MB limit")
    return content
