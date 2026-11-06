from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.models import AnswerShortQuestion, DescribeImageQuestion, HighlightCorrectSummaryTemplate, HighlightIncorrectWordsTemplate, ListeningFillBlanksTemplate, ListeningMultipleChoiceMultipleTemplate, ListeningMultipleChoiceSingleTemplate, MultipleChoiceMultipleTemplate, MultipleChoiceSingleTemplate, ReadAloudQuestion, ReadingFillBlanksRWTemplate, ReadingFillBlanksTemplate, ReorderParagraphsTemplate, RetellLectureQuestion, SelectMissingWordTemplate, SummarizeSpokenTextTemplate, SummarizeTextQuestion, WriteEssayQuestion, WriteFromDictationTemplate
from app.database.models import RepeatSentenceQuestion
from app.database.deps import get_db
from typing import List
import io
import datetime
import json
import re

router = APIRouter()

@router.post("/upload-read-aloud-questions")
async def upload_read_aloud_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    # Expected fields in each question
    required_fields = ['title', 'text',
             'difficulty', 'category']
    
    # Validate all questions have required fields
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ReadAloudQuestion objects
    questions = []
    for data in questions_data:
      question = ReadAloudQuestion(
        title=str(data['title']).replace("'", "''").strip(),
        text=str(data['text']).replace("'", "''").strip(),
        preparation_time=data.get('preparationTime', 30),
        recording_time=data.get('recordingTime', 40),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        tags=parse_array(data.get('tags')),
        expected_answer=str(data.get('expectedAnswer', '')).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} read aloud questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
@router.post("/upload-repeat-sentence-questions")
async def upload_repeat_sentence_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    # Expected fields in each question
    required_fields = ['audioUrl', 'sentence', 'recordingTime', 
             'difficulty', 'category', 'tags', 'title']
    
    # Validate all questions have required fields
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to RepeatSentenceQuestion objects
    questions = []
    for data in questions_data:
      question = RepeatSentenceQuestion(
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        sentence=str(data['sentence']).replace("'", "''").strip(),
        recording_time=data.get('recordingTime', 40),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        tags=parse_array(data.get('tags')),
        title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} repeat sentence questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-describe-image-questions")
async def upload_describe_image_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    # Expected fields in each question
    required_fields = ['imageUrl', 'imageType', 'preparationTime', 'speakingTime', 
             'difficulty', 'category', 'keyPoints', 'sampleAnswer', 'title']
    
    # Validate all questions have required fields
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to DescribeImageQuestion objects
    questions = []
    for data in questions_data:
      question = DescribeImageQuestion(
        image_url=str(data['imageUrl']).replace("'", "''").strip(),
        image_type=str(data['imageType']).replace("'", "''").strip(),
        preparation_time=data.get('preparationTime', 25),
        speaking_time=data.get('speakingTime', 40),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        key_points=parse_array(data.get('keyPoints')),
        sample_answer=str(data['sampleAnswer']).replace("'", "''").strip(),
        title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} describe image questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
@router.post("/upload-retell-lecture-questions")
async def upload_retell_lecture_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    # Expected fields in each question
    required_fields = ['audioUrl', 'transcript', 'duration', 'keyPoints', 
             'subject', 'preparationTime', 'speakingTime', 
             'difficulty', 'category', 'title']
    
    # Validate all questions have required fields
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to RetellLectureQuestion objects
    questions = []
    for data in questions_data:
      question = RetellLectureQuestion(
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        duration=data.get('duration'),
        key_points=parse_array(data.get('keyPoints')),
        subject=str(data['subject']).replace("'", "''").strip(),
        preparation_time=data.get('preparationTime', 10),
        speaking_time=data.get('speakingTime', 40),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} retell lecture questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-answer-short-question-questions")
async def upload_answer_short_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['audioUrl', 'question', 'correctAnswer', 'acceptableAnswers',
         'difficulty', 'category', 'tags', 'title']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
        status_code=400,
        detail=f"Each question must contain fields: {', '.join(required_fields)}"
      )
    
    # Convert dict objects to AnswerShortQuestion objects
    questions = []
    for data in questions_data:
      question = AnswerShortQuestion(
      audio_url=str(data['audioUrl']).replace("'", "''").strip(),
      question=str(data['question']).replace("'", "''").strip(),
      correct_answer=str(data['correctAnswer']).replace("'", "''").strip(),
      acceptable_answers=parse_array(data.get('acceptableAnswers')),
      difficulty=str(data['difficulty']).replace("'", "''").strip(),
      category=str(data['category']).replace("'", "''").strip(),
      tags=parse_array(data.get('tags')),
      title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} answer short questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

