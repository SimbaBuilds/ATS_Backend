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
import smtplib  # For sending emails
from email.mime.text import MIMEText




app = FastAPI()

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

#CHATBOT MANIPULATION ENPOINTS
#region

# Base models for data validation
class KnowledgeUpdate(BaseModel):
    topic_id: int
    new_information: str  # Updated information for a specific topic

class Personalization(BaseModel):
    user_id: int
    preference: str  # Could be related to learning styles, etc.

class UserPreference(BaseModel):
    user_id: int
    setting: str  # Personalization setting to update

class SessionSummary(BaseModel):
    chat_id: int
    highlights: List[str]  # Key points from the session

class Reminder(BaseModel):
    user_id: int
    reminder_time: str  # Scheduled time for the reminder
    message: str  # Reminder message

# PUT /chat/update-knowledge/{topicId}: Update the chatbot's knowledge base with new information
@app.put("/chat/update-knowledge/{topicId}")
async def update_knowledge(topicId: int, update: KnowledgeUpdate):
    # Logic to update the knowledge base
    return {"status": "Knowledge updated", "topicId": topicId, "new_information": update.new_information}

# POST /chat/personalize: Customize chatbot responses based on user preferences
@app.post("/chat/personalize")
async def personalize_chat(personalization: Personalization):
    # Logic to customize responses based on user preferences
    return {"status": "Personalization applied", "preference": personalization.preference}

# GET /chat/preferences/{userId}: Retrieve personalization settings for a specific user
@app.get("/chat/preferences/{userId}")
async def get_user_preferences(userId: int):
    # Logic to retrieve user preferences, here we're using a placeholder response
    return {"userId": userId, "preferences": ["style1", "style2"]}

# PUT /chat/preferences/{userId}: Update personalization settings for a specific user
@app.put("/chat/preferences/{userId}")
async def update_user_preferences(userId: int, preference: UserPreference):
    # Logic to update personalization settings
    return {"status": "Preferences updated", "userId": userId, "setting": preference.setting}

# POST /chat/summarize-session: Summarize a chat session, highlighting key points
@app.post("/chat/summarize-session")
async def summarize_session(summary: SessionSummary):
    # Logic to create a summary from chat interactions
    return {"status": "Session summarized", "highlights": summary.highlights}

# GET /chat/topic-summary/{topicId}: Retrieve a concise summary or explanation of a specific topic
@app.get("/chat/topic-summary/{topicId}")
async def get_topic_summary(topicId: int):
    # Logic to get a topic summary, returning a placeholder response
    return {"topicId": topicId, "summary": "Brief summary of the topic"}

# POST /chat/schedule-reminder: Schedule reminders for upcoming study sessions or tests
@app.post("/chat/schedule-reminder")
async def schedule_reminder(reminder: Reminder):
    # Logic to schedule a reminder
    return {"status": "Reminder scheduled", "user_id": reminder.user_id, "message": reminder.message}

#endregion

#AUTHENTICATION AND USER MANAGEMENT ENDPOINTS
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

#QUESTION MANAGEMENT
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

#PRACTICE TESTS AND QUIZZES
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

#HOMEWORK ASSIGNMENTS
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

#USER ANSWERS AND SCORING
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

#CURRICULUM AND STUDY PLANS
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

#PROGRESS TRACKING
#region

# Data model for progress tracking
class UserProgress(BaseModel):
    user_id: int
    quiz_id: int
    score: int  # Could represent a percentage or total score
    timestamp: Optional[datetime.datetime] = None
    session_id: Optional[str] = None  # Session ID for grouping related activities

