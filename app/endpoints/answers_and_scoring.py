from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.database.session import get_db
from app.models import Answer
from app.schemas import SubmitAnswerResponse, GetAnswersResponse, UpdateAnswerResponse, AnswerSchema
from typing import List

router = APIRouter()

# Admin authentication dependency placeholder
def admin_auth():
    # Placeholder for admin authentication logic
    pass

#submit_answer
@router.post("/answers", response_model=SubmitAnswerResponse)  # Use SubmitAnswerResponse for the response
async def submit_answer(answer_data: AnswerSchema, db: Session = Depends(get_db)):
    try:
        # Create a new answer record with SQLAlchemy using the validated Pydantic model data
        new_answer = Answer(**answer_data.dict())
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)

        # Prepare and return the response as per the SubmitAnswerResponse schema
        response_data = SubmitAnswerResponse(
            id=new_answer.id,
            timestamp=new_answer.timestamp,
            status="success" if new_answer.correct else "fail"
        )
        return response_data
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))  # Return a 500 error with details
    

@router.get("/answers/user/{user_id}", response_model=List[GetAnswersResponse])  # Using List of GetAnswersResponse for the output
async def get_user_answers(user_id: int, db: Session = Depends(get_db)):
    try:
        # Retrieve all submissions by a specific user
        user_answers = db.query(Answer).filter(Answer.user_id == user_id).all()
        return user_answers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Return a 500 error with details



@router.put("/answers/{answer_id}", response_model = UpdateAnswerResponse)
async def update_answer(answer_id: int, update_data: UpdateAnswerResponse, db: Session = Depends(get_db)):
    # Update a submitted answer with SQLAlchemy
    existing_answer = db.query(Answer).filter(Answer.id == answer_id).first()

    if not existing_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    existing_answer.answer = update_data.answer
    existing_answer.correct = update_data.correct

    db.commit()
    db.refresh(existing_answer)  # Refresh to get updated data

    return existing_answer


    