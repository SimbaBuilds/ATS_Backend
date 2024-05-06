
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models import SessionSummary, Reminder, KnowledgeUpdate, UserSettings
from app.schemas import UpdateKnowledgeResponse, PersonalizeChatResponse, SessionSummaryResponse, SetReminderResponse, GetUserSettingResponse


router = APIRouter()

@router.put("/chat/update-knowledge/{topicId}", response_model=UpdateKnowledgeResponse)
async def update_knowledge(topicId: int, new_information: str, db: Session = Depends(get_db)):
    knowledge_update = db.query(KnowledgeUpdate).filter(KnowledgeUpdate.topic_id == topicId).first()
    if not knowledge_update:
        knowledge_update = KnowledgeUpdate(topic_id=topicId, new_information=new_information)
        db.add(knowledge_update)
    else:
        knowledge_update.new_information = new_information

    db.commit()
    db.refresh(knowledge_update)
    return UpdateKnowledgeResponse(status="Knowledge updated", topic_id=topicId, new_information=new_information)


@router.post("/chat/personalize", response_model=PersonalizeChatResponse)
async def personalize_chat(user_id: int, preference: str, db: Session = Depends(get_db)):
    user_setting = db.query(UserSettings).filter(
        UserSettings.user_id == user_id, 
        UserSettings.setting_type == "personalization"
    ).first()

    if not user_setting:
        user_setting = UserSettings(user_id=user_id, setting=preference, setting_type="personalization")
        db.add(user_setting)
    else:
        user_setting.setting = preference
    
    db.commit()
    db.refresh(user_setting)
    return PersonalizeChatResponse(status="Chat personalized", user_id=user_id, preference=preference)



@router.post("/chat/session-summary", response_model=SessionSummaryResponse)
async def generate_session_summary(chat_id: int, highlights: List[str], db: Session = Depends(get_db)):
    session_summary = SessionSummary(chat_id=chat_id, highlights=highlights)
    db.add(session_summary)
    db.commit()
    db.refresh(session_summary)
    return SessionSummaryResponse(status="Session summary generated", chat_id=chat_id, highlights=highlights)



@router.post("/chat/set-reminder", response_model=SetReminderResponse)
async def set_reminder(user_id: int, reminder_time: str, message: str, db: Session = Depends(get_db)):
    try:
        reminder = Reminder(user_id=user_id, reminder_time=reminder_time, message=message)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    return SetReminderResponse(status="Reminder set", user_id=user_id, message=message)




@router.get("/chat/user-settings/{user_id}", response_model=List[GetUserSettingResponse])
async def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).all()
    if not user_settings:
        raise HTTPException(status_code=404, detail="No user settings found")
    
    return user_settings