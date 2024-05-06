from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import CurriculumPlan, User
from app.schemas import GetAllUsersResponse, GetCurriculumResponse, CreateCurriculumResponse, CurriculumPlanModel, UpdateCurriculumResponse, CurriculumPlanBase, DeleteCurriculumResponse
from app.database.session import get_db
from typing import List

router = APIRouter()


@router.get("/curriculum/{userId}", response_model=CurriculumPlanModel)
async def get_curriculum(userId: int, db: Session = Depends(get_db)):
    try:
        plans = db.query(CurriculumPlan).filter_by(user_id=userId).all()
        if not plans:
            raise HTTPException(status_code=404, detail="No curriculum plans found for this user")
        return CurriculumPlanModel
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/curriculum", response_model=CreateCurriculumResponse)
async def create_curriculum(plan: CurriculumPlanModel, db: Session = Depends(get_db)):
    try:
        new_plan = CurriculumPlan(**plan.dict(exclude_unset=True))
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return CreateCurriculumResponse(status="Curriculum plan created", plan_id=new_plan.id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /curriculum/{id}: Update an existing study plan
@router.put("/curriculum/{id}", response_model=UpdateCurriculumResponse)
async def update_curriculum(id: int, updated_plan: CurriculumPlanBase, db: Session = Depends(get_db)):
    try:
        existing_plan = db.query(CurriculumPlan).filter_by(id=id).first()
        if not existing_plan:
            raise HTTPException(status_code=404, detail="Curriculum plan not found")
        
        for key, value in updated_plan.dict().items():
            setattr(existing_plan, key, value)
        
        db.commit()
        db.refresh(existing_plan)
        return UpdateCurriculumResponse(message="Curriculum plan updated", plan=existing_plan)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /curriculum/{id}: Delete a study plan
@router.delete("/curriculum/{id}", response_model=DeleteCurriculumResponse)
async def delete_curriculum(id: int, db: Session = Depends(get_db)):
    try:
        plan_to_delete = db.query(CurriculumPlan).filter_by(id=id).first()
        if not plan_to_delete:
            raise HTTPException(status_code=404, detail="Curriculum plan not found")

        db.delete(plan_to_delete)
        db.commit()
        return DeleteCurriculumResponse(message="Curriculum plan deleted")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))