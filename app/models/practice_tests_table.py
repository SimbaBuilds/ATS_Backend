from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database.base import Base


# Practice test table for storing practice test data
class PracticeTestsTable(Base):
    __tablename__ = "practice_tests_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    test = Column(String(255), nullable=False)  # Name of the practice test
    content = Column(JSONB, nullable=False)  # JSON content for the practice test
