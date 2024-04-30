
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, File
from sqlalchemy.orm import Session
from app.models import UserMessage, Feedback, ChatbotResponse
from app.schemas import UserMessageStatusResponse, ChatbotResponseModel, AnalyzeImageResponse, ChatHistoryResponse, FeedbackReceivedResponse

from database.session import get_db  # Assuming the database session function exists

router = APIRouter()

# Endpoint for handling user messages and returning chatbot responses
@router.post("/chat/respond", response_model=ChatbotResponseModel)
async def chatbot_respond(message: UserMessage, db: Session = Depends(get_db)):
    # Generate a chatbot response
    response_content = f"Received your message: {message.content}"
    chatbot_response = ChatbotResponse(user_id=message.user_id, response=response_content)
    db.add(chatbot_response)
    db.commit()
    return chatbot_response

# POST /vision/analyze: Accepts file uploads and returns a structured response
@router.post("/vision/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(file: UploadFile = File(...)):
    return AnalyzeImageResponse(filename=file.filename, status="Processed")

# POST /chat/message: Accepts user messages for the chatbot and returns status
@router.post("/chat/message", response_model=UserMessageStatusResponse)
async def chat_message(message: UserMessage, db: Session = Depends(get_db)):
    db.add(message)
    db.commit()
    return UserMessageStatusResponse(status="Message received", content=message.content)


# GET /chat/history/{user_id}: Retrieves chat history for a specific user
@router.get("/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def chat_history(user_id: int, db: Session = Depends(get_db)):
    chat_history = db.query(UserMessage).filter(UserMessage.user_id == user_id).all()
    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return ChatHistoryResponse(history=chat_history)

# POST /chat/feedback: Accepts user feedback
@router.post("/chat/feedback", response_model=FeedbackReceivedResponse)
async def submit_feedback(feedback: Feedback, db: Session = Depends(get_db)):
    db.add(feedback)
    db.commit()
    return FeedbackReceivedResponse(status="Feedback received", rating=feedback.rating, comment=feedback.comment)