import unittest
from unittest.mock import Mock

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile as StarletteUploadFile
from starlette.responses import Response

from app.core.auth import require_admin
from app.core.uploads import MAX_AUDIO_UPLOAD_BYTES, read_audio_upload
from app.database.deps import get_db
from app.main import app


class AudioUploadValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_supported_audio_within_limit_is_read(self):
        audio = StarletteUploadFile(
            filename="response.webm",
            file=__import__("io").BytesIO(b"audio"),
            headers={"content-type": "audio/webm"},
        )

        self.assertEqual(await read_audio_upload(audio), b"audio")

    async def test_unsupported_content_type_is_rejected(self):
        audio = StarletteUploadFile(
            filename="response.txt",
            file=__import__("io").BytesIO(b"text"),
            headers={"content-type": "text/plain"},
        )

        with self.assertRaises(HTTPException) as raised:
            await read_audio_upload(audio)
        self.assertEqual(raised.exception.status_code, 415)

    async def test_audio_over_limit_is_rejected(self):
        audio = StarletteUploadFile(
            filename="response.webm",
            file=__import__("io").BytesIO(b"x" * (MAX_AUDIO_UPLOAD_BYTES + 1)),
            headers={"content-type": "audio/webm"},
        )

        with self.assertRaises(HTTPException) as raised:
            await read_audio_upload(audio)
        self.assertEqual(raised.exception.status_code, 413)


class QuestionImportErrorTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[require_admin] = lambda: {"uid": "admin-test", "admin": True}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(require_admin, None)
        app.dependency_overrides.pop(get_db, None)

    def test_validation_http_error_is_preserved(self):
        response = self.client.post(
            "/api/upload/upload-read-aloud-questions",
            json=[{"title": "missing required values"}],
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Each question must contain fields", response.json()["detail"])

    def test_database_exception_is_redacted(self):
        db = Mock()
        db.bulk_save_objects.side_effect = RuntimeError("private-host:5432 password=secret")

        def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        response = self.client.post(
            "/api/upload/upload-read-aloud-questions",
            json=[{
                "title": "Test",
                "text": "A test sentence",
                "difficulty": "easy",
                "category": "test",
            }],
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Question import failed"})
        self.assertNotIn("private-host", response.text)
        self.assertNotIn("secret", response.text)


if __name__ == "__main__":
    unittest.main()
