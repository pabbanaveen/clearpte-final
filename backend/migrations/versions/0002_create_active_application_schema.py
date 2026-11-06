"""Create the active question/content SQLAlchemy schema.

Revision ID: 0002_application_schema
Revises: 0001_firebase_identities
This is the initial schema for newly provisioned databases. Legacy
password-account/profile tables and tables only mentioned in tables.sql are
intentionally not created in a new Firebase-first database.
"""
from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_application_schema"
down_revision: Union[str, None] = "0001_firebase_identities"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "answer_short_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.String(), nullable=False),
        sa.Column("acceptable_answers", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_answer_short_question_id", "answer_short_question", ["id"])

    op.create_table(
        "describe_image_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("image_type", sa.String(length=100), nullable=True),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.Column("speaking_time", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("sample_answer", sa.String(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_describe_image_question_id", "describe_image_question", ["id"])

    op.create_table(
        "highlight_correct_summary_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("summary_a", sa.String(), nullable=False),
        sa.Column("summary_b", sa.String(), nullable=False),
        sa.Column("summary_c", sa.String(), nullable=False),
        sa.Column("correct_summary", sa.String(length=1), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_highlight_correct_summary_template_id",
        "highlight_correct_summary_template",
        ["id"],
    )

    op.create_table(
        "highlight_incorrect_words_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("incorrect_words", sa.JSON(), nullable=True),
        sa.Column("correct_transcript", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_highlight_incorrect_words_template_id",
        "highlight_incorrect_words_template",
        ["id"],
    )

    op.create_table(
        "listening_fill_blanks_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("blank1_answer", sa.String(length=100), nullable=True),
        sa.Column("blank1_word", sa.String(length=100), nullable=True),
        sa.Column("blank2_answer", sa.String(length=100), nullable=True),
        sa.Column("blank2_word", sa.String(length=100), nullable=True),
        sa.Column("blank3_answer", sa.String(length=100), nullable=True),
        sa.Column("blank3_word", sa.String(length=100), nullable=True),
        sa.Column("extra_words", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_listening_fill_blanks_template_id",
        "listening_fill_blanks_template",
        ["id"],
    )

    op.create_table(
        "listening_multiple_choice_multiple_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("option_a", sa.String(), nullable=False),
        sa.Column("option_b", sa.String(), nullable=False),
        sa.Column("option_c", sa.String(), nullable=False),
        sa.Column("option_d", sa.String(), nullable=False),
        sa.Column("option_e", sa.String(), nullable=True),
        sa.Column("correct_answers", sa.JSON(), nullable=True),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_listening_multiple_choice_multiple_template_id",
        "listening_multiple_choice_multiple_template",
        ["id"],
    )

    op.create_table(
        "listening_multiple_choice_single_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("option_a", sa.String(), nullable=False),
        sa.Column("option_b", sa.String(), nullable=False),
        sa.Column("option_c", sa.String(), nullable=False),
        sa.Column("option_d", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_listening_multiple_choice_single_template_id",
        "listening_multiple_choice_single_template",
        ["id"],
    )

    op.create_table(
        "multiple_choice_multiple_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("passage", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("option_a", sa.String(), nullable=False),
        sa.Column("option_b", sa.String(), nullable=False),
        sa.Column("option_c", sa.String(), nullable=False),
        sa.Column("option_d", sa.String(), nullable=False),
        sa.Column("option_e", sa.String(), nullable=True),
        sa.Column("correct_answers", sa.JSON(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_multiple_choice_multiple_template_id",
        "multiple_choice_multiple_template",
        ["id"],
    )

    op.create_table(
        "multiple_choice_single_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("passage", sa.String(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("option_a", sa.String(), nullable=False),
        sa.Column("option_b", sa.String(), nullable=False),
        sa.Column("option_c", sa.String(), nullable=False),
        sa.Column("option_d", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_multiple_choice_single_template_id",
        "multiple_choice_single_template",
        ["id"],
    )

    op.create_table(
        "read_aloud_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.Column("recording_time", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("expected_answer", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_read_aloud_question_id", "read_aloud_question", ["id"])

    op.create_table(
        "practice_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("firebase_uid", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=36), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("scores", sa.JSON(), nullable=False),
        sa.Column("corrections", sa.JSON(), nullable=False),
        sa.Column("feedback", sa.JSON(), nullable=False),
        sa.Column("rubric_version", sa.String(length=64), nullable=False),
        sa.Column("transcription_model", sa.String(length=64), nullable=False),
        sa.Column("scoring_model", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["firebase_uid"],
            ["firebase_identities.firebase_uid"],
            name="fk_practice_attempts_firebase_uid",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["read_aloud_question.id"],
            name="fk_practice_attempts_question_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_practice_attempts"),
        sa.UniqueConstraint(
            "firebase_uid",
            "idempotency_key",
            name="uq_practice_attempts_uid_idempotency_key",
        ),
    )
    op.create_index("ix_practice_attempts_id", "practice_attempts", ["id"])
    op.create_index("ix_practice_attempts_firebase_uid", "practice_attempts", ["firebase_uid"])
    op.create_index("ix_practice_attempts_question_id", "practice_attempts", ["question_id"])

    op.create_table(
        "reading_fill_blanks_rw_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("passage", sa.String(), nullable=False),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("blank1_answer", sa.String(length=100), nullable=True),
        sa.Column("blank1_options", sa.JSON(), nullable=True),
        sa.Column("blank2_answer", sa.String(length=100), nullable=True),
        sa.Column("blank2_options", sa.JSON(), nullable=True),
        sa.Column("blank3_answer", sa.String(length=100), nullable=True),
        sa.Column("blank3_options", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reading_fill_blanks_rw_template_id",
        "reading_fill_blanks_rw_template",
        ["id"],
    )

    op.create_table(
        "reading_fill_blanks_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("blank1_answer", sa.String(length=100), nullable=True),
        sa.Column("blank1_options", sa.JSON(), nullable=True),
        sa.Column("blank2_answer", sa.String(length=100), nullable=True),
        sa.Column("blank2_options", sa.JSON(), nullable=True),
        sa.Column("blank3_answer", sa.String(length=100), nullable=True),
        sa.Column("blank3_options", sa.JSON(), nullable=True),
        sa.Column("blank4_answer", sa.String(length=100), nullable=True),
        sa.Column("blank4_options", sa.JSON(), nullable=True),
        sa.Column("blank5_answer", sa.String(length=100), nullable=True),
        sa.Column("blank5_options", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reading_fill_blanks_template_id",
        "reading_fill_blanks_template",
        ["id"],
    )

    op.create_table(
        "reorder_paragraphs_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("paragraph1", sa.String(), nullable=False),
        sa.Column("paragraph2", sa.String(), nullable=False),
        sa.Column("paragraph3", sa.String(), nullable=False),
        sa.Column("paragraph4", sa.String(), nullable=False),
        sa.Column("paragraph5", sa.String(), nullable=True),
        sa.Column("correct_order", sa.JSON(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_reorder_paragraphs_template_id",
        "reorder_paragraphs_template",
        ["id"],
    )

    op.create_table(
        "repeat_sentence_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("sentence", sa.String(), nullable=False),
        sa.Column("recording_time", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_repeat_sentence_question_id",
        "repeat_sentence_question",
        ["id"],
    )

    op.create_table(
        "retell_lecture_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("subject", sa.String(length=100), nullable=True),
        sa.Column("preparation_time", sa.Integer(), nullable=True),
        sa.Column("speaking_time", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_retell_lecture_question_id",
        "retell_lecture_question",
        ["id"],
    )

    op.create_table(
        "select_missing_word_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("missing_word_position", sa.Integer(), nullable=False),
        sa.Column("option_a", sa.String(), nullable=False),
        sa.Column("option_b", sa.String(), nullable=False),
        sa.Column("option_c", sa.String(), nullable=False),
        sa.Column("option_d", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.String(length=1), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_select_missing_word_template_id",
        "select_missing_word_template",
        ["id"],
    )

    op.create_table(
        "summarize_spoken_text_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("transcript", sa.String(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("word_limit", sa.Integer(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("sample_summary", sa.String(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_summarize_spoken_text_template_id",
        "summarize_spoken_text_template",
        ["id"],
    )

    op.create_table(
        "summarize_text_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("passage", sa.String(), nullable=False),
        sa.Column("word_limit", sa.Integer(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("sample_summary", sa.String(), nullable=True),
        sa.Column("key_ideas", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_summarize_text_question_id",
        "summarize_text_question",
        ["id"],
    )

    op.create_table(
        "write_essay_question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("essay_type", sa.String(length=100), nullable=True),
        sa.Column("word_limit", sa.Integer(), nullable=True),
        sa.Column("time_limit", sa.Integer(), nullable=True),
        sa.Column("rubric_content", sa.String(), nullable=True),
        sa.Column("rubric_form", sa.String(), nullable=True),
        sa.Column("rubric_grammar", sa.String(), nullable=True),
        sa.Column("rubric_vocabulary", sa.String(), nullable=True),
        sa.Column("sample_essay", sa.String(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_write_essay_question_id", "write_essay_question", ["id"])

    op.create_table(
        "write_from_dictation_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audio_url", sa.String(), nullable=False),
        sa.Column("sentence", sa.String(), nullable=False),
        sa.Column("play_count", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=50), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("key_words", sa.JSON(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_write_from_dictation_template_id",
        "write_from_dictation_template",
        ["id"],
    )


def downgrade() -> None:
    op.drop_index("ix_write_from_dictation_template_id", table_name="write_from_dictation_template")
    op.drop_table("write_from_dictation_template")
    op.drop_index("ix_write_essay_question_id", table_name="write_essay_question")
    op.drop_table("write_essay_question")
    op.drop_index("ix_summarize_text_question_id", table_name="summarize_text_question")
    op.drop_table("summarize_text_question")
    op.drop_index("ix_summarize_spoken_text_template_id", table_name="summarize_spoken_text_template")
    op.drop_table("summarize_spoken_text_template")
    op.drop_index("ix_select_missing_word_template_id", table_name="select_missing_word_template")
    op.drop_table("select_missing_word_template")
    op.drop_index("ix_retell_lecture_question_id", table_name="retell_lecture_question")
    op.drop_table("retell_lecture_question")
    op.drop_index("ix_repeat_sentence_question_id", table_name="repeat_sentence_question")
    op.drop_table("repeat_sentence_question")
    op.drop_index("ix_reorder_paragraphs_template_id", table_name="reorder_paragraphs_template")
    op.drop_table("reorder_paragraphs_template")
    op.drop_index("ix_reading_fill_blanks_template_id", table_name="reading_fill_blanks_template")
    op.drop_table("reading_fill_blanks_template")
    op.drop_index("ix_reading_fill_blanks_rw_template_id", table_name="reading_fill_blanks_rw_template")
    op.drop_table("reading_fill_blanks_rw_template")
    op.drop_index("ix_practice_attempts_question_id", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_firebase_uid", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_id", table_name="practice_attempts")
    op.drop_table("practice_attempts")
    op.drop_index("ix_read_aloud_question_id", table_name="read_aloud_question")
    op.drop_table("read_aloud_question")
    op.drop_index("ix_multiple_choice_single_template_id", table_name="multiple_choice_single_template")
    op.drop_table("multiple_choice_single_template")
    op.drop_index("ix_multiple_choice_multiple_template_id", table_name="multiple_choice_multiple_template")
    op.drop_table("multiple_choice_multiple_template")
    op.drop_index("ix_listening_multiple_choice_single_template_id", table_name="listening_multiple_choice_single_template")
    op.drop_table("listening_multiple_choice_single_template")
    op.drop_index("ix_listening_multiple_choice_multiple_template_id", table_name="listening_multiple_choice_multiple_template")
    op.drop_table("listening_multiple_choice_multiple_template")
    op.drop_index("ix_listening_fill_blanks_template_id", table_name="listening_fill_blanks_template")
    op.drop_table("listening_fill_blanks_template")
    op.drop_index("ix_highlight_incorrect_words_template_id", table_name="highlight_incorrect_words_template")
    op.drop_table("highlight_incorrect_words_template")
    op.drop_index("ix_highlight_correct_summary_template_id", table_name="highlight_correct_summary_template")
    op.drop_table("highlight_correct_summary_template")
    op.drop_index("ix_describe_image_question_id", table_name="describe_image_question")
    op.drop_table("describe_image_question")
    op.drop_index("ix_answer_short_question_id", table_name="answer_short_question")
    op.drop_table("answer_short_question")
