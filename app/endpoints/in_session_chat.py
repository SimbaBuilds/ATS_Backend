
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, File
from sqlalchemy.orm import Session
from app.models import UserMessage, Feedback, ChatbotResponse, Conversation, Message
from app.schemas import UserMessageStatusResponse, ChatbotResponseModel, AnalyzeImageResponse, ChatHistoryResponse, FeedbackReceivedResponse, UserMessageSchema, FeedbackModel, ChatHistorySchema, MessageSchema, ConversationSchema
from app.database.session import get_db  # Assuming the database session function exists
from utils.chat_utils import generate_new_response

router = APIRouter()

@router.put("/chat/conversation/{conversation_id}", response_model=ConversationSchema)
async def update_conversation(conversation_id: int, message: UserMessageSchema, db: Session = Depends(get_db)):
    # Fetch the existing conversation
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Append user message to the conversation history
    user_msg = Message(user_id=message.user_id, content=message.content, role='user', conversation_id=conversation_id)
    db.add(user_msg)

    # Generate a response from the chatbot
    # Simulate generating a response
    chatbot_response_text = generate_new_response(message.content)

    # Append chatbot response to the conversation history
    bot_msg = Message(user_id=message.user_id, content=chatbot_response_text, role='assistant', conversation_id=conversation_id)
    db.add(bot_msg)

    # Commit the updated conversation to the database
    db.commit()

    # Reload the conversation to ensure all messages are included
    db.refresh(conversation)

    # Return the updated conversation, serialized using Pydantic
    return conversation

# POST /vision/analyze: Accepts file uploads and returns a structured response
@router.post("/vision/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(file: UploadFile = File(...)):
    return AnalyzeImageResponse(filename=file.filename, status="Processed")

# POST /chat/message: Accepts user messages for the chatbot and returns status
@router.post("/chat/message", response_model=UserMessageStatusResponse)
async def chat_message(message: UserMessageSchema, db: Session = Depends(get_db)):
    db.add(message)
    db.commit()
    return UserMessageStatusResponse(status="Message received", content=message.content)


# GET /chat/history/{user_id}: Retrieves chat history for a specific user
@router.get("/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def chat_history(user_id: int, db: Session = Depends(get_db)):
    chat_history = db.query(UserMessage).filter(UserMessage.user_id == user_id).all()
    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return chat_history

# POST /chat/feedback: Accepts user feedback
@router.post("/chat/feedback", response_model=FeedbackReceivedResponse)
async def submit_feedback(feedback: FeedbackModel, db: Session = Depends(get_db)):
    db.add(feedback)
    db.commit()
    return FeedbackReceivedResponse(status="Feedback received", rating=feedback.rating, comment=feedback.comment)