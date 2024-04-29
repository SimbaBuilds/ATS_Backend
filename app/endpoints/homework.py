
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Homework  # Pre-defined SQLAlchemy model
from app.database.session import get_db
from typing import Optional, List

router = APIRouter()

# GET /homework/{userId}: Retrieve all homework assignments for a specific user
@router.get("/homework/{userId}")
async def get_homework(userId: int, db: Session = Depends(get_db)):
    try:
        results = db.query(Homework).filter_by(user_id=userId).all()
        if not results:
            raise HTTPException(status_code=404, detail="No homework assignments found")
        
        homework_assignments = [{"id": r.id, "user_id": r.user_id, "assignment": r.assignment, "due_date": r.due_date, "details": r.details} for r in results]
        return {"homework": homework_assignments}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /homework: Assign new homework to a user or group
@router.post("/homework")
async def assign_homework(new_homework: Homework, db: Session = Depends(get_db)):
    try:
        db.add(new_homework)
        db.commit()
        db.refresh(new_homework)
        return {"message": "Homework assigned", "homework_id": new_homework.id}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /homework/{id}: Update details or deadlines of an existing homework assignment
@router.put("/homework/{id}")
async def update_homework(id: int, updated_homework: Homework, db: Session = Depends(get_db)):
    try:
        existing_homework = db.query(Homework).filter_by(id=id).first()
        if not existing_homework:
            raise HTTPException(status_code=404, detail="Homework not found")
        
        for key, value in updated_homework.dict().items():
            setattr(existing_homework, key, value)
        
        db.commit()
        db.refresh(existing_homework)
        return {"message": "Homework updated"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /homework/{id}: Remove a homework assignment
@router.delete("/homework/{id}")
async def delete_homework(id: int, db: Session = Depends(get_db)):
    try:
        homework_to_delete = db.query(Homework).filter_by(id=id).first()
        if not homework_to_delete:
            raise HTTPException(status_code=404, detail="Homework not found")

        db.delete(homework_to_delete)
        db.commit()
        return {"message": "Homework deleted"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
