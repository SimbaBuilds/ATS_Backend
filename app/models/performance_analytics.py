from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base

class PerformanceAnalytics(Base):
    __tablename__ = "performance_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    subject = Column(String(255), nullable=False)  # Subject name
    average_score = Column(Float, nullable=False)  # Average score across users
    completion_rate = Column(Float, nullable=False)  # Completion rate as a percentage
    difficulty_level = Column(String(50), nullable=True)  # Optional difficulty level
