from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoreResponse(BaseModel):
  score: float
  similarity: float
  transcript: str
  feedback: str

class AuthBody(BaseModel):
    token: str

class EvaluationScore(BaseModel):
    content: float
    fluency: float
    pronunciation: float

class MaxScores(BaseModel):
    content: int
    fluency: int
    pronunciation: int

class EvaluationResult(BaseModel):
    transcribed_text: str
    evaluation: EvaluationScore


class UserInput(BaseModel):
    id: Optional[int]
    email: str
    full_name: Optional[str]
    role: Optional[str]

class LoginDetails(BaseModel):
    email: str
    password: str

class RegisterDetails(BaseModel):
    email: str
    password: str
    full_name: Optional[str]


class ProfileUpdate(BaseModel):
    target_score: Optional[int] = Field(default=None, ge=10, le=90)
    test_date: Optional[date] = None


class FirebaseIdentityResponse(BaseModel):
    id: int
    uid: str
    email: str
    full_name: Optional[str]
    role: str
    target_score: Optional[int]
    test_date: Optional[date]

    model_config = ConfigDict(from_attributes=True)