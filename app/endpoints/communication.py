from fastapi import FastAPI, HTTPException, Depends, Body, Path
from sqlalchemy.orm import Session
from app.database.session import get_db  # Make sure this points correctly to your database session utility.
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter
from app.models import Feedback, Notification
from app.schemas import GetNotificationsResponse, SubmitFeedbackResponse, DismissNotificationResponse, FeedbackModel, GetNotificationHistoryResponse, SendEmailResponse

router = APIRouter()


@router.get("/notifications", response_model=GetNotificationsResponse)
async def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.is_dismissed == False).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found")
    return notifications

@router.post("/feedback", response_model=SubmitFeedbackResponse)
async def submit_feedback(feedback: FeedbackModel, db: Session = Depends(get_db)):
    new_feedback = Feedback(
        user_id=feedback.user_id,
        comment=feedback.comment,
        rating=feedback.rating,
        timestamp=datetime.now()
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return SubmitFeedbackResponse(status="Feedback submitted", feedback_id=new_feedback.id)

@router.post("/notifications/dismiss/{id}", response_model=DismissNotificationResponse)
async def dismiss_notification(id: int, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_dismissed = True
    db.commit()
    return DismissNotificationResponse(status="Notification dismissed")


@router.get("/notifications/history/{userId}", response_model=GetNotificationHistoryResponse)
async def get_notification_history(userId: int, db: Session = Depends(get_db)):
    history = db.query(Notification).filter(Notification.user_id == userId).all()
    if not history:
        raise HTTPException(status_code=404, detail="No notifications found for this user")
    return GetNotificationHistoryResponse(user_id=userId, history=history)

@router.post("/email/send", response_model=SendEmailResponse)
async def send_email(user_email: str = Body(...), subject: str = Body(...), message: str = Body(...)):
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

    return SendEmailResponse(status="Email sent")

