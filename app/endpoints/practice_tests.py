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

# Define data models for tests and test attempts
class Test(BaseModel):
    id: int
    test_name: str
    questions: Dict[str, Any]  # The test content (e.g., questions)

class TestAttempt(BaseModel):
    attempt_id: int
    test_id: int
    user_id: int
    status: str  # "started", "in_progress", or "completed"
    responses: Dict[str, Any]  # User's responses to questions

# GET /test/{id}: Get details about a specific quiz or test
@app.get("/test/{id}")
def get_test(
    id: int = Path(..., description="Unique identifier for the test")
):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM practice_tests_table WHERE id = %s", (id,))
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Test not found")
    
    test = {
        "id": result[0],
        "test_name": result[1],
        "content": result[2]
    }
    
    return {"test": test}

# POST /test: Create a new quiz or test (admin or teacher access)
@app.post("/test")
def create_test(test: Test):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO practice_tests_table (test_name, content) VALUES (%s, %s) RETURNING id",
            (test.test_name, json.dumps(test.questions))
        )
        new_id = cursor.fetchone()[0]
        connection.commit()
    
    return {"message": "Test created", "id": new_id}

# PUT /test/{id}: Update an existing quiz or test (admin or teacher access)
@app.put("/test/{id}")
def update_test(
    id: int,
    updated_test: Test
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE practice_tests_table SET test_name = %s, content = %s WHERE id = %s",
            (updated_test.test_name, json.dumps(updated_test.questions), id)
        )
        connection.commit()
    
    return {"message": "Test updated"}

# DELETE /test/{id}: Delete a quiz or test (admin or teacher access)
@app.delete("/test/{id}")
def delete_test(
    id: int
):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM practice_tests_table WHERE id = %s", (id,))
        connection.commit()
    
    return {"message": "Test deleted"}

# POST /test/attempt/{id}: Start or continue a test attempt
@app.post("/test/attempt/{id}")
def start_test_attempt(
    id: int,
    attempt_data: TestAttempt
):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO test_attempts_table (test_id, user_id, status, responses) VALUES (%s, %s, %s, %s) RETURNING attempt_id",
            (id, attempt_data.user_id, attempt_data.status, json.dumps(attempt_data.responses))
        )
        new_id = cursor.fetchone()[0]
        connection.commit()
    
    return {"message": "Test attempt started", "attempt_id": new_id}

# GET /test/score/{attempt_id}: Retrieve the score and feedback for a completed test attempt
@app.get("/test/score/{attempt_id}")
def get_test_score(
    attempt_id: int
):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM test_attempts_table WHERE attempt_id = %s AND status = 'completed'",
            (attempt_id,)
        )
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Test attempt not completed or not found")
    
    score = {"attempt_id": result[0], "score": result[3], "feedback": result[4]}  # Customize fields as needed
    
    return {"score": score}

# GET /test/summary/{id}: Get a summary of test results, including average scores and common weak areas
@app.get("/test/summary/{id}")
def get_test_summary(
    id: int = Path(..., description="Unique identifier for the test")
):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT AVG(score), COUNT(*) FROM test_attempts_table WHERE test_id = %s",
            (id,)
        )
        result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Test summary not found")
    
    summary = {
        "average_score": result[0],
        "attempt_count": result[1],
        "common_weak_areas": ["Example Area 1", "Example Area 2"]  # Placeholder, customize as needed
    }
    
    return {"summary": summary}

#endregion
