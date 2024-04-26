from sqlalchemy import Column, Integer, String
from app.database.base import Base

class KnowledgeUpdate(Base):
    __tablename__ = "knowledge_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    topic_id = Column(Integer, nullable=False)  # The topic being updated
    new_information = Column(String(1024), nullable=False)  # The updated information for the topic
