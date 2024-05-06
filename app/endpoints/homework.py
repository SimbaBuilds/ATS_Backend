
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Homework  # Pre-defined SQLAlchemy model
from app.schemas import HomeworkAssignmentsResponse, HomeworkAssignmentResponse, HomeworkBase, UpdateHomeworkResponse, DeleteHomeworkResponse
from app.database.session import get_db
from typing import Optional, List

router = APIRouter()

# GET /homework/{userId}: Retrieve all homework assignments for a specific user
@router.get("/homework/{userId}", response_model=HomeworkAssignmentsResponse)
async def get_homework(userId: int, db: Session = Depends(get_db)):
    try:
        results = db.query(Homework).filter_by(user_id=userId).all()
        if not results:
            raise HTTPException(status_code=404, detail="No homework assignments found")
        
        return results
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /homework: Assign new homework to a user or group
@router.post("/homework", response_model=HomeworkAssignmentResponse)
async def assign_homework(new_homework: HomeworkBase, db: Session = Depends(get_db)):
    try :
        homework_model = Homework(**new_homework.dict())
        db.add(homework_model)
        db.commit()
        db.refresh(homework_model)
        return HomeworkAssignmentResponse(message="Homework assigned", homework_id=homework_model.id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /homework/{id}: Update details or deadlines of an existing homework assignment
@router.put("/homework/{id}", response_model=UpdateHomeworkResponse)
async def update_homework(id: int, updated_homework: HomeworkBase, db: Session = Depends(get_db)):
    try:
        existing_homework = db.query(Homework).filter_by(id=id).first()
        if not existing_homework:
            raise HTTPException(status_code=404, detail="Homework not found")
        
        for key, value in updated_homework.dict().items():
            setattr(existing_homework, key, value)
        
        db.commit()
        db.refresh(existing_homework)
        return UpdateHomeworkResponse(message="Homework updated", homework=existing_homework)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /homework/{id}: Remove a homework assignment
@router.delete("/homework/{id}", response_model=DeleteHomeworkResponse)
async def delete_homework(id: int, db: Session = Depends(get_db)):
    try :
        homework_to_delete = db.query(Homework).filter_by(id=id).first()
        if not homework_to_delete:
            raise HTTPException(status_code=404, detail="Homework not found")

        db.delete(homework_to_delete)
        db.commit()
        return DeleteHomeworkResponse(message="Homework deleted")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))