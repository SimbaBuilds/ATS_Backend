from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy import ForeignKey

class Homework(Base):
    __tablename__ = "homework_table"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to the "users" table
    assignment = Column(String(255), nullable=False)  # Homework assignment description
    due_date = Column(Date, nullable=True)  # Due date for the homework
    details = Column(Text, nullable=True)  # Additional details for the assignment
