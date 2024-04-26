from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database.base import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # ID of the user
    quiz_id = Column(Integer, nullable=False, index=True)  # ID of the quiz or test
    score = Column(Integer, nullable=False)  # Score (can be a percentage or total)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # When the progress was recorded
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Optional session ID to group related activities
