import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_current_user
from app.database.deps import get_db
from app.database.models import Base, FirebaseIdentity, PracticeAttempt, ReadAloudQuestion
from app.main import app
from app.services.read_aloud_scoring import ScoringUnavailableError


class ReadAloudPracticeApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        def override_get_db():
            session = self.session_factory()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        self.identity = {
            "uid": "firebase-uid-learner",
            "email": "learner@example.test",
            "email_verified": True,
        }
        app.dependency_overrides[get_current_user] = lambda: self.identity
        self.headers = {"Authorization": "Bearer mocked-live-at-api-boundary"}
        self.idempotency_headers = {
            **self.headers,
            "Idempotency-Key": "d8b71898-b14a-4f4a-9df5-c6849e525bd6",
        }
        with self.session_factory() as session:
            self.question = ReadAloudQuestion(
                title="Read Aloud test",
                text="A short practice passage for testing.",
                tags=["test", "speaking"],
            )
            session.add(self.question)
            session.commit()
            session.refresh(self.question)
            self.question_id = self.question.id

    def tearDown(self):
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)
        self.engine.dispose()

    @patch("app.api.practice_routes.score_read_aloud")
    def test_submit_scores_and_persists_attempt_without_audio_or_transcript(self, score):
        score.return_value = {
            "scores": {"Content": 75, "Fluency": 72, "Pronunciation": 77, "Overall": 75},
            "corrections": ["One word was unclear."],
            "feedback": ["Keep a steady pace."],
        }

        response = self.client.post(
            f"/api/practice/read-aloud/{self.question_id}/attempts",
            headers=self.idempotency_headers,
            files={"audio": ("answer.webm", b"fake audio bytes", "audio/webm")},
        )

        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(body["question_id"], self.question_id)
        self.assertEqual(body["scores"]["Overall"], 75)
        self.assertEqual(body["rubric_version"], "read-aloud-v1")
        self.assertNotIn("transcript", body)
        self.assertNotIn("audio", body)
        score.assert_called_once_with(
            b"fake audio bytes",
            "answer.webm",
            "A short practice passage for testing.",
        )

        with self.session_factory() as session:
            attempts = session.query(PracticeAttempt).all()
            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0].firebase_uid, "firebase-uid-learner")
            self.assertEqual(session.query(FirebaseIdentity).count(), 1)

    def test_attempt_history_is_scoped_to_verified_firebase_uid(self):
        with self.session_factory() as session:
            session.add(
                FirebaseIdentity(
                    firebase_uid="firebase-uid-learner",
                    email="learner@example.test",
                    role="student",
                )
            )
            session.add(
                FirebaseIdentity(
                    firebase_uid="firebase-uid-other",
                    email="other@example.test",
                    role="student",
                )
            )
            session.flush()
            session.add_all(
                [
                    PracticeAttempt(
                        firebase_uid="firebase-uid-learner",
                        idempotency_key="d8b71898-b14a-4f4a-9df5-c6849e525bd6",
                        task_type="read_aloud",
                        question_id=self.question_id,
                        scores={"Overall": 70},
                        corrections=[],
                        feedback=["Good practice."],
                        rubric_version="read-aloud-v1",
                        transcription_model="whisper-1",
                        scoring_model="gpt-4o-mini",
                    ),
                    PracticeAttempt(
                        firebase_uid="firebase-uid-other",
                        idempotency_key="e8b71898-b14a-4f4a-9df5-c6849e525bd6",
                        task_type="read_aloud",
                        question_id=self.question_id,
                        scores={"Overall": 85},
                        corrections=[],
                        feedback=["Another learner."],
                        rubric_version="read-aloud-v1",
                        transcription_model="whisper-1",
                        scoring_model="gpt-4o-mini",
                    ),
                ]
            )
            session.commit()

        response = self.client.get("/api/practice/attempts", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["scores"]["Overall"], 70)

    def test_unsupported_audio_is_rejected_before_provider_call(self):
        with patch("app.api.practice_routes.score_read_aloud") as score:
            response = self.client.post(
                f"/api/practice/read-aloud/{self.question_id}/attempts",
                headers=self.idempotency_headers,
                files={"audio": ("answer.txt", b"not audio", "text/plain")},
            )

        self.assertEqual(response.status_code, 415)
        score.assert_not_called()

    def test_provider_failure_returns_safe_error_and_does_not_save_attempt(self):
        with patch(
            "app.api.practice_routes.score_read_aloud",
            side_effect=ScoringUnavailableError("provider internal details"),
        ):
            response = self.client.post(
                f"/api/practice/read-aloud/{self.question_id}/attempts",
                headers=self.idempotency_headers,
                files={"audio": ("answer.webm", b"fake audio bytes", "audio/webm")},
            )

        self.assertEqual(response.status_code, 502)
        self.assertNotIn("provider internal details", response.text)
        with self.session_factory() as session:
            self.assertEqual(session.query(PracticeAttempt).count(), 0)

    def test_unknown_question_does_not_invoke_provider(self):
        with patch("app.api.practice_routes.score_read_aloud") as score:
            response = self.client.post(
                "/api/practice/read-aloud/999999/attempts",
                headers=self.idempotency_headers,
                files={"audio": ("answer.webm", b"fake audio bytes", "audio/webm")},
            )

        self.assertEqual(response.status_code, 404)
        score.assert_not_called()

    def test_attempt_history_rejects_invalid_pagination(self):
        response = self.client.get("/api/practice/attempts?limit=101", headers=self.headers)
        self.assertEqual(response.status_code, 422)

    def test_duplicate_submission_key_returns_previous_result_without_rescoring(self):
        scoring_result = {
            "scores": {"Content": 75, "Fluency": 72, "Pronunciation": 77, "Overall": 75},
            "corrections": ["One word was unclear."],
            "feedback": ["Keep a steady pace."],
        }
        with patch("app.api.practice_routes.score_read_aloud", return_value=scoring_result) as score:
            first = self.client.post(
                f"/api/practice/read-aloud/{self.question_id}/attempts",
                headers=self.idempotency_headers,
                files={"audio": ("answer.webm", b"audio one", "audio/webm")},
            )
            retry = self.client.post(
                f"/api/practice/read-aloud/{self.question_id}/attempts",
                headers=self.idempotency_headers,
                files={"audio": ("answer.webm", b"audio different", "audio/webm")},
            )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(retry.status_code, 201)
        self.assertEqual(first.json()["id"], retry.json()["id"])
        self.assertEqual(score.call_count, 1)

    def test_missing_or_invalid_idempotency_key_is_rejected(self):
        no_key = self.client.post(
            f"/api/practice/read-aloud/{self.question_id}/attempts",
            headers=self.headers,
            files={"audio": ("answer.webm", b"audio", "audio/webm")},
        )
        invalid_key = self.client.post(
            f"/api/practice/read-aloud/{self.question_id}/attempts",
            headers={**self.headers, "Idempotency-Key": "not-a-uuid"},
            files={"audio": ("answer.webm", b"audio", "audio/webm")},
        )
        self.assertEqual(no_key.status_code, 422)
        self.assertEqual(invalid_key.status_code, 400)


if __name__ == "__main__":
    unittest.main()
