from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy import ForeignKey

class UserMessage(Base):
    __tablename__ = "user_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to "users" table
    content = Column(Text, nullable=False)  # Message content
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the message was sent
