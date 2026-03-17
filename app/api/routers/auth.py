from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.core import verify_password, create_access_token, create_refresh_token
from app.services import create_user, get_current_admin_user
from app.services.auth import store_refresh_token, validate_and_rotate_refresh_token, revoke_refresh_token
from app.schemas.auth import UserRegister, RefreshRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered",
        )

    new_user = create_user(db, user_in.model_dump())

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "role": new_user.role_obj.name,
    }


@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    raw_refresh, token_hash, expires_at = create_refresh_token()
    store_refresh_token(db, user.id, token_hash, expires_at)

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role_obj.name,
    }


@router.post("/refresh")
def refresh_access_token(body: RefreshRequest, db: Session = Depends(get_db)):
    user, new_raw_refresh = validate_and_rotate_refresh_token(db, body.refresh_token)

    new_access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_raw_refresh,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    revoke_refresh_token(db, body.refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/admin/create", status_code=status.HTTP_201_CREATED)
def create_admin_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)):
    
    user_exists = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered"
        )

    admin_data = user_in.model_dump()
    admin_data["role"] = UserRole.ADMIN.value

    new_admin = create_user(db, admin_data)

    return {
        "message": "Admin user created successfully",
        "user_id": new_admin.id,
        "username": new_admin.username,
        "role": new_admin.role_obj.name
    }