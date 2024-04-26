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

# Constants for JWT
SECRET_KEY = "secret-key"  # Keep this secret and secure in production
ALGORITHM = "HS256"  # Algorithm for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Data models for authentication and user management
class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str] = None

class UserInDB(User):
    hashed_password: str  # Store hashed password

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

class UpdateUser(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None

# Simulated database for demonstration purposes
users_db = {}

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = users_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = next((u for u in users_db.values() if u.user_id == user_id), None)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# POST /auth/register: Register a new user
@app.post("/auth/register", response_model=Token)
async def register_user(user: RegisterUser):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    if any(u.email == user.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already in use")
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user.password)
    users_db[user.username] = UserInDB(
        user_id=user_id,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    # Create an access token for the new user
    token_data = {"sub": user_id}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# POST /auth/login: Authenticate users and return a token
@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Create an access token upon successful login
    token_data = {"sub": user.user_id}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# GET /auth/user: Retrieve user profile information based on the token
@app.get("/auth/user", response_model=User)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# POST /auth/logout: Log out a user and invalidate the token
@app.post("/auth/logout")
async def logout():
    # In a real-world application, you'd need to implement token invalidation logic
    return {"status": "Logged out"}

# PUT /auth/user: Update user profile information
@app.put("/auth/user")
async def update_user_profile(update_data: UpdateUser, current_user: User = Depends(get_current_user)):
    # Update the user's profile information based on the provided data
    if update_data.full_name:
        current_user.full_name = update_data.full_name
    if update_data.email:
        if any(u.email == update_data.email for u in users_db.values() if u.user_id != current_user.user_id):
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = update_data.email
    return {"status": "User profile updated", "user": current_user}

# POST /auth/password-reset: Initiate password reset process
@app.post("/auth/password-reset")
async def password_reset(email: str = Body(...)):
    # In a real-world application, you'd send an email with reset instructions
    if not any(u.email == email for u in users_db.values()):
        raise HTTPException(status_code=404, detail="Email not found")
    return {"status": "Password reset instructions sent"}

# GET /auth/verify-email/{token}: Verify user's email address during registration
@app.get("/auth/verify-email/{token}")
async def verify_email(token: str):
    # In a real-world application, you'd verify the token and update the user's email verification status
    return {"status": "Email verified"}

# GET /auth/session-history/{userId}: Retrieve a user's login session history
@app.get("/auth/session-history/{userId}")
async def get_session_history(userId: int):
    # Example session history, in a real-world application, this would come from a database
    session_history = [
        {"userId": userId, "login_time": "2024-04-24T12:00:00", "logout_time": "2024-04-24T12:30:00"},
        {"userId": userId, "login_time": "2024-04-23T10:00:00", "logout_time": "2024-04-23T10:45:00"},
    ]
    if not session_history:
        raise HTTPException(status_code=404, detail="Session history not found")
    return session_history

# POST /auth/refresh-token: Issue a new token based on an existing session
@app.post("/auth/refresh-token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    # Create a new access token for an existing user session
    token_data = {"sub": current_user.user_id}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

#endregion
