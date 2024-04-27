
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.database.session import get_db
from app.models import User  # Assuming User model from users.py is imported here
from app.models import AdminActionsTable  # Include the admin actions model

router = APIRouter()

# Admin authentication dependency placeholder
def admin_auth():
    # Placeholder for admin authentication logic
    pass

# GET /admin/users: List all users (admin access)
@router.get("/admin/users", dependencies=[Depends(admin_auth)])
def list_users(db: Session = Depends(get_db)):
    # Using SQLAlchemy to list all users
    users = db.query(User).all()
    return users

# POST /admin/actions: Record an admin action (admin access)
@router.post("/admin/actions", dependencies=[Depends(admin_auth)])
def record_admin_action(action_type: str, user_id: int, details: str, db: Session = Depends(get_db)):
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

    return {
        "status": "Admin action recorded",
        "action_id": new_action.id
    }

# DELETE /admin/users/{user_id}: Remove a user from the platform (admin access)
@router.delete("/admin/users/{user_id}", dependencies=[Depends(admin_auth)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Delete a user with SQLAlchemy
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"status": "User removed from platform"}

# GET /admin/actions: List all admin actions (admin access)
@router.get("/admin/actions", dependencies=[Depends(admin_auth)])
def list_admin_actions(db: Session = Depends(get_db)):
    # List all admin actions with SQLAlchemy
    admin_actions = db.query(AdminActionsTable).all()
    return admin_actions

# PUT /admin/users/{user_id}: Update a user's role or status (admin access)
@router.put("/admin/users/{user_id}", dependencies=[Depends(admin_auth)])
def update_user_role_or_status(user_id: int, new_role: str, new_status: bool, db: Session = Depends(get_db)):
    # Update a user's role or status with SQLAlchemy
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    user.status = new_status

    db.commit()
    db.refresh(user)  # Refresh the object to get the updated data

    return {"status": "User role and status updated", "user": user}

    