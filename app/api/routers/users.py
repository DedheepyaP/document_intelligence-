from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.auth import get_current_admin_user, update_user_role
from app.schemas.users import UserOut, RoleUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role_obj.name,
        )
        for user in users
    ]


@router.put("/{user_id}/role", response_model=UserOut)
def update_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    updated_user = update_user_role(db, user_id, role_update.role)
    return UserOut(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role_obj.name,
    )
