from fastapi import FastAPI, HTTPException, Depends, Body, Path
from sqlalchemy.orm import Session
from app.database.session import get_db  # Make sure this points correctly to your database session utility.
from app.models import User, Notification, Feedback  # Assuming User and other models are defined correctly in your models
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.is_dismissed == False).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found")
    return {"notifications": [dict(id=n.id, user_id=n.user_id, message=n.message, is_dismissed=n.is_dismissed, timestamp=n.timestamp) for n in notifications]}

@app.post("/feedback")
def submit_feedback(feedback: Feedback, db: Session = Depends(get_db)):
    new_feedback = Feedback(
        user_id=feedback.user_id,
        comment=feedback.comment,
        rating=feedback.rating,
        timestamp=datetime.now()
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return {"status": "Feedback submitted", "feedback_id": new_feedback.id}

@app.post("/notifications/dismiss/{id}")
def dismiss_notification(id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == id).first()
    if notification:
        notification.is_dismissed = True
        db.commit()
        return {"status": "Notification dismissed"}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")

@app.get("/notifications/history/{userId}")
def get_notification_history(userId: int, db: Session = Depends(get_db)):
    history = db.query(Notification).filter(Notification.user_id == userId).all()
    if not history:
        raise HTTPException(status_code=404, detail="No notifications found for this user")
    return {
        "user_id": userId,
        "history": [dict(id=n.id, user_id=n.user_id, message=n.message, is_dismissed=n.is_dismissed, timestamp=n.timestamp) for n in history]
    }

@app.put("/feedback/{id}")
def update_feedback(id: int, updated_feedback: Feedback, db: Session = Depends(get_db)):
    feedback = db.query(Feedback).filter(Feedback.id == id).first()
    if feedback:
        feedback.comment = updated_feedback.comment
        feedback.rating = updated_feedback.rating
        db.commit()
        return {"status": "Feedback updated"}
    else:
        raise HTTPException(status_code=404, detail="Feedback not found")

@app.post("/email/send")
def send_email(user_email: str = Body(...), subject: str = Body(...), message: str = Body(...)):
    smtp_server = "your_smtp_server"
    smtp_port = 587
    smtp_user = "your_smtp_user"
    smtp_pass = "your_smtp_password"

    email_message = MIMEText(message)
    email_message["Subject"] = subject
    email_message["From"] = smtp_user
    email_message["To"] = user_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, user_email, email_message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")    

    return {"status": "Email sent"}

