
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from app.models import UserMessage, Feedback, Conversation, Message
from app.schemas import *
from app.database.session import get_db  # Assuming the database session function exists
from app.utils.chat_utils import query_agent
from uuid import uuid4
from uuid import UUID
import uuid


router = APIRouter()


@router.put("/chat/conversation/{conversation_id}", response_model=GetQBQuestionResponse)
async def update_conversation(conversation_id: str, user_id: UUID = Form(...), content: str = Form(...), role: str = Form('user'), file: UploadFile = File(None), db: Session = Depends(get_db)):
    # Generate a new conversation ID if not provided
    conversation_id = str(uuid4()) if not conversation_id else conversation_id
    
    # Fetch the latest conversation number for the user
    latest_conversation = db.query(Conversation).filter_by(user_id=user_id).order_by(Conversation.conversation_number.desc()).first()
    new_conversation_number = (latest_conversation.conversation_number if latest_conversation else 0) + 1

    # Fetch the existing conversation
    conversation = db.query(Conversation).filter_by(id=conversation_id).first()
    print("fetched conversation")

    # If no conversation found, create a new one
    if not conversation:
        conversation = Conversation(id=conversation_id, user_id=user_id, conversation_number=new_conversation_number, title="New Conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print("conversation created")

    # Append user message to the conversation history
    user_msg = Message(user_id=user_id, content=content, role=role, conversation_id=conversation_id)
    db.add(user_msg)
    db.commit()
    db.refresh(conversation)
    print("message added")

    # Transform conversation messages to the desired format
    #TYPE "TEXT" HARDCODED
    conversation_history = [
        {"role": msg.role, "content": msg.content, "type": "text"}
        for msg in conversation.messages
    ]

    # Add a default system message if the conversation history is empty
    if not conversation_history:
        conversation_history.append({"role": "system", "content": "You are a digital SAT tutor.", "type": "text"})

    chatbot_response_text, question_metadata = query_agent(conversation_history, user_id, db)

    if question_metadata is None:
        question_metadata = {}
        payload_to_chatbot = ""
    else:
        tabular_data_string = str(question_metadata.tabular_data)
        choices_string = str(question_metadata.choices)
        payload_to_chatbot = f"""chatbot response:{chatbot_response_text} \n Note: of the following information, the user will only be shown images/tables and the question content, not answer explanations or correct answers.
        figure description:{question_metadata.figure_description} \n 
        equation:{question_metadata.equation} \n question content:{question_metadata.question_content} \n
        answer explanation:{question_metadata.answer_explanation} \n correct answer:{question_metadata.correct_answer} \n
        tabular data:{tabular_data_string} \n choices:{choices_string}
        """
    

    # Append chatbot response to the conversation history
    bot_msg = Message(user_id=user_id, content=payload_to_chatbot, role='assistant', conversation_id=conversation_id)
    db.add(bot_msg)
    db.commit()
    db.refresh(conversation)
    print("Chatbot Message Added to DB")

    # Return the updated conversation with chatbot response and question metadata, serialized using Pydantic
#     return GetQBQuestionResponse(
#     chatbot_response = chatbot_response_text,
#     id=question_metadata.id,
#     topic=question_metadata.topic,
#     sub_topic=question_metadata.sub_topic,
#     question_number_in_subtopic=question_metadata.question_number_in_subtopic,
#     figure_description=question_metadata.figure_description,
#     image=question_metadata.image,
#     equation=question_metadata.equation,
#     svg=question_metadata.svg,
#     question_content=question_metadata.question_content,
#     answer_explanation=question_metadata.answer_explanation,
#     correct_answer=question_metadata.correct_answer,
#     tabular_data=question_metadata.tabular_data or {},  # ensure this is a dictionary
#     choices=question_metadata.choices or {}  # ensure this is a dictionary
# )
    return GetQBQuestionResponse(
        chatbot_response=chatbot_response_text,
        id=getattr(question_metadata, 'id', 0),
        topic=getattr(question_metadata, 'topic', ''),
        sub_topic=getattr(question_metadata, 'sub_topic', ''),
        question_number_in_subtopic=getattr(question_metadata, 'question_number_in_subtopic', 0),
        figure_description=getattr(question_metadata, 'figure_description', ''),
        image=getattr(question_metadata, 'image', ""),
        equation=getattr(question_metadata, 'equation', ''),
        svg=getattr(question_metadata, 'svg', ""),
        question_content=getattr(question_metadata, 'question_content', ''),
        answer_explanation=getattr(question_metadata, 'answer_explanation', ''),
        correct_answer=getattr(question_metadata, 'correct_answer', ''),
        tabular_data=getattr(question_metadata, 'tabular_data', {}),
        choices=getattr(question_metadata, 'choices', {})
    )



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