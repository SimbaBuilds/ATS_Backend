from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Text, Date, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Sequence  # For managing default sequences
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from uuid import UUID


#ADMIN SPECIFIC RESPONSE MODELS
#region 
# Pydantic model for AdminActions
class AdminActionResponse(BaseModel):
    id: int
    action_type: str
    user_id: int
    details: str
    timestamp: datetime


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


# ANSWER RESPONSE MODELS
#region
class SubmitAnswerResponse(BaseModel):
    id: int
    timestamp: datetime
    status: str

    class Config:
        orm_mode = True

# Pydantic Schema for submitting answers
class AnswerSchema(BaseModel):
    user_id: int
    answer: str
    correct: bool


class GetAnswersResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    question_id: int
    answer: str
    correct: bool
    timestamp: datetime

    class Config:
        orm_mode = True


class UpdateAnswerResponse(BaseModel):
    id: int
    answer: str
    correct: bool

    class Config:
        orm_mode = True

#endregion
        

#AUTH_USER_MGMT RESPONSE/INPUT MODELS
#region

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
    additional_info: Optional[dict]

    class Config:
        orm_mode = True


class AddUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime
    role: Optional[str] = None
    status: bool = Field(default=True, description="Active or suspended status of the user")

    class Config:
        orm_mode = True

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str

#expected format of arguments to update_user endpoint
class UpdateUserInput(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    full_name: Optional[str]
    role: Optional[str]
    status: Optional[bool]
    profile_picture: Optional[str]
    additional_info: Optional[dict]

class UpdateUserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    role: Optional[str]
    status: bool
    profile_picture: Optional[str]
    additional_info: Optional[dict]

    class Config:
        orm_mode = True

class DeleteUserResponse(BaseModel):
    detail: str


#endregion


#CHATBOTACTIONS
#region
class UpdateKnowledgeResponse(BaseModel):
    status: str
    topic_id: int
    new_information: str

class PersonalizeChatResponse(BaseModel):
    status: str
    user_id: int
    preference: str

    class Config:
        orm_mode = True


class SessionSummaryResponse(BaseModel):
    status: str
    chat_id: int
    highlights: List[str]

class SetReminderResponse(BaseModel):
    status: str
    user_id: int
    message: str

    class Config:
        orm_mode = True

class GetUserSettingResponse(BaseModel):
    user_id: int
    setting_name: str
    setting_value: str

    class Config:
        orm_mode = True

#endregion


#COMMUNICATION
#region
class NotificationModel(BaseModel):
    id: int
    user_id: int
    message: str
    is_dismissed: bool
    timestamp: datetime

    class Config:
        orm_mode = True

class GetNotificationsResponse(BaseModel):
    notifications: List[NotificationModel]

class FeedbackModel(BaseModel):
    user_id: int
    comment: str
    rating: int
    timestamp: datetime

    class Config:
        orm_mode = True

class SubmitFeedbackResponse(BaseModel):
    status: str
    feedback_id: int

class DismissNotificationResponse(BaseModel):
    status: str

class NotificationHistoryModel(BaseModel):
    id: int
    user_id: int
    message: str
    is_dismissed: bool
    timestamp: datetime

    class Config:
        orm_mode = True

class GetNotificationHistoryResponse(BaseModel):
    user_id: int
    history: List[NotificationHistoryModel]

class SendEmailResponse(BaseModel):
    status: str


#endregion


#CURRICULUM_AND_STUDY_PLAN
#region
class UserModel(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class GetAllUsersResponse(BaseModel):
    users: List[UserModel]

class CurriculumPlanModel(BaseModel):
    id: int
    user_id: int
    title: str
    description: str

    class Config:
        orm_mode = True

class GetCurriculumResponse(BaseModel):
    user_id: int
    curriculum_plans: List[CurriculumPlanModel]

class CreateCurriculumResponse(BaseModel):
    status: str
    plan_id: int



class CurriculumPlanBase(BaseModel):
    name: str
    description: Optional[str] = None

class CurriculumPlan(CurriculumPlanBase):
    id: int

    class Config:
        orm_mode = True

class UpdateCurriculumResponse(BaseModel):
    message: str
    plan: CurriculumPlan

    class Config:
        orm_mode = True

class DeleteCurriculumResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True

#endregion


#HOMEWORK
#region
class HomeworkBase(BaseModel):
    user_id: int
    assignment: str
    due_date: datetime
    details: Optional[str] = None

class Homework(HomeworkBase):
    id: int

    class Config:
        orm_mode = True

class HomeworkAssignmentsResponse(BaseModel):
    homework: List[Homework]

    class Config:
        orm_mode = True

class HomeworkAssignmentResponse(BaseModel):
    message: str
    homework_id: int

    class Config:
        orm_mode = True

class UpdateHomeworkResponse(BaseModel):
    message: str
    homework: Homework

    class Config:
        orm_mode = True

class DeleteHomeworkResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True

#endregion

#IN-SESSION CHAT
#region
        
class MessageSchema(BaseModel):
    user_id: int
    content: str
    role: str

    class Config:
        orm_mode = True  # This enables the model to handle ORM objects

class ConversationSchema(BaseModel):
    id: int
    title: str
    messages: list[MessageSchema] = []

    class Config:
        orm_mode = True

    
class ChatHistorySchema(BaseModel):
    id: int
    user_id: int
    messages: List[Dict[str, Any]]  # Assuming messages are stored as a list of dictionaries
    session_start: datetime

    class Config:
        orm_mode = True

class ChatbotResponseSchema(BaseModel):
    user_id: int
    response: str

    class Config:
        orm_mode = True


class AnalyzeImageResponse(BaseModel):
    filename: str
    status: str

class UserMessageStatusResponse(BaseModel):
    status: str
    content: str

class UserMessageSchema(BaseModel):
    user_id: int
    content: str
    role: str

    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    history: List[UserMessageSchema]

class FeedbackReceivedResponse(BaseModel):
    status: str
    rating: int
    comment: str

#endregion

#PRACTICE TESTS
#region

class GetTestResponse(BaseModel):
    id: int
    test_name: str
    content: dict

    class Config:
        orm_mode = True

class CreateTestResponse(BaseModel):
    test_id: int

    class Config:
        orm_mode = True

class DeleteTestResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True

#endregion

#PROGRESS TRACKING
#region

class UserProgressBase(BaseModel):
    user_id: int
    quiz_id: int
    score: float
    timestamp: datetime
    session_id: UUID

    class Config:
        orm_mode = True        

class UserProgressListResponse(BaseModel):
    progress: List[UserProgressBase]

class CreateProgressResponse(UserProgressBase):
    pass  # This inherits all fields from UserProgressBase

#endregion


#QUESTION MGMT
#region

class QuestionBase(BaseModel):
    id: int
    topic: str
    sub_topic: str
    content: str

    class Config:
        orm_mode = True

# Pydantic model for QuestionBank
class GetQBQuestionResponse(BaseModel):
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

class UpdateQuestionResponse(BaseModel):
    id: int
    message: str

class DeleteQuestionResponse(BaseModel):
    message: str

# Pydantic model for PracticeTestsTable
class GetPracticeTestResponse(BaseModel):
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


class UpdatePracticeTestResponse(BaseModel):
    message: str

class DeletePracticeTestResponse(BaseModel):
    message: str

class GetPracticeTestQuestionResponse(BaseModel):
    question: dict

#endregion


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


