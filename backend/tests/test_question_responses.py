import unittest

from app.database.models import (
    AnswerShortQuestion,
    DescribeImageQuestion,
    HighlightCorrectSummaryTemplate,
    HighlightIncorrectWordsTemplate,
    ListeningFillBlanksTemplate,
    ListeningMultipleChoiceMultipleTemplate,
    ListeningMultipleChoiceSingleTemplate,
    MultipleChoiceMultipleTemplate,
    MultipleChoiceSingleTemplate,
    ReadAloudQuestion,
    ReadingFillBlanksRWTemplate,
    ReadingFillBlanksTemplate,
    ReorderParagraphsTemplate,
    RepeatSentenceQuestion,
    RetellLectureQuestion,
    SelectMissingWordTemplate,
    SummarizeSpokenTextTemplate,
    SummarizeTextQuestion,
    WriteEssayQuestion,
    WriteFromDictationTemplate,
)
from app.services.question_responses import PUBLIC_QUESTION_FIELDS, serialize_question


QUESTION_MODELS = (
    ReadAloudQuestion,
    RepeatSentenceQuestion,
    DescribeImageQuestion,
    RetellLectureQuestion,
    AnswerShortQuestion,
    SummarizeTextQuestion,
    WriteEssayQuestion,
    ReadingFillBlanksTemplate,
    ReadingFillBlanksRWTemplate,
    MultipleChoiceMultipleTemplate,
    MultipleChoiceSingleTemplate,
    ReorderParagraphsTemplate,
    SummarizeSpokenTextTemplate,
    ListeningMultipleChoiceMultipleTemplate,
    ListeningMultipleChoiceSingleTemplate,
    ListeningFillBlanksTemplate,
    HighlightCorrectSummaryTemplate,
    SelectMissingWordTemplate,
    HighlightIncorrectWordsTemplate,
    WriteFromDictationTemplate,
)


class LearnerQuestionResponseTests(unittest.TestCase):
    def test_every_registered_question_model_has_an_explicit_allowlist(self):
        self.assertEqual(
            {model.__name__ for model in QUESTION_MODELS},
            set(PUBLIC_QUESTION_FIELDS),
        )

    def test_allowlists_exclude_known_answer_keys_rubrics_and_reference_text(self):
        hidden_fields = {
            "expected_answer", "sentence", "key_points", "sample_answer",
            "correct_answer", "acceptable_answers", "sample_summary", "key_ideas",
            "rubric_content", "rubric_form", "rubric_grammar", "rubric_vocabulary",
            "sample_essay", "blank1_answer", "blank2_answer", "blank3_answer",
            "blank4_answer", "blank5_answer", "correct_answers", "correct_order",
            "correct_summary", "incorrect_words", "correct_transcript", "key_words",
        }

        for model in QUESTION_MODELS:
            with self.subTest(model=model.__name__):
                question = model()
                payload = serialize_question(question)
                self.assertEqual(set(payload), set(PUBLIC_QUESTION_FIELDS[model.__name__]))
                self.assertFalse(hidden_fields.intersection(payload))

    def test_unknown_model_fails_closed(self):
        class UnregisteredQuestion:
            id = 1
            answer_key = "not for clients"

        with self.assertRaises(ValueError):
            serialize_question(UnregisteredQuestion())

    def test_schema_drift_fails_closed(self):
        class MissingColumnQuestion(ReadAloudQuestion):
            pass

        question = MissingColumnQuestion()
        original_fields = PUBLIC_QUESTION_FIELDS["MissingColumnQuestion"] if "MissingColumnQuestion" in PUBLIC_QUESTION_FIELDS else None
        self.assertIsNone(original_fields)
        with self.assertRaises(ValueError):
            serialize_question(question)


if __name__ == "__main__":
    unittest.main()
