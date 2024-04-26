from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base



class UsageAnalytics(Base):
    __tablename__ = "usage_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    feature_name = Column(String(255), nullable=False)  # Feature name
    usage_count = Column(Integer, nullable=False)  # Usage count
    last_used = Column(TIMESTAMP, nullable=True)  # Optional last used timestamp
