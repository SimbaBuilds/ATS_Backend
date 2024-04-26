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

# Data model for answer submissions
class Answer(BaseModel):
    user_id: int
    quiz_id: int
    question_id: int
    answer: str
    correct: bool  # True if the answer is correct, False otherwise
    timestamp: Optional[datetime.datetime] = None

# POST /answers: Submit answers for a quiz or practice test
@app.post("/answers")
def submit_answer(answer: Answer):
    answer.timestamp = datetime.datetime.now()  # Record the submission time
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO answers (user_id, quiz_id, question_id, answer, correct, timestamp) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (answer.user_id, answer.quiz_id, answer.question_id, answer.answer, answer.correct, answer.timestamp)
        )
        connection.commit()
        new_answer_id = cursor.fetchone()[0]
    
    return {"status": "Answer submitted", "answer_id": new_answer_id}

# GET /answers/user/{userId}: Retrieve all submissions by a specific user
@app.get("/answers/user/{userId}")
def get_user_answers(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM answers WHERE user_id = %s", (userId,))
        user_answers = cursor.fetchall()
    
    if not user_answers:
        raise HTTPException(status_code=404, detail="No answers found for this user")
    
    return {"user_id": userId, "answers": user_answers}

# GET /answers/quiz/{quizId}: Retrieve all answers for a specific quiz
@app.get("/answers/quiz/{quizId}")
def get_quiz_answers(quizId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM answers WHERE quiz_id = %s", (quizId,))
        quiz_answers = cursor.fetchall()
    
    if not quiz_answers:
        raise HTTPException(status_code=404, detail="No answers found for this quiz")
    
    return {"quiz_id": quizId, "answers": quiz_answers}

# GET /answers/{id}: Get details of a specific answer submission
@app.get("/answers/{id}")
def get_answer_details(id: str):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM answers WHERE id = %s", (id,))
        answer = cursor.fetchone()
    
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    return {"answer": answer}

#endregion
