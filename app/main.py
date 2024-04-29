from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import uuid
import psycopg2
from datetime import date, datetime
import smtplib  # For sending emails  
from email.mime.text import MIMEText


#probably don't need above in this module
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Body, Path
from app.endpoints import admin_specific, analytics, answers_and_scoring, auth_user_mgmt, chatbot_manipulation, communication, curriculum_and_study_plans, homework, in_session_chat, practice_tests, progress_tracking, question_mgmt
from app.database.session import get_db


app = FastAPI()


#include endpoints via router
#region
app.include_router(admin_specific.router, dependencies=[Depends(get_db)])
app.include_router(answers_and_scoring.router, dependencies=[Depends(get_db)])
app.include_router(auth_user_mgmt.router, dependencies=[Depends(get_db)])
app.include_router(chatbot_manipulation.router, dependencies=[Depends(get_db)])
app.include_router(communication.router, dependencies=[Depends(get_db)])
app.include_router(curriculum_and_study_plans.router, dependencies=[Depends(get_db)])
app.include_router(homework.router, dependencies=[Depends(get_db)])
app.include_router(in_session_chat.router, dependencies=[Depends(get_db)])
app.include_router(analytics.router, dependencies=[Depends(get_db)])
app.include_router(practice_tests.router, dependencies=[Depends(get_db)])
app.include_router(progress_tracking.router, dependencies=[Depends(get_db)])
app.include_router(question_mgmt.router, dependencies=[Depends(get_db)])
#endregion


# Connect to PostgreSQL database
connection = psycopg2.connect(
    dbname="question_bank_and_practice_tests",
    user="cameronhightower",
    password="Wellpleased22!",
    host="localhost",
    port="5432"
)

#FASTAPI DEMO
#region
# # This is your existing endpoint (route is to home page)
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# # Adding a new endpoint with a path parameter
# @app.get("/hello/{name}")  # Now, the URL can include a name
# def greet(name: str):  # 'name' is the path parameter
#     return {"Hello": name}  # Returns a personalized greeting

# # Adding an endpoint with a query parameter
# @app.get("/search")
# def search(query: Optional[str] = None):  # 'query' is optional
#     if query:
#         return {"result": f"Searching for {query}"}
#     return {"result": "No query provided"}
#endregion




# uvicorn app.main:app --reload

