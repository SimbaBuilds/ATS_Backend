
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import curriculum_plan, User  # Pre-defined models
from app.database.session import get_db
from typing import List

router = APIRouter()

# GET /users: Get all users
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    try:
        return db.query(User).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /curriculum/{userId}: Fetch the personalized study plan for a specific user
@router.get("/curriculum/{userId}")
def get_curriculum(userId: int, db: Session = Depends(get_db)):
    try:
        plans = db.query(curriculum_plan).filter_by(user_id=userId).all()
        if not plans:
            raise HTTPException(status_code=404, detail="No curriculum plans found for this user")
        return {"user_id": userId, "curriculum_plans": plans}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /curriculum: Create a new curriculum plan for a user or a group
@router.post("/curriculum")
def create_curriculum(plan: curriculum_plan, db: Session = Depends(get_db)):
    try:
        new_plan = curriculum_plan(**plan.dict())
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return {"status": "Curriculum plan created", "plan_id": new_plan.id}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /curriculum/{id}: Update an existing study plan
@router.put("/curriculum/{id}")
def update_curriculum(id: int, updated_plan: curriculum_plan, db: Session = Depends(get_db)):
    try:
        existing_plan = db.query(curriculum_plan).filter_by(id=id).first()
        if not existing_plan:
            raise HTTPException(status_code=404, detail="Curriculum plan not found")
        
        for key, value in updated_plan.dict().items():
            setattr(existing_plan, key, value)
        
        db.commit()
        db.refresh(existing_plan)
        return {"status": "Curriculum plan updated"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /curriculum/{id}: Delete a study plan
@router.delete("/curriculum/{id}")
def delete_curriculum(id: int, db: Session = Depends(get_db)):
    try:
        plan_to_delete = db.query(curriculum_plan).filter_by(id=id).first()
        if not plan_to_delete:
            raise HTTPException(status_code=404, detail="Curriculum plan not found")

        db.delete(plan_to_delete)
        db.commit()
        return {"status": "Curriculum plan deleted"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
