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

# Data model for a curriculum plan
class CurriculumPlan(BaseModel):
    user_id: int
    plan_name: str
    subjects: List[str]  # List of subjects or topics in the study plan
    description: Optional[str] = None  # Optional description of the study plan

# GET /curriculum/{userId}: Fetch the personalized study plan for a specific user
@app.get("/curriculum/{userId}")
def get_curriculum(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM curriculum_plans WHERE user_id = %s", (userId,))
        plans = cursor.fetchall()
    
    if not plans:
        raise HTTPException(status_code=404, detail="No curriculum plans found for this user")
    
    return {"user_id": userId, "curriculum_plans": plans}

# POST /curriculum: Create a new curriculum plan for a user or a group
@app.post("/curriculum")
def create_curriculum(plan: CurriculumPlan):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO curriculum_plans (user_id, plan_name, subjects, description) VALUES (%s, %s, %s, %s) RETURNING id",
            (plan.user_id, plan.plan_name, json.dumps(plan.subjects), plan.description)
        )
        connection.commit()
        new_plan_id = cursor.fetchone()[0]
    
    return {"status": "Curriculum plan created", "plan_id": new_plan_id}

# PUT /curriculum/{id}: Update an existing study plan
@app.put("/curriculum/{id}")
def update_curriculum(
    id: int,
    updated_plan: CurriculumPlan
):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE curriculum_plans SET plan_name = %s, subjects = %s, description = %s WHERE id = %s",
            (updated_plan.plan_name, json.dumps(updated_plan.subjects), updated_plan.description, id)
        )
        connection.commit()
    
    return {"status": "Curriculum plan updated"}

# DELETE /curriculum/{id}: Delete a study plan
@app.delete("/curriculum/{id}")
def delete_curriculum(id: int):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM curriculum_plans WHERE id = %s", (id,))
        connection.commit()
    
    return {"status": "Curriculum plan deleted"}

#endregion
