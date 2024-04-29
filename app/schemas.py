from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Text, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Sequence  # For managing default sequences
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, Dict, List
from uuid import UUID


#region
# Pydantic model for AdminActions
class AdminActionResponse(BaseModel):
    id: int
    action_type: str
    user_id = int
    details = str
    timestamp = datetime


    class Config:
        orm_mode = True


# Pydantic model for AdminActions
class DeleteAdminActionResponse(BaseModel):
    status: str
    action_id: int

    class Config:
        orm_mode = True

# Pydantic model for AdminActions
class RecordAdminActionResponse(BaseModel):
    status: str
    action_id: int

    class Config:
        orm_mode = True

# Pydantic model for AdminActions
class DeleteUserResponse(BaseModel):
    status: str
    user_id: int

    class Config:
        orm_mode = True

class UpdateUserResponse(BaseModel):
    status: str
    user_id: int
    user_role: str
    user_status: bool

    class Config:
        orm_mode = True


#endregion



# Pydantic model for Answer
class AnswerResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    question_id: int
    answer: str
    correct: bool
    timestamp: datetime

    class Config:
        orm_mode = True


# Pydantic model for ChatbotResponse
class ChatbotResponseResponse(BaseModel):
    id: int
    user_id: int
    response: str
    created_at: datetime

    class Config:
        orm_mode = True


# Pydantic model for CurriculumPlan
class CurriculumPlanResponse(BaseModel):
    id: int
    user_id: int
    plan_name: str
    subjects: dict  # JSONB in PostgreSQL corresponds to dict in Python
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


# Pydantic model for Feedback
class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    comment: str
    rating: Optional[int]
    timestamp: datetime

    class Config:
        orm_mode = True


# Pydantic model for Homework
class HomeworkResponse(BaseModel):
    id: int
    user_id: int
    assignment: str
    due_date: Optional[date]
    details: Optional[str]

    class Config:
        orm_mode = True



# Pydantic model for KnowledgeUpdate
class KnowledgeUpdateResponse(BaseModel):
    id: int
    topic_id: int
    new_information: str

    class Config:
        orm_mode = True


# Pydantic model for Notification
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    is_dismissed: bool
    timestamp: datetime

    class Config:
        orm_mode = True



# Pydantic model for PerformanceAnalytics
class PerformanceAnalyticsResponse(BaseModel):
    id: int
    subject: str
    average_score: float
    completion_rate: float
    difficulty_level: Optional[str]

    class Config:
        orm_mode = True


# Pydantic model for PracticeTestsTable
class PracticeTestsResponse(BaseModel):
    id: int
    practice_test: str
    type: Optional[str]
    domain: Optional[str]
    skill: Optional[str]
    topic: Optional[str]
    sub_topic: Optional[str]
    question_number: Optional[int]
    difficulty: Optional[str]
    figure_description: Optional[str]
    image: Optional[str]
    equation: Optional[str]
    svg: Optional[str]
    tabular_data: Optional[Dict]
    question_content: Optional[str]
    answer_explanation: Optional[str]
    correct_answer: Optional[str]
    choices: Optional[Dict]

    class Config:
        orm_mode = True


# Pydantic model for QuestionBank
class QuestionBankResponse(BaseModel):
    id: int
    topic: Optional[str]
    sub_topic: Optional[str]
    question_number_in_subtopic: Optional[int]
    figure_description: Optional[str]
    image: Optional[str]
    equation: Optional[str]
    svg: Optional[str]
    question_content: Optional[str]
    answer_explanation: Optional[str]
    correct_answer: Optional[str]
    tabular_data: Optional[Dict]
    choices: Optional[Dict]

    class Config:
        orm_mode = True



# Pydantic model for Reminder
class ReminderResponse(BaseModel):
    id: int
    user_id: int
    reminder_time: datetime
    message: str

    class Config:
        orm_mode = True


# Pydantic model for SessionSummary
class SessionSummaryResponse(BaseModel):
    id: int
    chat_id: int
    highlights: Dict

    class Config:
        orm_mode = True


# Pydantic model for TestAttempt
class TestAttemptResponse(BaseModel):
    attempt_id: int
    test_id: int
    user_id: int
    status: str
    responses: Dict
    created_at: datetime

    class Config:
        orm_mode = True



class UsageAnalyticsResponse(BaseModel):
    id: int
    feature_name: str
    usage_count: int
    last_used: Optional[datetime]

    class Config:
        orm_mode = True


class UserMessageResponse(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserPracticeTestsResponse(BaseModel):
    user_id: int
    practice_test_id: int
    completed_at: datetime
    score: Optional[int]

    class Config:
        orm_mode = True


class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    score: int
    timestamp: datetime
    session_id: Optional[UUID]

    class Config:
        orm_mode = True



class UserQuestionsSeenResponse(BaseModel):
    user_id: int
    question_id: int
    seen_at: datetime

    class Config:
        orm_mode = True


class UserSettingsResponse(BaseModel):
    id: int
    user_id: int
    setting: str
    setting_type: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    access_token: Optional[str]
    token_type: Optional[str]
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    role: Optional[str]
    status: bool
    profile_picture: Optional[str]
    additional_info: Optional[dict]  # JSONB is represented as a dictionary in Python

    class Config:
        orm_mode = True