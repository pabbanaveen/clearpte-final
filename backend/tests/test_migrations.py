import os
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.database.models import ReadAloudQuestion


BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_CONFIG = BACKEND_ROOT / "alembic.ini"


class FirebaseIdentityMigrationTests(unittest.TestCase):
    def test_identity_migration_upgrade_and_downgrade(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "migration.sqlite"
            previous_database_url = os.environ.get("DATABASE_URL")
            os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
            try:
                config = Config(str(ALEMBIC_CONFIG))
                command.upgrade(config, "head")
                command.check(config)

                engine = create_engine(os.environ["DATABASE_URL"])
                inspector = inspect(engine)
                tables = set(inspector.get_table_names())
                expected_tables = {
                    "firebase_identities",
                    "practice_attempts",
                    "practice_attempts",
                    "read_aloud_question", "repeat_sentence_question",
                    "describe_image_question", "retell_lecture_question",
                    "answer_short_question", "summarize_text_question",
                    "write_essay_question", "reading_fill_blanks_template",
                    "reading_fill_blanks_rw_template", "multiple_choice_multiple_template",
                    "multiple_choice_single_template", "reorder_paragraphs_template",
                    "summarize_spoken_text_template", "listening_multiple_choice_multiple_template",
                    "listening_multiple_choice_single_template", "listening_fill_blanks_template",
                    "highlight_correct_summary_template", "select_missing_word_template",
                    "highlight_incorrect_words_template", "write_from_dictation_template",
                }
                self.assertTrue(expected_tables.issubset(tables))
                self.assertNotIn("users", tables)
                self.assertNotIn("user_profile", tables)
                self.assertEqual(
                    {column["name"] for column in inspector.get_columns("firebase_identities")},
                    {
                        "id", "firebase_uid", "email", "full_name", "role",
                        "target_score", "test_date", "created_at", "updated_at",
                    },
                )
                attempt_columns = {
                    column["name"] for column in inspector.get_columns("practice_attempts")
                }
                self.assertIn("idempotency_key", attempt_columns)
                self.assertIn("firebase_uid", attempt_columns)
                self.assertIn("question_id", attempt_columns)
                unique_columns = {
                    column
                    for constraint in inspector.get_unique_constraints("firebase_identities")
                    for column in constraint["column_names"]
                }
                self.assertTrue({"firebase_uid", "email"}.issubset(unique_columns))

                with Session(engine) as session:
                    session.add(ReadAloudQuestion(text="Migration test", tags=["array", "json"]))
                    session.commit()
                    session.expunge_all()
                    stored_question = session.query(ReadAloudQuestion).one()
                    self.assertEqual(stored_question.tags, ["array", "json"])
                engine.dispose()

                command.downgrade(config, "base")
                engine = create_engine(os.environ["DATABASE_URL"])
                self.assertNotIn("firebase_identities", inspect(engine).get_table_names())
                engine.dispose()
            finally:
                if previous_database_url is None:
                    os.environ.pop("DATABASE_URL", None)
                else:
                    os.environ["DATABASE_URL"] = previous_database_url


if __name__ == "__main__":
    unittest.main()
