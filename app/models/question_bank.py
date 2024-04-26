from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database.base import Base

# Question table for storing question bank data
class QuestionBankTable(Base):
    __tablename__ = "question_bank_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    topic = Column(String(255), nullable=False)  # Main topic of the question
    sub_topic = Column(String(255), nullable=True)  # Optional sub-topic
    content = Column(JSONB, nullable=False)  # JSON content for the question

# Practice test table for storing practice test data
class PracticeTestsTable(Base):
    __tablename__ = "practice_tests_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    test = Column(String(255), nullable=False)  # Name of the practice test
    content = Column(JSONB, nullable=False)  # JSON content for the practice test
