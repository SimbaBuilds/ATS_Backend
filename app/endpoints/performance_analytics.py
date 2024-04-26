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

# Data model for performance analytics
class PerformanceAnalytics(BaseModel):
    subject: str
    average_score: float  # Average score across users for this subject
    completion_rate: float  # Completion rate (e.g., % of users who completed all questions)
    difficulty_level: Optional[str] = None  # Could be used to categorize by difficulty

# GET /analytics/performance: Get analytics on user performance across different subjects and difficulty levels
@app.get("/analytics/performance")
def get_performance_analytics():
    with connection.cursor() as cursor:
        # Example query to calculate average score and completion rate for each subject
        cursor.execute(
            """
            SELECT
                subject,
                AVG(score) AS average_score,
                COUNT(score) / (SELECT COUNT(*) FROM questions WHERE subject = subject) * 100 AS completion_rate,
                difficulty_level
            FROM
                user_progress
            GROUP BY
                subject, difficulty_level
            """
        )
        analytics_data = cursor.fetchall()
    
    if not analytics_data:
        raise HTTPException(status_code=404, detail="No performance analytics data found")
    
    # Transform the raw data into a structured format
    performance_analytics = [
        PerformanceAnalytics(
            subject=row[0],
            average_score=row[1],
            completion_rate=row[2],
            difficulty_level=row[3]
        )
        for row in analytics_data
    ]
    
    return {"performance_analytics": performance_analytics}

# Data model for usage analytics
class UsageAnalytics(BaseModel):
    feature_name: str
    usage_count: int  # Number of times a feature or part of the service is used
    last_used: Optional[datetime.datetime]  # Optional timestamp of last usage

# GET /analytics/usage: Obtain statistics on how often different parts of the service are used
@app.get("/analytics/usage")
def get_usage_analytics():
    with connection.cursor() as cursor:
        # Example query to count usage of different features
        cursor.execute(
            """
            SELECT
                feature_name,
                COUNT(*) AS usage_count,
                MAX(timestamp) AS last_used
            FROM
                usage_logs  # Assuming you have a table tracking feature usage
            GROUP BY
                feature_name
            """
        )
        usage_data = cursor.fetchall()
    
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage analytics data found")
    
    # Transform the raw data into a structured format
    usage_analytics = [
        UsageAnalytics(
            feature_name=row[0],
            usage_count=row[1],
            last_used=row[2]
        )
        for row in usage_data
    ]
    
    return {"usage_analytics": usage_analytics}

#endregion
