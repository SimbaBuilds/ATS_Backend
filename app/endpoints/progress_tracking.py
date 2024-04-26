from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body, Path
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import uuid
import psycopg2
import json
from datetime import date, datetime
import smtplib  
from email.mime.text import MIMEText


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User  # Example model

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


#region

# Data model for progress tracking
class UserProgress(BaseModel):
    user_id: int
    quiz_id: int
    score: int  # Could represent a percentage or total score
    timestamp: Optional[datetime.datetime] = None
    session_id: Optional[str] = None  # Session ID for grouping related activities

# GET /progress/user/{userId}: Track the learning progress of a user over time
@app.get("/progress/user/{userId}")
def get_user_progress(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_progress WHERE user_id = %s ORDER BY timestamp ASC", (userId,))
        progress_data = cursor.fetchall()
    
    if not progress_data:
        raise HTTPException(status_code=404, detail="No progress data found for this user")
    
    return {
        "user_id": userId,
        "progress": progress_data
    }

# POST /progress: Update progress data after each quiz or test attempt
@app.post("/progress")
def record_progress(progress: UserProgress):
    progress.timestamp = datetime.datetime.now()  # Record when the progress data was created
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO user_progress (user_id, quiz_id, score, timestamp, session_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (progress.user_id, progress.quiz_id, progress.score, progress.timestamp, progress.session_id)
        )
        connection.commit()
        new_progress_id = cursor.fetchone()[0]
    
    return {
        "status": "Progress recorded",
        "progress_id": new_progress_id
    }

# GET /progress/session/{sessionId}: Retrieve progress details for a specific learning session
@app.get("/progress/session/{sessionId}")
def get_session_progress(sessionId: str):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_progress WHERE session_id = %s", (sessionId,))
        session_progress = cursor.fetchall()
    
    if not session_progress:
        raise HTTPException(status_code=404, detail="No progress data found for this session")
    
    return {
        "session_id": sessionId,
        "progress": session_progress
    }

#endregion
