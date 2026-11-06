"""Allow-listed learner-facing question response payloads.

Answer keys, transcripts used as scoring references, sample solutions, and
rubrics stay server-side. Add new question models here explicitly; unknown
model classes fail closed rather than returning ORM fields by default.
"""

from typing import Any

from sqlalchemy import inspect


PUBLIC_QUESTION_FIELDS: dict[str, tuple[str, ...]] = {
    "ReadAloudQuestion": (
        "id", "title", "text", "preparation_time", "recording_time",
        "difficulty", "category", "tags",
    ),
    "RepeatSentenceQuestion": (
        "id", "audio_url", "recording_time", "difficulty", "category",
        "tags", "title",
    ),
    "DescribeImageQuestion": (
        "id", "image_url", "image_type", "preparation_time", "speaking_time",
        "difficulty", "category", "title", "description",
    ),
    "RetellLectureQuestion": (
        "id", "audio_url", "duration", "subject", "preparation_time",
        "speaking_time", "difficulty", "category", "title",
    ),
    "AnswerShortQuestion": (
        "id", "audio_url", "question", "difficulty", "category", "tags", "title",
    ),
    "SummarizeTextQuestion": (
        "id", "passage", "word_limit", "time_limit", "difficulty", "category", "title",
    ),
    "WriteEssayQuestion": (
        "id", "prompt", "essay_type", "word_limit", "time_limit",
        "difficulty", "category", "title",
    ),
    "ReadingFillBlanksTemplate": (
        "id", "title", "text", "blank1_options", "blank2_options",
        "blank3_options", "blank4_options", "blank5_options", "difficulty", "category",
    ),
    "ReadingFillBlanksRWTemplate": (
        "id", "title", "passage", "time_limit", "blank1_options",
        "blank2_options", "blank3_options", "difficulty", "category",
    ),
    "MultipleChoiceMultipleTemplate": (
        "id", "passage", "question", "option_a", "option_b", "option_c",
        "option_d", "option_e", "time_limit", "difficulty", "category", "title",
    ),
    "MultipleChoiceSingleTemplate": (
        "id", "passage", "question", "option_a", "option_b", "option_c",
        "option_d", "time_limit", "difficulty", "category", "title",
    ),
    "ReorderParagraphsTemplate": (
        "id", "title", "paragraph1", "paragraph2", "paragraph3", "paragraph4",
        "paragraph5", "time_limit", "difficulty", "category",
    ),
    "SummarizeSpokenTextTemplate": (
        "id", "audio_url", "duration", "word_limit", "time_limit",
        "difficulty", "category", "title",
    ),
    "ListeningMultipleChoiceMultipleTemplate": (
        "id", "audio_url", "question", "option_a", "option_b", "option_c",
        "option_d", "option_e", "difficulty", "category", "title",
    ),
    "ListeningMultipleChoiceSingleTemplate": (
        "id", "audio_url", "question", "option_a", "option_b", "option_c",
        "option_d", "difficulty", "category", "title",
    ),
    "ListeningFillBlanksTemplate": (
        "id", "title", "audio_url", "duration", "blank1_word", "blank2_word",
        "blank3_word", "extra_words", "difficulty", "category",
    ),
    "HighlightCorrectSummaryTemplate": (
        "id", "audio_url", "summary_a", "summary_b", "summary_c",
        "difficulty", "category", "title",
    ),
    "SelectMissingWordTemplate": (
        "id", "audio_url", "missing_word_position", "option_a", "option_b",
        "option_c", "option_d", "difficulty", "category", "title",
    ),
    "HighlightIncorrectWordsTemplate": (
        "id", "transcript", "difficulty", "category", "title",
    ),
    "WriteFromDictationTemplate": (
        "id", "audio_url", "play_count", "difficulty", "category", "title",
    ),
}


def serialize_question(question: Any) -> dict[str, Any]:
    """Return only explicitly approved learner-visible fields for a question."""
    model_name = type(question).__name__
    public_fields = PUBLIC_QUESTION_FIELDS.get(model_name)
    if public_fields is None:
        raise ValueError(f"No learner response schema registered for {model_name}")

    mapped_columns = {column.key for column in inspect(type(question)).columns}
    if not set(public_fields).issubset(mapped_columns):
        raise ValueError(f"Learner response schema is out of sync for {model_name}")

    return {field: getattr(question, field) for field in public_fields}


def serialize_questions(questions: list[Any]) -> list[dict[str, Any]]:
    """Serialize a collection using the same fail-closed allow-list."""
    return [serialize_question(question) for question in questions]
