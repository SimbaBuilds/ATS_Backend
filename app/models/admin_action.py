from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database.base import Base


# Model for logging administrative actions
class AdminActionsTable(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    action_type = Column(String(255), nullable=False)  # Type of admin action (e.g., 'delete', 'update')
    user_id = Column(Integer, nullable=True, index=True)  # Optional ID of the user associated with the action
    details = Column(String(255), nullable=True)  # Optional details about the action
    timestamp = Column(TIMESTAMP, server_default=func.now())  # Timestamp of the admin action
