from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.database.session import get_db
from app.models import User, AdminActionsTable  # Assuming User model from users.py is imported here
from app.schemas import UserResponse, DeleteUserResponse, RecordAdminActionResponse, AdminActionResponse, UpdateUserResponse
from pydantic import List

router = APIRouter()

# Admin authentication dependency placeholder
def admin_auth():
    # Placeholder for admin authentication logic
    pass

# GET /admin/users: List all users (admin access)
@router.get("/admin/users", dependencies=[Depends(admin_auth)], response_model = List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    # Using SQLAlchemy to list all users
    users = db.query(User).all()
    return users

#POST record admin action
@router.post("/admin/actions", dependencies=[Depends(admin_auth)], response_model= RecordAdminActionResponse)
async def record_admin_action(action_type: str, user_id: int, details: str, db: Session = Depends(get_db)):
    try:
        # Create a new admin action record with SQLAlchemy
        new_action = AdminActionsTable(
            action_type=action_type,
            user_id=user_id,
            details=details,
            timestamp=datetime.now()
        )
        db.add(new_action)
        db.commit()
        db.refresh(new_action)  # Refresh the object to get the generated ID
        return RecordAdminActionResponse(status="Admin action recorded", action_id=new_action.id)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /admin/users/{user_id}: Remove a user from the platform (admin access)
@router.delete("/admin/users/{user_id}", dependencies=[Depends(admin_auth)], response_model=DeleteUserResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Delete a user with SQLAlchemy
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"status": "User removed from platform", "user_id": user_id}



# GET /admin/action: Get an admin action
@router.get("/admin/action", dependencies=[Depends(admin_auth)], response_model = AdminActionResponse)
async def list_admin_actions(action_id: int, db: Session = Depends(get_db)):
    # List all admin actions with SQLAlchemy
    admin_action = db.query(AdminActionsTable.id)
    return admin_action


# GET /admin/actions: List all admin actions (admin access)
@router.get("/admin/actions", dependencies=[Depends(admin_auth)], response_model = List[AdminActionResponse])
async def list_admin_actions(db: Session = Depends(get_db)):
    # List all admin actions with SQLAlchemy
    admin_actions = db.query(AdminActionsTable).all()
    return admin_actions



@router.put("/admin/users/{user_id}", dependencies=[Depends(admin_auth)], response_model=UpdateUserResponse)
async def update_user_role_or_status(user_id: int, new_role: str, new_status: bool, db: Session = Depends(get_db)):
    # Update a user's role or status with SQLAlchemy
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    user.status = new_status
    db.commit()
    db.refresh(user)  # Refresh the object to get the updated data

    # Return response matching the UpdateUserResponse schema
    return UpdateUserResponse(
        status="User role and status updated",
        user_id=user.id,
        user_role=user.role,
        user_status=user.status
    )