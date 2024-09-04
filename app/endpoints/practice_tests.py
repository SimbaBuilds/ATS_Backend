
# Import necessary FastAPI and SQLAlchemy modules
from fastapi import FastAPI, HTTPException, Path, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.session import get_db  # Database session setup
from app.models import PracticeTestQuestion, TestAttempt # Using existing SQLAlchemy models
from app.schemas import GetTestResponse, CreateTestResponse, DeleteTestResponse

# define FastAPI router
router = APIRouter()

@router.get("/test/{id}", response_model=GetTestResponse)
async def get_test(
    id: int = Path(..., description="Unique identifier for the test"),
    db: Session = Depends(get_db)
):
    try:
        test = db.query(PracticeTestQuestion).filter_by(id=id).first()

        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        return test
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    
@router.post("/test", response_model=CreateTestResponse)
async def create_test(
    test_name: str,
    content: dict,
    db: Session = Depends(get_db)
):
    try:
        new_test = PracticeTestQuestion(test_name=test_name, content=content)

        db.add(new_test)
        db.commit()

        return {"test_id": new_test.id}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/test/{id}", response_model=DeleteTestResponse)
async def delete_test(
    id: int = Path(..., description="Unique identifier for the test"),
    db: Session = Depends(get_db)
):
    try:
        test = db.query(PracticeTestQuestion).filter_by(id=id).first()

        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        db.delete(test)
        db.commit()

        return {"message": "Test deleted"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
