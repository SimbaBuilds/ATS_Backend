from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database.base import Base
from sqlalchemy import ForeignKey

class CurriculumPlan(Base):
    __tablename__ = "curriculum_plans"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # Primary key with auto-increment
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the "users" table
    plan_name = Column(String(255), nullable=False)  # Name of the curriculum plan
    subjects = Column(JSONB, nullable=False)  # Subjects or topics in the plan, stored as JSON
    description = Column(Text, nullable=True)  # Optional description
    created_at = Column(TIMESTAMP, server_default=func.now())  # When the plan was created
