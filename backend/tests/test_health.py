import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.database.deps import get_db
from app.main import app


class HealthCheckTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(get_db, None)

    def test_database_ready_returns_ok(self):
        fake_db = Mock()
        fake_db.execute.return_value.scalar.return_value = 1
        app.dependency_overrides[get_db] = lambda: fake_db

        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "db_connection": "ok"})

    def test_database_exception_returns_redacted_unhealthy_response(self):
        fake_db = Mock()
        fake_db.execute.side_effect = RuntimeError("secret-host db-password internal detail")
        app.dependency_overrides[get_db] = lambda: fake_db

        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Database unavailable"})
        self.assertNotIn("secret-host", response.text)
        self.assertNotIn("db-password", response.text)

    def test_failed_database_probe_returns_unhealthy_status(self):
        fake_db = Mock()
        fake_db.execute.return_value.scalar.return_value = 0
        app.dependency_overrides[get_db] = lambda: fake_db

        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Database readiness check failed"})


if __name__ == "__main__":
    unittest.main()
