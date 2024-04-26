from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy import ForeignKey

class ChatbotResponse(Base):
    __tablename__ = "chatbot_responses"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to "users" table
    response = Column(Text, nullable=False)  # Chatbot's response message
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the response was created