@router.post("/upload-summarize-text-questions")
async def upload_summarize_text_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['passage', 'wordLimit', 'sampleSummary', 'keyIdeas',
         'difficulty', 'category', 'title']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
        status_code=400,
        detail=f"Each question must contain fields: {', '.join(required_fields)}"
      )
    
    # Convert dict objects to SummarizeTextQuestion objects
    questions = []
    for data in questions_data:
      question = SummarizeTextQuestion(
      passage=str(data['passage']).replace("'", "''").strip(),
      word_limit=data.get('wordLimit', 75),
      sample_summary=str(data['sampleSummary']).replace("'", "''").strip(),
      key_ideas=parse_array(data.get('keyIdeas')),
      difficulty=str(data['difficulty']).replace("'", "''").strip(),
      category=str(data['category']).replace("'", "''").strip(),
      title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} summarize text questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-write-essay-questions")
async def upload_write_essay_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['prompt', 'essayType',
         'difficulty', 'category', 'title']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
        status_code=400,
        detail=f"Each question must contain fields: {', '.join(required_fields)}"
      )
    
    # Convert dict objects to WriteEssayQuestion objects
    questions = []
    for data in questions_data:
      question = WriteEssayQuestion(
        prompt=str(data['prompt']).replace("'", "''").strip(),
        essay_type=str(data['essayType']).replace("'", "''").strip(),
        word_limit=data.get('wordLimit', 200),
        time_limit=data.get('timeLimit', 1200),
        rubric_content=str(data.get('rubricContent', '')).replace("'", "''").strip(),
        rubric_form=str(data.get('rubricForm', '')).replace("'", "''").strip(), 
        rubric_grammar=str(data.get('rubricGrammar', '')).replace("'", "''").strip(),
        rubric_vocabulary=str(data.get('rubricVocabulary', '')).replace("'", "''").strip(),
        sample_essay=str(data.get('sampleEssay', '')).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} write essay questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

def clean_value(value):
    """Return sanitized string (or None if missing)."""
    if value is None:
        return None
    return str(value).replace("'", "''").strip()

def parse_array(value, item_type=str):
  """Normalize JSON arrays or legacy comma/semicolon-separated values to lists."""
  if value is None or value == "":
    return None

  if isinstance(value, (list, tuple)):
    items = list(value)
  else:
    raw_value = str(value).strip()
    if not raw_value:
      return None
    try:
      parsed = json.loads(raw_value)
    except (json.JSONDecodeError, TypeError):
      parsed = None
    if isinstance(parsed, list):
      items = parsed
    else:
      items = re.split(r"[,;]", raw_value)

  normalized = [str(item).strip() for item in items if str(item).strip()]
  try:
    return [item_type(item) for item in normalized] or None
  except (TypeError, ValueError):
    raise HTTPException(status_code=422, detail="Array contains an invalid value")
  
@router.post("/upload-reading-fill-blanks-questions")
async def upload_reading_fill_blanks_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'text', 'blank1_answer', 'blank1_options',
              'blank2_answer', 'blank2_options', 'blank3_answer', 
              'blank3_options', 'blank4_answer', 'blank4_options',
              'blank5_answer', 'blank5_options', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ReadingFillBlanksTemplate objects
    questions = []
    for data in questions_data:
      question = ReadingFillBlanksTemplate(
      title = clean_value(data.get('title')),
      text = clean_value(data.get('text')),
      blank1_answer = clean_value(data.get('blank1_answer')),
      blank1_options = parse_array(data.get('blank1_options')),
      blank2_answer = clean_value(data.get('blank2_answer')),
      blank2_options = parse_array(data.get('blank2_options')),
      blank3_answer = clean_value(data.get('blank3_answer')),
      blank3_options = parse_array(data.get('blank3_options')),
      blank4_answer = clean_value(data.get('blank4_answer')),
      blank4_options = parse_array(data.get('blank4_options')),
      blank5_answer = clean_value(data.get('blank5_answer')),
      blank5_options = parse_array(data.get('blank5_options')),
      difficulty = clean_value(data.get('difficulty')),
      category=clean_value(data.get('category')) 
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} reading fill blanks questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-reading-fill-blanks-rw-questions")
async def upload_reading_fill_blanks_rw_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'passage', 'blank1_answer', 'blank1_options',
              'blank2_answer', 'blank2_options', 'blank3_answer', 
              'blank3_options', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ReadingFillBlanksRWTemplate objects
    questions = []
    for data in questions_data:
      question = ReadingFillBlanksRWTemplate(
        title = clean_value(data.get('title')),
        passage = clean_value(data.get('passage')),
        time_limit=data.get('time_limit', 600),
        blank1_answer = clean_value(data.get('blank1_answer')),
        blank1_options = parse_array(data.get('blank1_options')),
        blank2_answer = clean_value(data.get('blank2_answer')),
        blank2_options = parse_array(data.get('blank2_options')),
        blank3_answer = clean_value(data.get('blank3_answer')),
        blank3_options = parse_array(data.get('blank3_options')),
        difficulty = clean_value(data.get('difficulty')),
        category=clean_value(data.get('category'))
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} reading fill blanks RW questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

