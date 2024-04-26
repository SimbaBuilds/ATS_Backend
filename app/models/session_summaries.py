from sqlalchemy import Column, Integer, JSONB
from app.database.base import Base

class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    chat_id = Column(Integer, nullable=False)  # Identifier for the chat session
    highlights = Column(JSONB, nullable=False)  # Key points from the session in JSONB format
