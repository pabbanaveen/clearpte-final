import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import auth as firebase_auth

from app.core.auth import get_current_user, require_admin
from app.core.firebase import FirebaseConfigurationError
from app.main import app


class FirebaseAuthDependencyTests(unittest.TestCase):
    def setUp(self):
        self.credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="unit-test-token",
        )
        self.verified_claims = {
            "uid": "firebase-uid-1",
            "sub": "firebase-uid-1",
            "email": "learner@example.test",
            "email_verified": True,
        }

    @patch("app.core.auth.verify_firebase_id_token")
    def test_missing_bearer_token_is_rejected(self, verify_token):
        with self.assertRaises(HTTPException) as raised:
            get_current_user(None)

        self.assertEqual(raised.exception.status_code, 401)
        verify_token.assert_not_called()

    @patch("app.core.auth.verify_firebase_id_token")
    def test_verified_firebase_identity_is_returned(self, verify_token):
        verify_token.return_value = dict(self.verified_claims)

        identity = get_current_user(self.credentials)

        self.assertEqual(identity["uid"], "firebase-uid-1")
        self.assertEqual(identity["email"], "learner@example.test")

    @patch("app.core.auth.verify_firebase_id_token")
    def test_unverified_email_is_rejected(self, verify_token):
        verify_token.return_value = {**self.verified_claims, "email_verified": False}

        with self.assertRaises(HTTPException) as raised:
            get_current_user(self.credentials)

        self.assertEqual(raised.exception.status_code, 403)

    @patch("app.core.auth.verify_firebase_id_token")
    def test_invalid_firebase_token_is_rejected(self, verify_token):
        verify_token.side_effect = firebase_auth.InvalidIdTokenError("invalid")

        with self.assertRaises(HTTPException) as raised:
            get_current_user(self.credentials)

        self.assertEqual(raised.exception.status_code, 401)

    def test_admin_requires_server_issued_custom_claim(self):
        with self.assertRaises(HTTPException) as raised:
            require_admin({**self.verified_claims, "admin": False})

        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(
            require_admin({**self.verified_claims, "admin": True}),
            {**self.verified_claims, "admin": True},
        )

    @patch("app.core.auth.verify_firebase_id_token")
    def test_missing_firebase_configuration_is_service_unavailable(self, verify_token):
        verify_token.side_effect = FirebaseConfigurationError("missing project")

        with self.assertRaises(HTTPException) as raised:
            get_current_user(self.credentials)

        self.assertEqual(raised.exception.status_code, 503)


class ProtectedRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_api_sensitive_routes_reject_anonymous_requests(self):
        requests = [
            ("GET", "/api/auth/me", None),
            ("GET", "/api/questions/read-aloud", None),
            ("POST", "/api/evaluate/evaluate-essay", {}),
            ("POST", "/api/upload/upload-read-aloud-questions", []),
            ("GET", "/api/users/profile", None),
        ]

        for method, path, body in requests:
            with self.subTest(path=path):
                response = self.client.request(method, path, json=body)
                self.assertEqual(response.status_code, 401)

    @patch("app.core.auth.verify_firebase_id_token")
    def test_learner_cannot_upload_questions(self, verify_token):
        verify_token.return_value = {
            "uid": "firebase-uid-1",
            "email": "learner@example.test",
            "email_verified": True,
        }

        response = self.client.post(
            "/api/upload/upload-read-aloud-questions",
            headers={"Authorization": "Bearer unit-test-token"},
            json=[],
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
