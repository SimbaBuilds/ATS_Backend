
# Import necessary FastAPI and SQLAlchemy modules
from fastapi import FastAPI, HTTPException, Path, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.session import get_db  # Database session setup
from app.models import practice_tests_table, test_attempts  # Using existing SQLAlchemy models


# Define FastAPI router
router = APIRouter()

# GET /test/{id}: Get details about a specific quiz or test
@router.get("/test/{id}")
def get_test(
    id: int = Path(..., description="Unique identifier for the test"),
    db: Session = Depends(get_db)
):
    try:
        test = db.query(practice_tests_table).filter_by(id=id).first()

        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        return {
            "test": {
                "id": test.id,
                "test_name": test.test_name,
                "content": test.content  # Test content could be questions or other data
            }
        }
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# POST /test: Create a new quiz or test (admin or teacher access)
@router.post("/test")
def create_test(
    test_name: str,
    content: dict,
    db: Session = Depends(get_db)
):
    try:
        new_test = practice_tests_table(test_name=test_name, content=content)

        db.add(new_test)
        db.commit()

        return {"test_id": new_test.id}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# DELETE /test/{id}: Delete a specific test
@router.delete("/test/{id}")
def delete_test(
    id: int = Path(..., description="Unique identifier for the test"),
    db: Session = Depends(get_db)
):
    try:
        test = db.query(practice_tests_table).filter_by(id=id).first()

        if not test:
            raise HTTPException(status_code=404, detail="Test not found")

        db.delete(test)
        db.commit()

        return {"message": "Test deleted"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
