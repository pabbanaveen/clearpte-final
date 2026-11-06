from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.deps import get_db

from app.database.models import (
  HighlightCorrectSummaryTemplate, HighlightIncorrectWordsTemplate, ListeningFillBlanksTemplate, ListeningMultipleChoiceMultipleTemplate, ListeningMultipleChoiceSingleTemplate, MultipleChoiceMultipleTemplate, MultipleChoiceSingleTemplate, ReadAloudQuestion, ReadingFillBlanksRWTemplate, ReadingFillBlanksTemplate, ReorderParagraphsTemplate, RepeatSentenceQuestion, DescribeImageQuestion,
  RetellLectureQuestion, AnswerShortQuestion, SelectMissingWordTemplate, SummarizeSpokenTextTemplate, SummarizeTextQuestion, WriteEssayQuestion, WriteFromDictationTemplate
)

from app.services.question_responses import serialize_question, serialize_questions

router = APIRouter()

@router.get("/read-aloud", response_model=None)
def get_read_aloud_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ReadAloudQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/read-aloud/{question_id}", response_model=None)
def get_read_aloud_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ReadAloudQuestion).filter(ReadAloudQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/repeat-sentence", response_model=None)
def get_repeat_sentence_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(RepeatSentenceQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/repeat-sentence/{question_id}", response_model=None)
def get_repeat_sentence_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(RepeatSentenceQuestion).filter(RepeatSentenceQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/describe-image", response_model=None)
def get_describe_image_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(DescribeImageQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/describe-image/{question_id}", response_model=None)
def get_describe_image_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(DescribeImageQuestion).filter(DescribeImageQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/retell-lecture", response_model=None)
def get_retell_lecture_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(RetellLectureQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/retell-lecture/{question_id}", response_model=None)
def get_retell_lecture_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(RetellLectureQuestion).filter(RetellLectureQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/answer-short", response_model=None)
def get_answer_short_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(AnswerShortQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/answer-short/{question_id}", response_model=None)
def get_answer_short_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(AnswerShortQuestion).filter(AnswerShortQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/summarize-text", response_model=None)
def get_summarize_text_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(SummarizeTextQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/summarize-text/{question_id}", response_model=None)
def get_summarize_text_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(SummarizeTextQuestion).filter(SummarizeTextQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/writing-essay", response_model=None)
def get_writing_essay_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(WriteEssayQuestion).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/writing-essay/{question_id}", response_model=None)
def get_writing_essay_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(WriteEssayQuestion).filter(WriteEssayQuestion.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)


@router.get("/reading-fill-blanks", response_model=None)
def get_reading_fill_blanks_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ReadingFillBlanksTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/reading-fill-blanks/{question_id}", response_model=None)
def get_reading_fill_blanks_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ReadingFillBlanksTemplate).filter(ReadingFillBlanksTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/reading-fill-blanks-rw", response_model=None)
def get_reading_fill_blanks_rw_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ReadingFillBlanksRWTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/reading-fill-blanks-rw/{question_id}", response_model=None)
def get_reading_fill_blanks_rw_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ReadingFillBlanksRWTemplate).filter(ReadingFillBlanksRWTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/multiple-choice-multiple", response_model=None)
def get_multiple_choice_multiple_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(MultipleChoiceMultipleTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/multiple-choice-multiple/{question_id}", response_model=None)
def get_multiple_choice_multiple_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(MultipleChoiceMultipleTemplate).filter(MultipleChoiceMultipleTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/multiple-choice-single", response_model=None)
def get_multiple_choice_single_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(MultipleChoiceSingleTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/multiple-choice-single/{question_id}", response_model=None)
def get_multiple_choice_single_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(MultipleChoiceSingleTemplate).filter(MultipleChoiceSingleTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/reorder-paragraphs", response_model=None)
def get_reorder_paragraphs_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ReorderParagraphsTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/reorder-paragraphs/{question_id}", response_model=None)
def get_reorder_paragraphs_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ReorderParagraphsTemplate).filter(ReorderParagraphsTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/summarize-spoken-text", response_model=None)
def get_summarize_spoken_text_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(SummarizeSpokenTextTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/summarize-spoken-text/{question_id}", response_model=None)
def get_summarize_spoken_text_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(SummarizeSpokenTextTemplate).filter(SummarizeSpokenTextTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/listening-multiple-choice-multiple", response_model=None)
def get_listening_multiple_choice_multiple_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ListeningMultipleChoiceMultipleTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/listening-multiple-choice-multiple/{question_id}", response_model=None)
def get_listening_multiple_choice_multiple_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ListeningMultipleChoiceMultipleTemplate).filter(ListeningMultipleChoiceMultipleTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/listening-multiple-choice-single", response_model=None)
def get_listening_multiple_choice_single_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ListeningMultipleChoiceSingleTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/listening-multiple-choice-single/{question_id}", response_model=None)
def get_listening_multiple_choice_single_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ListeningMultipleChoiceSingleTemplate).filter(ListeningMultipleChoiceSingleTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/listening-fill-blanks", response_model=None)
def get_listening_fill_blanks_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(ListeningFillBlanksTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/listening-fill-blanks/{question_id}", response_model=None)
def get_listening_fill_blanks_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(ListeningFillBlanksTemplate).filter(ListeningFillBlanksTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/highlight-correct-summary", response_model=None)
def get_highlight_correct_summary_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(HighlightCorrectSummaryTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/highlight-correct-summary/{question_id}", response_model=None)
def get_highlight_correct_summary_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(HighlightCorrectSummaryTemplate).filter(HighlightCorrectSummaryTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/select-missing-word", response_model=None)
def get_select_missing_word_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(SelectMissingWordTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/select-missing-word/{question_id}", response_model=None)
def get_select_missing_word_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(SelectMissingWordTemplate).filter(SelectMissingWordTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/highlight-incorrect-words", response_model=None)
def get_highlight_incorrect_words_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(HighlightIncorrectWordsTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/highlight-incorrect-words/{question_id}", response_model=None)
def get_highlight_incorrect_words_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(HighlightIncorrectWordsTemplate).filter(HighlightIncorrectWordsTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)

@router.get("/write-from-dictation", response_model=None)
def get_write_from_dictation_questions(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db)
):
  questions = db.query(WriteFromDictationTemplate).offset(skip).limit(limit).all()
  return serialize_questions(questions)

@router.get("/write-from-dictation/{question_id}", response_model=None)
def get_write_from_dictation_question(question_id: int, db: Session = Depends(get_db)):
  question = db.query(WriteFromDictationTemplate).filter(WriteFromDictationTemplate.id == question_id).first()
  if not question:
    raise HTTPException(status_code=404, detail="Question not found")
  return serialize_question(question)
