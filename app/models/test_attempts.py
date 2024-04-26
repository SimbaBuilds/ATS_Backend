from sqlalchemy import Column, Integer, String, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base


class TestAttempt(Base):
    __tablename__ = "test_attempts_table"

    attempt_id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    test_id = Column(Integer, ForeignKey("practice_tests_table.id"), nullable=False)  # Reference to the "practice_tests_table"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to the "users" table
    status = Column(String(50), nullable=False)  # Status: "started", "in_progress", or "completed"
    responses = Column(JSON, nullable=False)  # JSON-encoded user responses
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the attempt was created
