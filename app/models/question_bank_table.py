from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB  # PostgreSQL dialect for JSONB
from app.database.base import Base  # Base class for SQLAlchemy models
from sqlalchemy.schema import Sequence  # For managing default sequences

class QuestionBank(Base):
    __tablename__ = "question_bank_table"  # Match the table name in your schema

    id = Column(Integer, primary_key=True, index=True, server_default=Sequence("question_bank_table_id_seq"))  # Auto-incrementing ID with default sequence
    topic = Column(String(255), nullable=True)  # Topic with a max length of 255
    sub_topic = Column(String(255), nullable=True)  # Sub-topic with a max length of 255
    content = Column(JSONB, nullable=True)  # JSONB column to store question content
