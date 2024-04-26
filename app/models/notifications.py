from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the "users" table
    message = Column(String(255), nullable=False)  # Notification message
    is_dismissed = Column(Boolean, default=False)  # Default is not dismissed
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Automatically set the current timestamp
