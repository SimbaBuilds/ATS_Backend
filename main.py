from fastapi import FastAPI
from typing import Optional  # This is for defining optional parameters
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

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



# Data model for POST /chat/message
class Message(BaseModel):
    user_id: int
    content: str

# Data model for POST /chat/feedback
class Feedback(BaseModel):
    user_id: int
    rating: int  # Example feedback, could be a rating out of 5
    comment: str

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


# uvicorn main:app --reload
