
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models import SessionSummary, Reminder, KnowledgeUpdate, UserSettings

router = APIRouter()

# Update the chatbot's knowledge base with new information
@router.put("/chat/update-knowledge/{topicId}")
async def update_knowledge(topicId: int, new_information: str, db: Session = Depends(get_db)):
    knowledge_update = db.query(KnowledgeUpdate).filter(KnowledgeUpdate.topic_id == topicId).first()
    if not knowledge_update:
        knowledge_update = KnowledgeUpdate(topic_id=topicId, new_information=new_information)
        db.add(knowledge_update)
    else:
        knowledge_update.new_information = new_information
    
    db.commit()
    db.refresh(knowledge_update)
    return {"status": "Knowledge updated", "topic_id": topicId, "new_information": new_information}

# Personalize chatbot responses based on user preferences
@router.post("/chat/personalize")
async def personalize_chat(user_id: int, preference: str, db: Session = Depends(get_db)):
    user_setting = db.query(UserSettings).filter(UserSettings.user_id == user_id, UserSettings.setting_type == "personalization").first()
    if not user_setting:
        user_setting = UserSettings(user_id=user_id, setting=preference, setting_type="personalization")
        db.add(user_setting)
    else:
        user_setting.setting = preference
    
    db.commit()
    db.refresh(user_setting)
    return {"status": "Chat personalized", "user_id": user_id, "preference": preference}

# Generate a session summary with key points
@router.post("/chat/session-summary")
async def generate_session_summary(chat_id: int, highlights: List[str], db: Session = Depends(get_db)):
    session_summary = SessionSummary(chat_id=chat_id, highlights=highlights)
    db.add(session_summary)
    db.commit()
    db.refresh(session_summary)
    return {"status": "Session summary generated", "chat_id": chat_id, "highlights": highlights}

# Set a reminder for a user with a specific message
@router.post("/chat/set-reminder")
async def set_reminder(user_id: int, reminder_time: str, message: str, db: Session = Depends(get_db)):
    reminder = Reminder(user_id=user_id, reminder_time=reminder_time, message=message)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return {"status": "Reminder set", "user_id": user_id, "message": message}

# Update user settings based on preference
@router.put("/chat/user-settings/{user_id}")
async def update_user_settings(user_id: int, setting: str, setting_type: str, db: Session = Depends(get_db)):
    user_setting = db.query(UserSettings).filter(UserSettings.user_id == user_id, UserSettings.setting_type == setting_type).first()
    if not user_setting:
        user_setting = UserSettings(user_id=user_id, setting=setting, setting_type=setting_type)
        db.add(user_setting)
    else:
        user_setting.setting = setting
    
    db.commit()
    db.refresh(user_setting)
    return {"status": "User setting updated", "user_id": user_id, "setting": setting, "setting_type": setting_type}

# Retrieve user settings based on user ID
@router.get("/chat/user-settings/{user_id}")
async def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).all()
    if not user_settings:
        raise HTTPException(status_code=404, detail="No user settings found")
    
    return user_settings
