from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base

class UserPracticeTests(Base):
    __tablename__ = "user_practice_tests"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # Foreign key to the user table
    practice_test_id = Column(Integer, ForeignKey("practice_tests_table.id"), primary_key=True)  # Foreign key to practice tests
    completed_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user completed the test
    score = Column(Integer, nullable=True)  # Optional score
