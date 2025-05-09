from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Text, Date, ForeignKey, Float, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from uuid import UUID as PythonUUID
from sqlalchemy_utils import UUIDType
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Sequence  # For managing default sequences
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, Dict, List
from sqlalchemy.orm import relationship
import uuid



# Model for logging administrative actions
class AdminActionsTable(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    action_type = Column(String(255), nullable=False)  # Type of admin action (e.g., 'delete', 'update')
    user_id = Column(Integer, nullable=True, index=True)  # Optional ID of the user associated with the action
    details = Column(String(255), nullable=True)  # Optional details about the action
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Timestamp of the admin action


class Answer(Base):
    __tablename__ = "answers"  # Table name matching the queries

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Auto-incrementing primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key referencing the "users" table
    quiz_id = Column(Integer, nullable=False)  # ID of the quiz or practice test
    question_id = Column(Integer, ForeignKey("question_bank_table.id"), nullable=False)  #MAY NEED TO FIGURE OUT QUESTION ID THING
    answer = Column(String(255), nullable=False)  # Answer given by the user
    correct = Column(Boolean, nullable=False)  # Indicates if the answer is correct
    timestamp = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)  # Submission time


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the "users" table
    messages = Column(JSON, nullable=False)  # Stores a list of message objects
    session_start = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the chat session started



class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    conversation_number = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Automatically set the current timestamp

    title = Column(String, index=True)
    messages = relationship("Message", back_populates="conversation")

    # Add any additional fields or relationships as necessary



class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    content = Column(String)
    role = Column(String)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Automatically set the current timestamp
    conversation_id = Column(ForeignKey('conversations.id'))

    conversation = relationship("Conversation", back_populates="messages")



class CurriculumPlan(Base):
    __tablename__ = "curriculum_plans"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key with auto-increment
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the "users" table
    plan_name = Column(String(255), nullable=False)  # Name of the curriculum plan
    subjects = Column(JSONB, nullable=False)  # Subjects or topics in the plan, stored as JSON
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the plan was created



class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String(500), nullable=False)
    rating = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # This should work now



class Homework(Base):
    __tablename__ = "homework_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to the "users" table
    assignment = Column(String(255), nullable=False)  # Homework assignment description
    due_date = Column(Date, nullable=True)  # Due date for the homework
    details = Column(Text, nullable=True)  # Additional details for the assignment




class KnowledgeUpdate(Base):
    __tablename__ = "knowledge_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    topic_id = Column(Integer, nullable=False)  # The topic being updated
    new_information = Column(String(1024), nullable=False)  # The updated information for the topic



class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the "users" table
    message = Column(String(255), nullable=False)  # Notification message
    is_dismissed = Column(Boolean, default=False)  # Default is not dismissed
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Automatically set the current timestamp



class PerformanceAnalytics(Base):
    __tablename__ = "performance_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    subject = Column(String(255), nullable=False)  # Subject name
    average_score = Column(Float, nullable=False)  # Average score across users
    completion_rate = Column(Float, nullable=False)  # Completion rate as a percentage
    difficulty_level = Column(String(50), nullable=True)  # Optional difficulty level



# Practice test table for storing practice test data
class PracticeTestQuestion(Base):
    __tablename__ = "practice_tests_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    practice_test = Column(String(255), nullable=False)  # Name of the practice test
    type = Column(String(255), nullable=True)  # Type of practice test
    domain = Column(String(255), nullable=True)  # Test domain
    skill = Column(String(255), nullable=True)  # Skill tested
    topic = Column(String(255), nullable=True)  # Main topic of the question
    sub_topic = Column(String(255), nullable=True)  # Sub-topic
    question_number = Column(Integer, nullable=True)  # Question number
    difficulty = Column(String(255), nullable=True)  # Difficulty level
    figure_description = Column(String, nullable=True)  # Description for figures/images
    image = Column(String, nullable=True)  # Image content or URL
    equation = Column(String, nullable=True)  # Mathematical equations in String format
    svg = Column(String, nullable=True)  # SVG content
    tabular_data = Column(JSONB, nullable=True)  # Tabular data in JSON format
    question_content = Column(String, nullable=True)  # String content for questions
    answer_explanation = Column(String, nullable=True)  # Explanation for correct answer
    correct_answer = Column(String, nullable=True)  # The correct answer in String format
    choices = Column(JSONB, nullable=True)  # JSON content with multiple choices



