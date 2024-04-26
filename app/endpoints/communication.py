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

# Data model for notifications
class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    is_dismissed: bool = False  # Whether the notification has been dismissed
    timestamp: Optional[datetime.datetime] = None

# Data model for feedback
class Feedback(BaseModel):
    user_id: int
    comment: str
    rating: Optional[int] = None  # Optional rating for feedback
    timestamp: Optional[datetime.datetime] = None

# GET /notifications: Retrieve notifications for a user
@app.get("/notifications")
def get_notifications():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM notifications WHERE is_dismissed = false")
        notifications = cursor.fetchall()
    
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found")
    
    return {
        "notifications": [
            {
                "id": row[0],
                "user_id": row[1],
                "message": row[2],
                "is_dismissed": row[3],
                "timestamp": row[4]
            }
            for row in notifications
        ]
    }

# POST /feedback: Submit feedback about the service or specific content
@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    feedback.timestamp = datetime.datetime.now()  # Record when the feedback was submitted
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO feedback (user_id, comment, rating, timestamp) VALUES (%s, %s, %s, %s) RETURNING id",
            (feedback.user_id, feedback.comment, feedback.rating, feedback.timestamp)
        )
        connection.commit()
        new_feedback_id = cursor.fetchone()[0]
    
    return {"status": "Feedback submitted", "feedback_id": new_feedback_id}

# POST /notifications/dismiss/{id}: Dismiss a specific notification
@app.post("/notifications/dismiss/{id}")
def dismiss_notification(id: int):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE notifications SET is_dismissed = true WHERE id = %s", (id,))
        connection.commit()
    
    return {"status": "Notification dismissed"}

# GET /notifications/history/{userId}: Retrieve history of all notifications for a user
@app.get("/notifications/history/{userId}")
def get_notification_history(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s", (userId,))
        history = cursor.fetchall()
    
    if not history:
        raise HTTPException(status_code=404, detail="No notifications found for this user")
    
    return {
        "user_id": userId,
        "history": [
            {
                "id": row[0],
                "user_id": row[1],
                "message": row[2],
                "is_dismissed": row[3],
                "timestamp": row[4]
            }
            for row in history
        ]
    }

# PUT /feedback/{id}: Update a previously submitted feedback entry
@app.put("/feedback/{id}")
def update_feedback(id: int, updated_feedback: Feedback):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE feedback SET comment = %s, rating = %s WHERE id = %s",
            (updated_feedback.comment, updated_feedback.rating, id)
        )
        connection.commit()
    
    return {"status": "Feedback updated"}

# POST /email/send: Send an email to a user, particularly useful for updates, reminders, or promotional content
@app.post("/email/send")
def send_email(user_email: str = Body(...), subject: str = Body(...), message: str = Body(...)):
    # Example email configuration (ensure SMTP server and credentials are correct)
    smtp_server = "your_smtp_server"
    smtp_port = 587
    smtp_user = "your_smtp_user"
    smtp_pass = "your_smtp_password"
    
    # Create email
    email_message = MIMEText(message)
    email_message["Subject"] = subject
    email_message["From"] = smtp_user
    email_message["To"] = user_email
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, user_email, email_message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    return {"status": "Email sent"}

#endregion
