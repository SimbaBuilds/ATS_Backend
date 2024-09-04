from app.models import User, UserQuestionProgress, QuestionType, QuestionBankQuestion
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, Form

def get_user_progress_on_question_type(db: Session, user_id: UUID, question_type_id: int):
    return (
        db.query(UserQuestionProgress)
        .join(User)
        .join(QuestionType)
        .filter(User.id == user_id, UserQuestionProgress.question_type_id == question_type_id)
        .first()
    )

def get_question_by_sub_topic_and_number(db: Session, sub_topic: str, question_number_in_subtopic: int):
    return (
        db.query(Question)
        .filter(Question.sub_topic == sub_topic, Question.question_number_in_subtopic == question_number_in_subtopic)
        .first()
    )

def increment_user_progress(db: Session, user_id: UUID, sub_topic: str):
    # Step 1: Retrieve the current progress record
    progress_record = (
        db.query(UserQuestionProgress)
        .join(Question, Question.sub_topic == sub_topic)
        .filter(UserQuestionProgress.user_id == user_id, UserQuestionProgress.question_type_id == Question.id)
        .first()
    )
    
    if progress_record:
        # Step 2: Increment the progress field
        progress_record.progress += 1
        
        # Step 3: Commit the changes
        db.commit()
        
        return progress_record
    else:
        # If no record exists, consider creating one or handling this case appropriately
        print(f"No progress record found for user {user_id} in sub-topic {sub_topic}.")
        return None