@router.post("/upload-multiple-choice-multiple-questions")
async def upload_multiple_choice_multiple_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'passage', 'question', 'optionA', 'optionB',
              'optionC', 'optionD', 'correctAnswers', 'difficulty', 
              'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to MultipleChoiceMultipleTemplate objects
    questions = []
    for data in questions_data:
      question = MultipleChoiceMultipleTemplate(

        title=str(data['title']).replace("'", "''").strip(),
        passage=str(data['passage']).replace("'", "''").strip(),
        question=str(data['question']).replace("'", "''").strip(),
        option_a=str(data['optionA']).replace("'", "''").strip(),
        option_b=str(data['optionB']).replace("'", "''").strip(),
        option_c=str(data['optionC']).replace("'", "''").strip(),
        option_d=str(data['optionD']).replace("'", "''").strip(),
        option_e=str(data.get('optionE', '')).replace("'", "''").strip(),
        correct_answers= parse_array(data.get('correctAnswers')),
        time_limit=data.get('timeLimit', 600),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} multiple choice multiple questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple-choice-single-questions")
async def upload_multiple_choice_single_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'passage', 'question', 'optionA', 'optionB',
              'optionC', 'optionD', 'correctAnswer', 'difficulty', 
              'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to MultipleChoiceSingleTemplate objects
    questions = []
    for data in questions_data:
      question = MultipleChoiceSingleTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        passage=str(data['passage']).replace("'", "''").strip(),
        question=str(data['question']).replace("'", "''").strip(),
        option_a=str(data['optionA']).replace("'", "''").strip(),
        option_b=str(data['optionB']).replace("'", "''").strip(),
        option_c=str(data['optionC']).replace("'", "''").strip(),
        option_d=str(data['optionD']).replace("'", "''").strip(),
        correct_answer=str(data['correctAnswer']).replace("'", "''").strip(),
        time_limit=data.get('timeLimit', 600),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} multiple choice single questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

@router.post("/upload-reorder-paragraphs-questions")
async def upload_reorder_paragraphs_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'paragraph1', 'paragraph2', 'paragraph3', 
              'paragraph4', 'correctOrder', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ReorderParagraphsTemplate objects  
    questions = []
    for data in questions_data:
      question = ReorderParagraphsTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        paragraph1=str(data['paragraph1']).replace("'", "''").strip(),
        paragraph2=str(data['paragraph2']).replace("'", "''").strip(),
        paragraph3=str(data['paragraph3']).replace("'", "''").strip(),
        paragraph4=str(data['paragraph4']).replace("'", "''").strip(),
        paragraph5=str(data.get('paragraph5', '')).replace("'", "''").strip(),
        correct_order=parse_array(data.get('correctOrder'), int),
        time_limit=data.get('timeLimit', 600),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} reorder paragraphs questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-summarize-spoken-text-questions")
async def upload_summarize_spoken_text_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'transcript', 'wordLimit', 
                      'keyPoints', 'sampleSummary', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to SummarizeSpokenTextTemplate objects
    questions = []
    for data in questions_data:
      question = SummarizeSpokenTextTemplate(
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        duration=data.get('duration'),
        word_limit=data.get('wordLimit', 70),
        time_limit=data.get('timeLimit', 600),
        key_points = parse_array(data.get('keyPoints')),
        sample_summary=str(data['sampleSummary']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip(),
        title=str(data['title']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} summarize spoken text questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-listening-multiple-choice-multiple-questions")
async def upload_listening_multiple_choice_multiple_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'question', 'optionA', 'optionB',
              'optionC', 'optionD', 'correctAnswers', 'transcript',
              'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ListeningMultipleChoiceMultipleTemplate objects
    questions = []
    for data in questions_data:
      question = ListeningMultipleChoiceMultipleTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        question=str(data['question']).replace("'", "''").strip(),
        option_a=str(data['optionA']).replace("'", "''").strip(),
        option_b=str(data['optionB']).replace("'", "''").strip(),
        option_c=str(data['optionC']).replace("'", "''").strip(),
        option_d=str(data['optionD']).replace("'", "''").strip(),
        option_e=str(data.get('optionE', '')).replace("'", "''").strip(),
        correct_answers=parse_array(data.get('correctAnswers')),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} listening multiple choice multiple questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
@router.post("/upload-listening-multiple-choice-single-questions")
async def upload_listening_multiple_choice_single_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'question', 'optionA', 'optionB',
              'optionC', 'optionD', 'correctAnswer', 'transcript',
              'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ListeningMultipleChoiceSingleTemplate objects
    questions = []
    for data in questions_data:
      question = ListeningMultipleChoiceSingleTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        question=str(data['question']).replace("'", "''").strip(),
        option_a=str(data['optionA']).replace("'", "''").strip(),
        option_b=str(data['optionB']).replace("'", "''").strip(),
        option_c=str(data['optionC']).replace("'", "''").strip(),
        option_d=str(data['optionD']).replace("'", "''").strip(),
        correct_answer=str(data['correctAnswer']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} listening multiple choice single questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-listening-fill-blanks-questions")
async def upload_listening_fill_blanks_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'transcript', 'blank1_answer', 
              'blank1_word', 'blank2_answer', 'blank2_word',
              'blank3_answer', 'blank3_word', 'extraWords',
              'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to ListeningFillBlanksTemplate objects
    questions = []
    for data in questions_data:
      question = ListeningFillBlanksTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        duration=data.get('duration'),
        blank1_answer=str(data['blank1_answer']).replace("'", "''").strip(),
        blank1_word=str(data['blank1_word']).replace("'", "''").strip(),
        blank2_answer=str(data['blank2_answer']).replace("'", "''").strip(),
        blank2_word=str(data['blank2_word']).replace("'", "''").strip(),
        blank3_answer=str(data['blank3_answer']).replace("'", "''").strip(),
        blank3_word=str(data['blank3_word']).replace("'", "''").strip(),
        extra_words=parse_array(data.get('extraWords')),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} listening fill blanks questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-highlight-correct-summary-questions")
