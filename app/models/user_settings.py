from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.base import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the user table
    setting = Column(String(255), nullable=False)  # The specific user setting
    setting_type = Column(String(50), nullable=False)  # A type to differentiate between personalization and other settings
