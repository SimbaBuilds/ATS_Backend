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

# Define data models for questions and practice tests
class Question(BaseModel):
    id: int
    topic: str
    sub_topic: Optional[str]
    content: Dict[str, Any]  # JSONB field for question content

class PracticeTest(BaseModel):
    id: int
    test: str
    content: Dict[str, Any]  # JSONB field for test content

# CRUD operations for `question_bank_table`
# GET /questions/{question_id}: Retrieve a specific question from question_bank_table
@app.get("/questions/{question_id}")
def get_question(
    question_id: int = Path(..., description="Unique identifier for the question")
):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM question_bank_table WHERE id = %s", (question_id,))
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = {
        "id": result[0],
        "topic": result[1],
        "sub_topic": result[2],
        "content": result[3]
    }
    
    return {"question": question}

# PUT /questions/{question_id}: Update a question in question_bank_table
@app.put("/questions/{question_id}")
def update_question(
    question_id: int,
    updated_question: Question
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE question_bank_table SET topic = %s, sub_topic = %s, content = %s WHERE id = %s",
            (updated_question.topic, updated_question.sub_topic, updated_question.content, question_id)
        )
        connection.commit()
    
    return {"message": "Question updated"}

# DELETE /questions/{question_id}: Delete a question from question_bank_table
@app.delete("/questions/{question_id}")
def delete_question(
    question_id: int
):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM question_bank_table WHERE id = %s", (question_id,))
        connection.commit()
    
    return {"message": "Question deleted"}

# CRUD operations for `practice_tests_table`
# GET /practice_tests/{test_id}: Retrieve a specific practice test by ID
@app.get("/practice_tests/{test_id}")
def get_practice_test(
    test_id: int = Path(..., description="Unique identifier for the practice test")
):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM practice_tests_table WHERE id = %s", (test_id,))
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Practice test not found")
    
    practice_test = {
        "id": result[0],
        "test": result[1],
        "content": result[2]
    }
    
    return {"practice_test": practice_test}

# PUT /practice_tests/{test_id}: Update a specific practice test
@app.put("/practice_tests/{test_id}")
def update_practice_test(
    test_id: int,
    updated_practice_test: PracticeTest
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE practice_tests_table SET test = %s, content = %s WHERE id = %s",
            (updated_practice_test.test, updated_practice_test.content, test_id)
        )
        connection.commit()
    
    return {"message": "Practice test updated"}

# DELETE /practice_tests/{test_id}: Delete a specific practice test
@app.delete("/practice_tests/{test_id}")
def delete_practice_test(
    test_id: int
):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM practice_tests_table WHERE id = %s", (test_id,))
        connection.commit()
    
    return {"message": "Practice test deleted"}

# GET /practice_tests/{test_id}/questions/{question_key}: Retrieve a specific question within a practice test
@app.get("/practice_tests/{test_id}/questions/{question_key}")
def get_practice_test_question(
    test_id: int,
    question_key: str
):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT content->%s FROM practice_tests_table WHERE id = %s",
            (question_key, test_id)
        )
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {"question": result[0]}

# POST /practice_tests/{test_id}/questions: Add a new question to a practice test
@app.post("/practice_tests/{test_id}/questions")
def add_practice_test_question(
    test_id: int,
    new_question: Dict[str, Any]
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE practice_tests_table SET content = jsonb_set(content, %s, %s, true) WHERE id = %s",
            ("{" + new_question["key"] + "}", json.dumps(new_question["value"]), test_id)
        )
        connection.commit()
    
    return {"message": "Question added"}

# PUT /practice_tests/{test_id}/questions/{question_key}: Update a specific question in a practice test
@app.put("/practice_tests/{test_id}/questions/{question_key}")
def update_practice_test_question(
    test_id: int,
    question_key: str,
    updated_question: Dict[str, Any]
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE practice_tests_table SET content = jsonb_set(content, %s, %s, true) WHERE id = %s",
            ("{" + question_key + "}", json.dumps(updated_question), test_id)
        )
        connection.commit()
    
    return {"message": "Question updated"}

# DELETE /practice_tests/{test_id}/questions/{question_key}: Delete a specific question from a practice test
@app.delete("/practice_tests/{test_id}/questions/{question_key}")
def delete_practice_test_question(
    test_id: int,
    question_key: str
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE practice_tests_table SET content = content - %s WHERE id = %s",
            (question_key, test_id)
        )
        connection.commit()
    
    return {"message": "Question deleted"}

#endregion
