
from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database.session import get_db
from app.models import User
from app.schemas import UserResponse, AddUserResponse, UserLoginResponse, UpdateUserInput, UpdateUserResponse
from passlib.context import CryptContext
from jose import jwt
from app.utils.auth_utils import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, hash_password  #utility functions for these tasks


router = APIRouter()

# Get all users
@router.get("/users", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

# Get a specific user by ID
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/auth/register_user", response_model=AddUserResponse)
async def register_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_password = hash_password(password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# User login endpoint
@router.post("/auth/login", response_model=UserLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create a new token
    token_data = {"sub": user.id}
    access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/users/{user_id}", response_model=UpdateUserResponse)
async def update_user(user_id: int, update_data: UpdateUserInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = update_data.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


# Delete a user
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}
