from app.models import User, UserQuestionProgress, QuestionType, QuestionBankQuestion
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, Form

def get_user_progress_on_question_type(db: Session, user_id: UUID, question_type_id: int):
    
    if not db.query(UserQuestionProgress).join(User).join(QuestionType).filter(User.user_id == user_id, UserQuestionProgress.question_type_id == question_type_id).first():
        return 0
    
    progress_record =  db.query(UserQuestionProgress).join(User).join(QuestionType).filter(User.user_id == user_id, UserQuestionProgress.question_type_id == question_type_id).first().progress

    return progress_record

def increment_user_progress(db: Session, user_id: UUID, sub_topic: str):
    
    question_type_id = db.query(QuestionType).filter(QuestionType.question_type_name == sub_topic).first().question_type_id
    
    # Step 1: Retrieve the current progress record
    progress_record = (
        db.query(UserQuestionProgress)
        .join(QuestionType)
        .filter(UserQuestionProgress.user_id == user_id, QuestionType.question_type_name == sub_topic)
        .first()
    )
    
    if progress_record:
        # Step 2: Increment the progress field
        progress_record.progress += 1
        
        # Step 3: Commit the changes
        db.commit()
        
        return 
    else:
        # If no record exists, consider creating one or handling this case appropriately
        new_progress_record = UserQuestionProgress(user_id=user_id, question_type_id=question_type_id, progress=2)
        db.add(new_progress_record)
        db.commit()
        return 

def get_question_by_sub_topic_and_number(db: Session, sub_topic: str, question_number_in_subtopic: int):
    return (
        db.query(QuestionBankQuestion)
        .filter(QuestionBankQuestion.sub_topic == sub_topic,  QuestionBankQuestion.question_number_in_subtopic == question_number_in_subtopic)
        .first()
    )
