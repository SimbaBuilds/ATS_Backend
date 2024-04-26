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

# Define data model for homework assignments
class Homework(BaseModel):
    id: int
    user_id: int
    assignment: str
    due_date: Optional[date]
    details: Optional[str]

# GET /homework/{userId}: Retrieve all homework assignments for a specific user
@app.get("/homework/{userId}")
def get_homework(
    userId: int = Path(..., description="Unique identifier for the user")
):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM homework_table WHERE user_id = %s", (userId,))
        results = cursor.fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail="No homework assignments found")
    
    homework = [{"id": r[0], "user_id": r[1], "assignment": r[2], "due_date": r[3], "details": r[4]} for r in results]
    
    return {"homework": homework}

# POST /homework: Assign new homework to a user or group
@app.post("/homework")
def assign_homework(homework: Homework):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO homework_table (user_id, assignment, due_date, details) VALUES (%s, %s, %s, %s) RETURNING id",
            (homework.user_id, homework.assignment, homework.due_date, homework.details)
        )
        new_id = cursor.fetchone()[0]
        connection.commit()
    
    return {"message": "Homework assigned", "homework_id": new_id}

# PUT /homework/{id}: Update details or deadlines of an existing homework assignment
@app.put("/homework/{id}")
def update_homework(
    id: int,
    updated_homework: Homework
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE homework_table SET assignment = %s, due_date = %s, details = %s WHERE id = %s",
            (updated_homework.assignment, updated_homework.due_date, updated_homework.details, id)
        )
        connection.commit()
    
    return {"message": "Homework updated"}

# DELETE /homework/{id}: Remove a homework assignment
@app.delete("/homework/{id}")
def delete_homework(
    id: int = Path(..., description="Unique identifier for the homework assignment")
):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM homework_table WHERE id = %s", (id,))
        connection.commit()
    
    return {"message": "Homework deleted"}

#endregion