async def upload_highlight_correct_summary_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'summaryA', 'summaryB',
              'summaryC', 'correctSummary', 'transcript',
              'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to HighlightCorrectSummaryTemplate objects
    questions = []
    for data in questions_data:
      question = HighlightCorrectSummaryTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        summary_a=str(data['summaryA']).replace("'", "''").strip(),
        summary_b=str(data['summaryB']).replace("'", "''").strip(),
        summary_c=str(data['summaryC']).replace("'", "''").strip(),
        correct_summary=str(data['correctSummary']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} highlight correct summary questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  
@router.post("/upload-select-missing-word-questions")
async def upload_select_missing_word_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'transcript', 'missingWordPosition',
              'optionA', 'optionB', 'optionC', 'optionD', 
              'correctAnswer', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to SelectMissingWordTemplate objects
    questions = []
    for data in questions_data:
      question = SelectMissingWordTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(), 
        missing_word_position=int(data['missingWordPosition']),
        option_a=str(data['optionA']).replace("'", "''").strip(),
        option_b=str(data['optionB']).replace("'", "''").strip(),
        option_c=str(data['optionC']).replace("'", "''").strip(),
        option_d=str(data['optionD']).replace("'", "''").strip(),
        correct_answer=str(data['correctAnswer']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} select missing word questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

@router.post("/upload-highlight-incorrect-words-questions")
async def upload_highlight_incorrect_words_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'transcript', 'incorrectWords', 
              'correctTranscript', 'difficulty', 'category']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to HighlightIncorrectWordsTemplate objects
    questions = []
    for data in questions_data:
      question = HighlightIncorrectWordsTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        transcript=str(data['transcript']).replace("'", "''").strip(),
        incorrect_words=parse_array(data.get('incorrectWords')),
        correct_transcript=str(data['correctTranscript']).replace("'", "''").strip(),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} highlight incorrect words questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  

@router.post("/upload-write-from-dictation-questions")
async def upload_write_from_dictation_questions(
  questions_data: List[dict],
  db: Session = Depends(get_db)
):
  try:
    required_fields = ['title', 'audioUrl', 'sentence', 'difficulty', 
                      'category', 'keyWords']
    
    for question in questions_data:
      if not all(field in question for field in required_fields):
        raise HTTPException(
          status_code=400,
          detail=f"Each question must contain fields: {', '.join(required_fields)}"
        )
    
    # Convert dict objects to WriteFromDictationTemplate objects
    questions = []
    for data in questions_data:
      question = WriteFromDictationTemplate(
        title=str(data['title']).replace("'", "''").strip(),
        audio_url=str(data['audioUrl']).replace("'", "''").strip(),
        sentence=str(data['sentence']).replace("'", "''").strip(),
        play_count=data.get('playCount', 2),
        key_words=parse_array(data.get('keyWords')),
        difficulty=str(data['difficulty']).replace("'", "''").strip(),
        category=str(data['category']).replace("'", "''").strip()
      )
      questions.append(question)
    
    # Add all questions to the database
    db.bulk_save_objects(questions)
    db.commit()
    
    return {"message": f"Successfully uploaded {len(questions)} write from dictation questions"}
    
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

