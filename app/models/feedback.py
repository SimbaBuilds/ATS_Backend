from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func  # Add this import
from app.database.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String(500), nullable=False)
    rating = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())  # This should work now
