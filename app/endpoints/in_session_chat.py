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



#IN SESSION CHAT ENDPOINTS
#region
# Data model for POST /chat/message
class Message(BaseModel):
    user_id: int
    content: str

# Data model for POST /chat/feedback
class Feedback(BaseModel):
    user_id: int
    rating: int  # Example feedback, could be a rating out of 5
    comment: str

# Data model for user messages
class UserMessage(BaseModel):
    user_id: int
    content: str  # Message sent by the user

# Data model for chatbot responses
class ChatbotResponse(BaseModel):
    user_id: int
    response: str  # The chatbot's response message

# Endpoint for handling user messages and returning chatbot responses
@app.post("/chat/respond")
async def chatbot_respond(message: UserMessage):
    # Basic logic for generating a chatbot response
    # In a real-world scenario, this could involve complex chatbot logic or an external service
    response_content = f"Received your message: {message.content}"
    chatbot_response = ChatbotResponse(user_id=message.user_id, response=response_content)
    return chatbot_response


# POST /vision/analyze: Accepts file uploads
@app.post("/vision/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Simulate processing the uploaded file (e.g., image analysis)
    return {"filename": file.filename, "status": "Processed"}

# POST /chat/message: Accepts user messages for the chatbot
@app.post("/chat/message")
async def chat_message(message: Message):
    # Simulate processing the chat message (e.g., sending to a chatbot)
    return {"status": "Message received", "content": message.content}

# GET /chat/history/{userId}: Retrieves chat history for a specific user
@app.get("/chat/history/{userId}")
async def chat_history(userId: int):
    # Simulate fetching chat history (e.g., from a database)
    chat_history = [
        {"userId": userId, "message": "Hello!"},
        {"userId": userId, "message": "How can I help you?"},
    ]
    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return chat_history

# POST /chat/feedback: Accepts user feedback
@app.post("/chat/feedback")
async def submit_feedback(feedback: Feedback):
    # Simulate storing feedback for future analysis or improvement
    return {"status": "Feedback received", "rating": feedback.rating, "comment": feedback.comment}

#endregion
