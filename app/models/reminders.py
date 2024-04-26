from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from app.database.base import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the user table
    reminder_time = Column(TIMESTAMP, nullable=False)  # Scheduled time for the reminder
    message = Column(String(255), nullable=False)  # Reminder message
