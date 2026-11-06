import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app


class LegacyEvaluationSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {
            "uid": "verified-test-user",
            "email": "learner@example.test",
            "email_verified": True,
        }

    def tearDown(self):
        app.dependency_overrides.pop(get_current_user, None)

    @patch(
        "app.api.evaluation_routes._get_openai_client",
        side_effect=RuntimeError("private provider configuration details"),
    )
    def test_text_evaluation_does_not_expose_provider_error(self, get_client):
        response = self.client.post(
            "/api/evaluate/evaluate-summary",
            data={
                "original_text": "Climate research studies several changing ecosystems and long-term patterns.",
                "student_summary": "Scientists compare environmental data to understand effects over many years.",
            },
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Evaluation service is temporarily unavailable"})
        self.assertNotIn("private provider configuration details", response.text)
        get_client.assert_called_once()

    @patch(
        "app.api.openai_routes._get_openai_client",
        side_effect=RuntimeError("private audio provider credentials"),
    )
    def test_audio_evaluation_does_not_expose_provider_error(self, get_client):
        response = self.client.post(
            "/api/compare/read-aloud",
            data={"referenceText": "A short reference sentence for a test."},
            files={"audio": ("answer.webm", b"small test payload", "audio/webm")},
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"detail": "Evaluation service is temporarily unavailable"})
        self.assertNotIn("private audio provider credentials", response.text)
        get_client.assert_called_once()


if __name__ == "__main__":
    unittest.main()
