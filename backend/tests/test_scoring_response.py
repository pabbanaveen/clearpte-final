import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.schemas import EvaluationScore
from app.services.openai_client import (
    ScoringResponseError,
    _parse_score_json,
    evaluate_against_image,
    evaluate_against_text,
)
from app.services.read_aloud_scoring import ScoringUnavailableError, score_read_aloud


class ScoringResponseValidationTests(unittest.TestCase):
    def test_strict_json_scores_are_parsed(self):
        scores = _parse_score_json(
            '{"content": 80, "fluency": 70.5, "pronunciation": 72}',
            {"content", "fluency", "pronunciation"},
        )
        self.assertEqual(scores["content"], 80.0)
        self.assertEqual(scores["fluency"], 70.5)

    def test_python_expression_is_rejected_without_execution(self):
        with self.assertRaises(ScoringResponseError):
            _parse_score_json(
                "__import__('pathlib').Path('should-not-exist').touch()",
                {"content"},
            )

    def test_missing_extra_boolean_and_out_of_range_scores_are_rejected(self):
        invalid_payloads = (
            ('{"content": 5}', {"content", "fluency"}),
            ('{"content": 5, "unexpected": 6}', {"content"}),
            ('{"content": true}', {"content"}),
            ('{"content": 91}', {"content"}),
            ('{"content": NaN}', {"content"}),
        )
        for payload, required_fields in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ScoringResponseError):
                    _parse_score_json(payload, required_fields)

    @patch("app.services.openai_client._get_openai_client")
    def test_text_evaluation_uses_json_and_returns_bounded_scores(self, get_client):
        message = SimpleNamespace(content='{"fluency": 70, "pronunciation": 75}')
        response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kwargs: response)
            )
        )
        get_client.return_value = client

        result = evaluate_against_text(
            "the quick brown fox", "the quick fox", {"content": 90, "fluency": 90, "pronunciation": 90}
        )

        self.assertIsInstance(result, EvaluationScore)
        self.assertEqual(result.fluency, 70)
        self.assertEqual(result.pronunciation, 75)

    @patch("builtins.open")
    @patch("app.services.openai_client._get_openai_client")
    def test_image_evaluation_rejects_non_json_model_response(self, get_client, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = b"test-image"
        message = SimpleNamespace(content="{'content': 1, 'fluency': 2, 'pronunciation': 3}")
        response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kwargs: response)
            )
        )
        get_client.return_value = client

        with self.assertRaises(ScoringResponseError):
            evaluate_against_image(
                "local.png",
                "A description",
                {"content": 90, "fluency": 90, "pronunciation": 90},
            )

    @patch("app.services.read_aloud_scoring._get_openai_client", side_effect=RuntimeError("missing key"))
    def test_read_aloud_missing_provider_configuration_is_normalized(self, get_client):
        with self.assertRaises(ScoringUnavailableError):
            score_read_aloud(b"fake audio", "answer.webm", "reference")


if __name__ == "__main__":
    unittest.main()
