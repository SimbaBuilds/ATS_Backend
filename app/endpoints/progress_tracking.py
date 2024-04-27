
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID 
from app.models import UserProgress  # Assumed path to your SQLAlchemy model
from app.database.session import get_db  # Assumed path to your database session

router = APIRouter()


@app.get("/users", response_model=List[UserProgressBase])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserProgress).all()

@app.get("/progress/user/{userId}", response_model=List[UserProgressBase])
def get_user_progress(userId: int, db: Session = Depends(get_db)):
    progress_data = db.query(UserProgress).filter(UserProgress.user_id == userId).order_by(UserProgress.timestamp.asc()).all()
    if not progress_data:
        raise HTTPException(status_code=404, detail="No progress data found for this user")
    return progress_data

@app.post("/progress", response_model=UserProgressBase)
def record_progress(progress: UserProgressBase, db: Session = Depends(get_db)):
    new_progress = UserProgress(
        user_id=progress.user_id,
        quiz_id=progress.quiz_id,
        score=progress.score,
        timestamp=datetime.now(),
        session_id=progress.session_id
    )
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    return new_progress

@app.get("/progress/session/{sessionId}", response_model=List[UserProgressBase])
def get_session_progress(sessionId: UUID, db: Session = Depends(get_db)):
    session_progress = db.query(UserProgress).filter(UserProgress.session_id == sessionId).all()
    if not session_progress:
        raise HTTPException(status_code=404, detail="No progress data found for this session")
    return session_progress


