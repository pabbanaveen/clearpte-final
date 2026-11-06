"""Create Firebase identity and profile table.

Revision ID: 0001_firebase_identities
Revises: None
"""
from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_firebase_identities"
down_revision: Union[str, None] = None
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "firebase_identities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("firebase_uid", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), server_default="student", nullable=False),
        sa.Column("target_score", sa.Integer(), nullable=True),
        sa.Column("test_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_firebase_identities"),
        sa.UniqueConstraint("firebase_uid", name="uq_firebase_identities_firebase_uid"),
        sa.UniqueConstraint("email", name="uq_firebase_identities_email"),
    )
    op.create_index(
        "ix_firebase_identities_id",
        "firebase_identities",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_firebase_identities_id", table_name="firebase_identities")
    op.drop_table("firebase_identities")
