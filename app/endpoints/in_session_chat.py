
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from models import UserMessage, ChatbotResponse, Feedback
from database import get_db  # Assuming the database session function exists

router = APIRouter()

# Endpoint for handling user messages and returning chatbot responses
@app.post("/chat/respond")
async def chatbot_respond(message: UserMessage, db: Session = Depends(get_db)):
    # Generate a chatbot response
    response_content = f"Received your message: {{message.content}}"
    chatbot_response = ChatbotResponse(user_id=message.user_id, response=response_content)
    db.add(chatbot_response)
    db.commit()
    return chatbot_response

# POST /vision/analyze: Accepts file uploads
@app.post("/vision/analyze")
async def analyze_image(file: UploadFile = File(...)):
    return {"filename": file.filename, "status": "Processed"}

# POST /chat/message: Accepts user messages for the chatbot
@app.post("/chat/message")
async def chat_message(message: UserMessage, db: Session = Depends(get_db)):
    db.add(message)
    db.commit()
    return {"status": "Message received", "content": message.content}

# GET /chat/history/{user_id}: Retrieves chat history for a specific user
@app.get("/chat/history/{user_id}")
async def chat_history(user_id: int, db: Session = Depends(get_db)):
    chat_history = db.query(UserMessage).filter(UserMessage.user_id == user_id).all()
    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return chat_history

# POST /chat/feedback: Accepts user feedback
@app.post("/chat/feedback")
async def submit_feedback(feedback: Feedback, db: Session = Depends(get_db)):
    db.add(feedback)
    db.commit()
    return {"status": "Feedback received", "rating": feedback.rating, "comment": feedback.comment}
