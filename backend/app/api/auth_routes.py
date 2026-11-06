"""Routes for Firebase-authenticated application identities."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.deps import get_db
from app.services.identity_service import (
    IdentityEmailConflict,
    get_or_create_firebase_identity,
)

router = APIRouter()


@router.get("/me")
def get_current_identity(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Idempotently provision and return the verified Firebase identity."""
    try:
        identity = get_or_create_firebase_identity(db, user)
    except IdentityEmailConflict:
        raise HTTPException(
            status_code=409,
            detail="This email is already linked to a different account. Contact support.",
        )

    return {
        "id": identity.id,
        "uid": identity.firebase_uid,
        "email": identity.email,
        "full_name": identity.full_name,
        "email_verified": True,
        "role": "admin" if user.get("admin") is True else identity.role,
    }