class QuestionBankQuestion(Base):
    __tablename__ = "question_bank_table"  # Match the table name in your schema

     # Primary key with auto-incrementing sequence
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # String-based attributes
    topic = Column(String(255), nullable=True)  # Main topic of the question
    sub_topic = Column(String(255), nullable=True)  # Sub-topic
    question_number_in_subtopic = Column(Integer, nullable=True)  # Question number within the sub-topic
    figure_description = Column(String, nullable=True)  # Description for any figures/images
    image = Column(String, nullable=True)  # Store image URLs or paths
    equation = Column(String, nullable=True)  # String-based mathematical equations
    svg = Column(String, nullable=True)  # Store SVG code
    question_content = Column(String, nullable=True)  # Question String content
    answer_explanation = Column(String, nullable=True)  # Explanation for the answer
    correct_answer = Column(String, nullable=True)  # The correct answer in String format
    
    # JSON-based attributes
    tabular_data = Column(JSONB, nullable=True)  # JSON-based tabular data
    choices = Column(JSONB, nullable=True)  # Possible answer choices in JSON format



class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the user table
    reminder_time = Column(TIMESTAMP, nullable=False)  # Scheduled time for the reminder
    message = Column(String(255), nullable=False)  # Reminder message




class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    chat_id = Column(Integer, nullable=False)  # Identifier for the chat session
    highlights = Column(JSONB, nullable=False)  # Key points from the session in JSONB format


class TestAttempt(Base):
    __tablename__ = "test_attempts_table"

    attempt_id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    test_id = Column(Integer, ForeignKey("practice_tests_table.id"), nullable=False)  # Reference to the "practice_tests_table"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to the "users" table
    status = Column(String(50), nullable=False)  # Status: "started", "in_progress", or "completed"
    responses = Column(JSONB, nullable=False)  # JSON-encoded user responses
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the attempt was created




class UsageAnalytics(Base):
    __tablename__ = "usage_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    feature_name = Column(String(255), nullable=False)  # Feature name
    usage_count = Column(Integer, nullable=False)  # Usage count
    last_used = Column(TIMESTAMP, nullable=True)  # Optional last used timestamp



class UserMessage(Base):
    __tablename__ = "user_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to "users" table
    content = Column(Text, nullable=False)  # Message content
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the message was sent





class UserPracticeTests(Base):
    __tablename__ = "user_practice_tests"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # Foreign key to the user table
    practice_test_id = Column(Integer, ForeignKey("practice_tests_table.id"), primary_key=True)  # Foreign key to practice tests
    completed_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user completed the test
    score = Column(Integer, nullable=True)  # Optional score





class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the user table
    setting = Column(String(255), nullable=False)  # The specific user setting
    setting_type = Column(String(50), nullable=False)  # A type to differentiate between personalization and other settings



class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    access_token = Column(String(255), nullable=True)  
    token_type = Column(String(255), nullable=True)  
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Hashed password
    full_name = Column(String(255), nullable=True)  # Optional full name
    created_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user was created
    updated_at = Column(TIMESTAMP, onupdate=func.now())  # Updated when user information changes
    role = Column(String(50), nullable=True)  # Optional role (e.g., student, tutor)
    status = Column(Boolean, default=True)  # Active or suspended
    profile_picture = Column(String(255), nullable=True)  # Reference to the profile picture
    additional_info = Column(JSONB, nullable=True)  # Store additional user-related data
    progress = relationship('UserQuestionProgress', back_populates='user')

class QuestionType(Base):
    __tablename__ = 'question_types'
    question_type_id = Column(Integer, primary_key=True, autoincrement=True)
    question_type_name = Column(String, nullable=False, unique=True)
    progress = relationship('UserQuestionProgress', back_populates='question_type')

class UserQuestionProgress(Base):
    __tablename__ = 'user_question_progress'
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), primary_key=True)
    question_type_id = Column(Integer, ForeignKey('question_types.question_type_id'), primary_key=True)
    progress = Column(Integer, nullable=False, default=0)
    user = relationship('User', back_populates='progress')
    question_type = relationship('QuestionType', back_populates='progress')

    @property
    def question_type_name(self):
        return self.question_type.question_type_name

    __table_args__ = (
        UniqueConstraint('user_id', 'question_type_id', name='uix_user_question_type'),
    )

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # ID of the user
    quiz_id = Column(Integer, nullable=False, index=True)  # ID of the quiz or test
    score = Column(Integer, nullable=False)  # Score (can be a percentage or total)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # When the progress was recorded
    session_id = Column(UUIDType, nullable=True, index=True)


# # MODEL TO DB
# from sqlalchemy import create_engine
# from app.database.base import Base
# from app.models import *  # This imports all models

# DATABASE_URL = "postgresql://cameronhightower:Wellpleased22!@localhost:5432/automated_tutoring_service"
# engine = create_engine(DATABASE_URL, echo=True)  # Set echo to True to log SQL queries
# Base.metadata.create_all(engine)
