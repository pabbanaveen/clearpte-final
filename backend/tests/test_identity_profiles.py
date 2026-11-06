import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_current_user
from app.database.deps import get_db
from app.database.models import Base, FirebaseIdentity
from app.main import app


class FirebaseIdentityProfileApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        def override_get_db():
            db = self.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.claims = {
            "uid": "firebase-uid-1",
            "email": "learner@example.test",
            "email_verified": True,
            "name": "Test Learner",
            # This must never control the application role.
            "role": "admin",
        }
        self.token_patch = patch("app.core.auth.verify_firebase_id_token", return_value=self.claims)
        self.token_patch.start()
        self.headers = {"Authorization": "Bearer test-token"}

    def tearDown(self):
        self.token_patch.stop()
        app.dependency_overrides.pop(get_db, None)
        self.engine.dispose()

    def test_auth_me_creates_a_server_controlled_identity(self):
        response = self.client.get("/api/auth/me", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["uid"], "firebase-uid-1")
        self.assertEqual(body["email"], "learner@example.test")
        self.assertEqual(body["role"], "student")
        self.assertTrue(body["email_verified"])

        with self.session_factory() as db:
            self.assertEqual(db.query(FirebaseIdentity).count(), 1)

    def test_profile_is_created_and_updated_for_verified_uid(self):
        update = self.client.put(
            "/api/users/profile",
            headers=self.headers,
            json={"target_score": 79, "test_date": "2027-04-15"},
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()["target_score"], 79)
        self.assertEqual(update.json()["test_date"], "2027-04-15")

        profile = self.client.get("/api/users/profile", headers=self.headers)
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["uid"], "firebase-uid-1")
        self.assertEqual(profile.json()["target_score"], 79)

    def test_profile_rejects_out_of_range_target_score(self):
        response = self.client.put(
            "/api/users/profile",
            headers=self.headers,
            json={"target_score": 100},
        )
        self.assertEqual(response.status_code, 422)

    def test_different_uid_cannot_claim_an_existing_verified_email(self):
        with self.session_factory() as db:
            db.add(
                FirebaseIdentity(
                    firebase_uid="other-uid",
                    email="learner@example.test",
                    role="student",
                )
            )
            db.commit()

        response = self.client.get("/api/auth/me", headers=self.headers)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(FirebaseIdentity.__tablename__, "firebase_identities")

    def test_client_cannot_choose_another_users_profile_by_path_id(self):
        response = self.client.get("/api/users/profile/123", headers=self.headers)
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
