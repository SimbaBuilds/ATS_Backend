
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, File
from sqlalchemy.orm import Session
from app.models import UserMessage, Feedback, ChatbotResponse, Conversation, Message
from app.schemas import UserMessageStatusResponse, ChatbotResponseSchema, AnalyzeImageResponse, ChatHistoryResponse, FeedbackReceivedResponse, UserMessageSchema, FeedbackModel, ChatHistorySchema, MessageSchema, ConversationSchema
from app.database.session import get_db  # Assuming the database session function exists
from app.utils.chat_utils import generate_new_response

router = APIRouter()


@router.put("/chat/conversation/{conversation_id}", response_model=ChatbotResponseSchema)
async def update_conversation(conversation_id: int, message: UserMessageSchema, db: Session = Depends(get_db)):
    # Fetch the existing conversation
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    print("fetched conversation")

    # If no conversation found, create a new one
    if not conversation:
        conversation = Conversation(id=conversation_id, title="New Conversation")  # Ensure title handling
        db.add(conversation)
        db.commit()
        db.refresh(conversation)  # Refresh to get the ID
        print("conversation created")

    # Append user message to the conversation history
    user_msg = Message(user_id=message.user_id, content=message.content, role='user', conversation_id=conversation_id)
    db.add(user_msg)
    db.commit()  # Commit to ensure the message is saved in the database
    db.refresh(conversation)  # Refresh to include the latest message
    print("message added")

    # Transform conversation messages to the desired format
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation.messages
    ]

    # Add a default system message if the conversation history is empty
    if not conversation_history:
        conversation_history.append({"role": "system", "content": "You are a helpful digital SAT tutor."})

    chatbot_response_text = generate_new_response(conversation_history)
    print(f"Chatbot Response: {chatbot_response_text}")

    # Append chatbot response to the conversation history
    bot_msg = Message(user_id=message.user_id, content=chatbot_response_text, role='assistant', conversation_id=conversation_id)
    db.add(bot_msg)
    db.commit()  # Commit to save the chatbot's response in the database
    db.refresh(conversation)  # Refresh to include all messages
    print("Chatbot Message Added")

    # Return the updated conversation, serialized using Pydantic
    return ChatbotResponseSchema(user_id=message.user_id, response=chatbot_response_text)



# @router.put("/chat/conversation/{conversation_id}", response_model=ChatbotResponseSchema)
# async def update_conversation(conversation_id: int, message: UserMessageSchema, db: Session = Depends(get_db)):
#     # Fetch the existing conversation
#     conversation = db.query(Conversation).filter_by(id=conversation_id).first()
#     print("fetched conversation")

#     # If no conversation found, create a new one
#     if not conversation:
#         conversation = Conversation(id=conversation_id, title="New Conversation")  # Ensure title handling
#         db.add(conversation)
#         db.commit()
#         print("conversation created")

#     # Append user message to the conversation history
#     user_msg = Message(user_id=message.user_id, content=message.content, role='user', conversation_id=conversation_id)
#     db.add(user_msg)
#     print("message added")

#     # Transform conversation messages to the desired format
#     conversation_history = [
#         {"role": msg.role, "content": msg.content}
#         for msg in conversation.messages
#     ]

#     # Add a default system message if the conversation history is empty
#     if not conversation_history:
#         conversation_history.append({"role": "system", "content": "You are a helpful digital SAT tutor."})


#     chatbot_response_text = generate_new_response(conversation_history)
#     print(f"Chatbot Response: {chatbot_response_text}")

#     # Append chatbot response to the conversation history
#     bot_msg = Message(user_id=message.user_id, content=chatbot_response_text, role='assistant', conversation_id=conversation_id)
#     db.add(bot_msg)
#     print("Chatbot Message Added")


#     # Commit the updated conversation to the database
#     db.commit()
#     print("response added")

#     # Reload the conversation to ensure all messages are included
#     db.refresh(conversation)

#     # Return the updated conversation, serialized using Pydantic
#     return ChatbotResponseSchema(user_id=message.user_id, response=chatbot_response_text)




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