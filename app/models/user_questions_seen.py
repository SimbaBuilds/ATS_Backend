from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base

class UserQuestionsSeen(Base):
    __tablename__ = "user_questions_seen"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # Foreign key to the user table
    question_id = Column(Integer, ForeignKey("question_bank_table.id"), primary_key=True)  # Foreign key to the question bank
    seen_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user saw the question
