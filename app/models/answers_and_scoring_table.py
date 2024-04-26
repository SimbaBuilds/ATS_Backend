from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.schema import ForeignKey
from app.database.base import Base  # Base class for SQLAlchemy models

class Answer(Base):
    __tablename__ = "answers"  # Table name matching the queries

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Auto-incrementing primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key referencing the "users" table
    quiz_id = Column(Integer, nullable=False)  # ID of the quiz or practice test
    question_id = Column(Integer, ForeignKey("question_bank_table.id"), nullable=False)  #MAY NEED TO FIGURE OUT QUESTION ID THING
    answer = Column(String(255), nullable=False)  # Answer given by the user
    correct = Column(Boolean, nullable=False)  # Indicates if the answer is correct
    timestamp = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)  # Submission time
