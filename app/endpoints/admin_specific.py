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
# Example admin authentication dependency
def admin_auth():
    # This is a simple placeholder; implement proper authentication logic here
    # Raise an exception if the user is not authorized
    pass

# Data model for user information
class User(BaseModel):
    id: int
    name: str
    email: str
    role: str  # User role, e.g., 'user', 'admin'
    created_at: Optional[datetime.datetime] = None

# Data model for admin actions
class AdminAction(BaseModel):
    action_type: str  # Type of action, e.g., 'delete', 'update'
    user_id: Optional[int]  # User ID associated with the action
    details: Optional[str] = None  # Additional details or comments
    timestamp: Optional[datetime.datetime] = None

# GET /admin/users: List all users (admin access)
@app.get("/admin/users", dependencies=[Depends(admin_auth)])
def list_users():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    
    return {
        "users": [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "role": row[3],
                "created_at": row[4]
            }
            for row in users
        ]
    }

# GET /admin/reports: Generate reports on user engagement and performance (admin access)
@app.get("/admin/reports", dependencies=[Depends(admin_auth)])
def generate_reports():
    # This is a basic example; adjust to meet your reporting needs
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_users,
                AVG(score) AS average_score,
                MAX(score) AS highest_score,
                MIN(score) AS lowest_score
            FROM
                user_progress
            """
        )
        report = cursor.fetchone()
    
    return {
        "total_users": report[0],
        "average_score": report[1],
        "highest_score": report[2],
        "lowest_score": report[3]
    }

# PUT /admin/users/{userId}: Update details for a specific user (admin access)
@app.put("/admin/users/{userId}", dependencies=[Depends(admin_auth)])
def update_user(userId: int, updated_user: User):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET name = %s, email = %s, role = %s WHERE id = %s",
            (updated_user.name, updated_user.email, updated_user.role, userId)
        )
        connection.commit()
    
    return {"status": "User details updated"}

# POST /admin/actions: Log and manage administrative actions taken on the platform (admin access)
@app.post("/admin/actions", dependencies=[Depends(admin_auth)])
def log_admin_action(admin_action: AdminAction):
    admin_action.timestamp = datetime.datetime.now()  # Record the action timestamp
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO admin_actions (action_type, user_id, details, timestamp) VALUES (%s, %s, %s, %s) RETURNING id",
            (admin_action.action_type, admin_action.user_id, admin_action.details, admin_action.timestamp)
        )
        connection.commit()
        new_action_id = cursor.fetchone()[0]
    
    return {"status": "Admin action logged", "action_id": new_action_id}

# DELETE /admin/users/{userId}: Remove a user from the platform (admin access)
@app.delete("/admin/users/{userId}", dependencies=[Depends(admin_auth)])
def delete_user(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (userId,))
        connection.commit()
    
    return {"status": "User removed from platform"}

#endregion
