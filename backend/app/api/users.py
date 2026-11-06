
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database.deps import get_db
from app.database.models import FirebaseIdentity
from app.schemas import ProfileUpdate
from app.services.identity_service import (
    IdentityEmailConflict,
    get_or_create_firebase_identity,
)

router = APIRouter()

def _current_identity(db: Session, claims: dict) -> FirebaseIdentity:
    try:
        return get_or_create_firebase_identity(db, claims)
    except IdentityEmailConflict:
        raise HTTPException(
            status_code=409,
            detail="This email is already linked to a different account. Contact support.",
        )


@router.get("/profile")
def get_my_profile(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user),
) -> dict:
    identity = _current_identity(db, claims)
    return {
        "uid": identity.firebase_uid,
        "email": identity.email,
        "full_name": identity.full_name,
        "role": "admin" if claims.get("admin") is True else identity.role,
        "target_score": identity.target_score,
        "test_date": identity.test_date,
    }


@router.put("/profile")
def update_my_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user),
) -> dict:
    identity = _current_identity(db, claims)
    for field, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(identity, field, value)

    db.commit()
    db.refresh(identity)
    return {
        "uid": identity.firebase_uid,
        "email": identity.email,
        "full_name": identity.full_name,
        "role": "admin" if claims.get("admin") is True else identity.role,
        "target_score": identity.target_score,
        "test_date": identity.test_date,
    }
