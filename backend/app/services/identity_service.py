"""Provision and retrieve application identities for verified Firebase users."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import FirebaseIdentity


class IdentityEmailConflict(Exception):
    """A verified provider email is already attached to another Firebase UID."""


def get_or_create_firebase_identity(
    db: Session,
    claims: dict,
) -> FirebaseIdentity:
    """Idempotently map a verified Firebase subject to an application profile.

    Role is only initialized server-side. Provider/client-supplied role values
    are deliberately ignored; admin elevation uses trusted custom claims.
    """
    firebase_uid = claims["uid"]
    email = claims["email"].strip().lower()
    full_name = claims.get("name")

    identity = (
        db.query(FirebaseIdentity)
        .filter(FirebaseIdentity.firebase_uid == firebase_uid)
        .one_or_none()
    )
    if identity is None:
        email_owner = (
            db.query(FirebaseIdentity)
            .filter(FirebaseIdentity.email == email)
            .one_or_none()
        )
        if email_owner is not None and email_owner.firebase_uid != firebase_uid:
            raise IdentityEmailConflict

        identity = FirebaseIdentity(
            firebase_uid=firebase_uid,
            email=email,
            full_name=full_name,
            role="student",
        )
        db.add(identity)
    else:
        email_owner = (
            db.query(FirebaseIdentity)
            .filter(
                FirebaseIdentity.email == email,
                FirebaseIdentity.firebase_uid != firebase_uid,
            )
            .one_or_none()
        )
        if email_owner is not None:
            raise IdentityEmailConflict
        identity.email = email
        if full_name:
            identity.full_name = full_name
        # Never overwrite server role from a Firebase client claim/body.

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # A concurrent request may have provisioned this UID. Reload only if
        # it maps to the same email; otherwise fail closed.
        identity = (
            db.query(FirebaseIdentity)
            .filter(FirebaseIdentity.firebase_uid == firebase_uid)
            .one_or_none()
        )
        if identity is not None and identity.email == email:
            return identity
        raise IdentityEmailConflict from exc

    db.refresh(identity)
    return identity