# GET /progress/user/{userId}: Track the learning progress of a user over time
@app.get("/progress/user/{userId}")
def get_user_progress(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_progress WHERE user_id = %s ORDER BY timestamp ASC", (userId,))
        progress_data = cursor.fetchall()
    
    if not progress_data:
        raise HTTPException(status_code=404, detail="No progress data found for this user")
    
    return {
        "user_id": userId,
        "progress": progress_data
    }

# POST /progress: Update progress data after each quiz or test attempt
@app.post("/progress")
def record_progress(progress: UserProgress):
    progress.timestamp = datetime.datetime.now()  # Record when the progress data was created
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO user_progress (user_id, quiz_id, score, timestamp, session_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (progress.user_id, progress.quiz_id, progress.score, progress.timestamp, progress.session_id)
        )
        connection.commit()
        new_progress_id = cursor.fetchone()[0]
    
    return {
        "status": "Progress recorded",
        "progress_id": new_progress_id
    }

# GET /progress/session/{sessionId}: Retrieve progress details for a specific learning session
@app.get("/progress/session/{sessionId}")
def get_session_progress(sessionId: str):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_progress WHERE session_id = %s", (sessionId,))
        session_progress = cursor.fetchall()
    
    if not session_progress:
        raise HTTPException(status_code=404, detail="No progress data found for this session")
    
    return {
        "session_id": sessionId,
        "progress": session_progress
    }

#endregion

#PERFORAMNCE ANALYTICS
#region

# Data model for performance analytics
class PerformanceAnalytics(BaseModel):
    subject: str
    average_score: float  # Average score across users for this subject
    completion_rate: float  # Completion rate (e.g., % of users who completed all questions)
    difficulty_level: Optional[str] = None  # Could be used to categorize by difficulty

# GET /analytics/performance: Get analytics on user performance across different subjects and difficulty levels
@app.get("/analytics/performance")
def get_performance_analytics():
    with connection.cursor() as cursor:
        # Example query to calculate average score and completion rate for each subject
        cursor.execute(
            """
            SELECT
                subject,
                AVG(score) AS average_score,
                COUNT(score) / (SELECT COUNT(*) FROM questions WHERE subject = subject) * 100 AS completion_rate,
                difficulty_level
            FROM
                user_progress
            GROUP BY
                subject, difficulty_level
            """
        )
        analytics_data = cursor.fetchall()
    
    if not analytics_data:
        raise HTTPException(status_code=404, detail="No performance analytics data found")
    
    # Transform the raw data into a structured format
    performance_analytics = [
        PerformanceAnalytics(
            subject=row[0],
            average_score=row[1],
            completion_rate=row[2],
            difficulty_level=row[3]
        )
        for row in analytics_data
    ]
    
    return {"performance_analytics": performance_analytics}

# Data model for usage analytics
class UsageAnalytics(BaseModel):
    feature_name: str
    usage_count: int  # Number of times a feature or part of the service is used
    last_used: Optional[datetime.datetime]  # Optional timestamp of last usage

# GET /analytics/usage: Obtain statistics on how often different parts of the service are used
@app.get("/analytics/usage")
def get_usage_analytics():
    with connection.cursor() as cursor:
        # Example query to count usage of different features
        cursor.execute(
            """
            SELECT
                feature_name,
                COUNT(*) AS usage_count,
                MAX(timestamp) AS last_used
            FROM
                usage_logs  # Assuming you have a table tracking feature usage
            GROUP BY
                feature_name
            """
        )
        usage_data = cursor.fetchall()
    
    if not usage_data:
        raise HTTPException(status_code=404, detail="No usage analytics data found")
    
    # Transform the raw data into a structured format
    usage_analytics = [
        UsageAnalytics(
            feature_name=row[0],
            usage_count=row[1],
            last_used=row[2]
        )
        for row in usage_data
    ]
    
    return {"usage_analytics": usage_analytics}

#endregion

#COMMUNICATION, NOTIFICATIONS, AND FEEDBACK
#region

# Data model for notifications
class Notification(BaseModel):
    id: int
    user_id: int
    message: str
    is_dismissed: bool = False  # Whether the notification has been dismissed
    timestamp: Optional[datetime.datetime] = None

# Data model for feedback
class Feedback(BaseModel):
    user_id: int
    comment: str
    rating: Optional[int] = None  # Optional rating for feedback
    timestamp: Optional[datetime.datetime] = None

# GET /notifications: Retrieve notifications for a user
@app.get("/notifications")
def get_notifications():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM notifications WHERE is_dismissed = false")
        notifications = cursor.fetchall()
    
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found")
    
    return {
        "notifications": [
            {
                "id": row[0],
                "user_id": row[1],
                "message": row[2],
                "is_dismissed": row[3],
                "timestamp": row[4]
            }
            for row in notifications
        ]
    }

# POST /feedback: Submit feedback about the service or specific content
@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    feedback.timestamp = datetime.datetime.now()  # Record when the feedback was submitted
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO feedback (user_id, comment, rating, timestamp) VALUES (%s, %s, %s, %s) RETURNING id",
            (feedback.user_id, feedback.comment, feedback.rating, feedback.timestamp)
        )
        connection.commit()
        new_feedback_id = cursor.fetchone()[0]
    
    return {"status": "Feedback submitted", "feedback_id": new_feedback_id}

# POST /notifications/dismiss/{id}: Dismiss a specific notification
@app.post("/notifications/dismiss/{id}")
def dismiss_notification(id: int):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE notifications SET is_dismissed = true WHERE id = %s", (id,))
        connection.commit()
    
    return {"status": "Notification dismissed"}

# GET /notifications/history/{userId}: Retrieve history of all notifications for a user
@app.get("/notifications/history/{userId}")
def get_notification_history(userId: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s", (userId,))
        history = cursor.fetchall()
    
    if not history:
        raise HTTPException(status_code=404, detail="No notifications found for this user")
    
    return {
        "user_id": userId,
        "history": [
            {
                "id": row[0],
                "user_id": row[1],
                "message": row[2],
                "is_dismissed": row[3],
                "timestamp": row[4]
            }
            for row in history
        ]
    }

# PUT /feedback/{id}: Update a previously submitted feedback entry
@app.put("/feedback/{id}")
def update_feedback(id: int, updated_feedback: Feedback):
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE feedback SET comment = %s, rating = %s WHERE id = %s",
            (updated_feedback.comment, updated_feedback.rating, id)
        )
        connection.commit()
    
    return {"status": "Feedback updated"}

# POST /email/send: Send an email to a user, particularly useful for updates, reminders, or promotional content
@app.post("/email/send")
def send_email(user_email: str = Body(...), subject: str = Body(...), message: str = Body(...)):
    # Example email configuration (ensure SMTP server and credentials are correct)
    smtp_server = "your_smtp_server"
    smtp_port = 587
    smtp_user = "your_smtp_user"
    smtp_pass = "your_smtp_password"
    
    # Create email
    email_message = MIMEText(message)
    email_message["Subject"] = subject
    email_message["From"] = smtp_user
    email_message["To"] = user_email
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, user_email, email_message.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    
    return {"status": "Email sent"}

#endregion

#ADMIN SPECIFIC
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


# uvicorn main:app --reload
