from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.database.session import get_db
from app.models import User, Answer, QuestionBank  #

router = APIRouter()

# Admin authentication dependency placeholder
def admin_auth():
    # Placeholder for admin authentication logic
    pass

# POST /answers: Submit answers for a quiz or practice test
@router.post("/answers")
async def submit_answer(user_id: int, quiz_id: int, question_id: int, answer: str, correct: bool, db: Session = Depends(get_db)):
    # Create a new answer record with SQLAlchemy
    new_answer = Answer(
        user_id=user_id,
        quiz_id=quiz_id,
        question_id=question_id,
        answer=answer,
        correct=correct,
        timestamp=datetime.now()  # Record the submission time
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)  # Refresh to get the generated ID

    return {"status": "Answer submitted", "answer_id": new_answer.id}

# GET /answers/user/{user_id}: Retrieve all submissions by a specific user
@router.get("/answers/user/{user_id}")
async def get_user_answers(user_id: int, db: Session = Depends(get_db)):
    # Retrieve all submissions by a specific user
    user_answers = db.query(Answer).filter(Answer.user_id == user_id).all()
    return user_answers

# GET /answers/quiz/{quiz_id}: Retrieve all answers for a specific quiz
@router.get("/answers/quiz/{quiz_id}")
async def get_quiz_answers(quiz_id: int, db: Session = Depends(get_db)):
    # Retrieve all answers for a specific quiz
    quiz_answers = db.query(Answer).filter(Answer.quiz_id == quiz_id).all()
    return quiz_answers

# PUT /answers/{answer_id}: Update a submitted answer
@router.put("/answers/{answer_id}")
async def update_answer(answer_id: int, answer: str, correct: bool, db: Session = Depends(get_db)):
    # Update a submitted answer with SQLAlchemy
    existing_answer = db.query(Answer).filter(Answer.id == answer_id).first()

    if not existing_answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    existing_answer.answer = answer
    existing_answer.correct = correct

    db.commit()
    db.refresh(existing_answer)  # Refresh to get updated data

    return {"status": "Answer updated", "answer": existing_answer}

# GET /question_bank: Retrieve all questions in the bank
@router.get("/question_bank")
async def get_question_bank(db: Session = Depends(get_db)):
    # Retrieve all questions from the question bank
    questions = db.query(QuestionBank).all()
    return questions
    