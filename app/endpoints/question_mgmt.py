from fastapi import FastAPI, HTTPException, Path, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database.session import get_db  # Assuming databases session setup
from app.models import QuestionBank, PracticeTestsTable  # Your SQLAlchmey models
from app.schemas import UpdateQuestionResponse, DeleteQuestionResponse, GetPracticeTestResponse, UpdatePracticeTestResponse, DeletePracticeTestResponse, GetPracticeTestQuestionResponse, GetQBQuestionResponse

router = APIRouter()
@router.get("/questions/{question_id}", response_model=GetQBQuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.put("/questions/{question_id}", response_model=UpdateQuestionResponse)
async def update_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    # Update logic here, e.g., question.topic = new_topic
    db.commit()
    return UpdateQuestionResponse(message="Question updated", id = question.id)

@router.delete("/questions/{question_id}", response_model=DeleteQuestionResponse)
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return DeleteQuestionResponse(message="Question deleted")

@router.get("/practice_tests/{test_id}", response_model=GetPracticeTestResponse)
async def get_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    return practice_test

@router.put("/practice_tests/{test_id}", response_model=UpdatePracticeTestResponse)
async def update_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    # Update logic here, e.g., practice_test.test = new_test
    db.commit()
    return UpdatePracticeTestResponse(message="Practice test updated")

@router.delete("/practice_tests/{test_id}", response_model=DeletePracticeTestResponse)
async def delete_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    db.delete(practice_test)
    db.commit()
    return DeletePracticeTestResponse(message="Practice test deleted")

@router.get("/practice_tests/{practice_test}/questions/{question_number}", response_model=GetPracticeTestQuestionResponse)
async def get_practice_test_question(practice_test: str, question_number: int, db: Session = Depends(get_db)):
    practice_test_question = db.query(PracticeTestsTable).filter(PracticeTestsTable.practice_test == practice_test and PracticeTestsTable.question_number == question_number).first()
    if not practice_test or question_number not in practice_test.content:
        raise HTTPException(status_code=404, detail="Question not found")
    return practice_test_question
