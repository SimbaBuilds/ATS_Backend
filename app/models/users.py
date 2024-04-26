from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    access_token = Column(String(255), nullable=True)  
    token_type = Column(String(255), nullable=True)  
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Hashed password
    full_name = Column(String(255), nullable=True)  # Optional full name
    created_at = Column(TIMESTAMP, server_default=func.now())  # Timestamp when the user was created
    updated_at = Column(TIMESTAMP, onupdate=func.now())  # Updated when user information changes
    role = Column(String(50), nullable=True)  # Optional role (e.g., student, tutor)
    status = Column(Boolean, default=True)  # Active or suspended
    profile_picture = Column(String(255), nullable=True)  # Reference to the profile picture
    additional_info = Column(JSONB, nullable=True)  # Store additional user-related data
