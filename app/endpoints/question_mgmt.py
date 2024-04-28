from fastapi import FastAPI, HTTPException, Path, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database.session import get_db  # Assuming databases session setup
from app.models import QuestionBank, PracticeTestsTable  # Your SQLAlchmey models
from pydantic import BaseModel
import json

router = APIRouter()


@router.get("/questions/{question_id}")
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"question": question}

@router.put("/questions/{question_id}")
async def update_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question.topic = question.topic
    question.sub_topic = question.sub_topic
    question.content = question.content
    db.commit()
    return {"message": "Question updated"}

@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}

@router.get("/practice_tests/{test_id}")
async def get_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    return {"practice_test": practice_test}

@router.put("/practice_tests/{test_id}")
async def update_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    practice_test.test = practice_test.test
    practice_test.content = practice_test.content
    db.commit()
    return {"message": "Practice test updated"}

@router.delete("/practice_tests/{test_id}")
async def delete_practice_test(test_id: int, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test:
        raise HTTPException(status_code=404, detail="Practice test not found")
    db.delete(practice_test)
    db.commit()
    return {"message": "Practice test deleted"}

# Additional endpoints for CRUD operations inside a practice test must be adjusted based on your JSON structure
# and might need a more complex handling depending on your actual practice test schema and requirements.

@router.get("/practice_tests/{test_id}/questions/{question_key}")
async def get_practice_test_question(test_id: int, question_key: str, db: Session = Depends(get_db)):
    practice_test = db.query(PracticeTestsTable).filter(PracticeTestsTable.id == test_id).first()
    if not practice_test or question_key not in practice_test.content:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"question": practice_test.content[question_key]}

# POST, PUT, DELETE for questions within a practice test would heavily depend on your JSONB manipulation logic
# and might require using PostgreSQL's JSONB functions through SQLAlchemy's `func` for elaborate JSONB updates.

