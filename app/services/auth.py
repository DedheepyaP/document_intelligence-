from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Role, UserRole, RefreshToken
from app.core.security import get_password_hash, hash_token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_user(db: Session, user_data: dict) -> User:
    hashed_pwd = get_password_hash(user_data["password"])

    role_name = user_data.get("role", UserRole.GENERAL.value)
    role = db.query(Role).filter(Role.name == role_name).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_name}' does not exist",
        )

    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_pwd,
        role_id=role.id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_role(db: Session, user_id: int, role_name: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_name}' does not exist",
        )

    user.role_id = role.id
    db.commit()
    db.refresh(user)
    return user


def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    request.state.user_id = f"user:{user.id}"
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_obj.name != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def store_refresh_token(
    db: Session,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    rt = RefreshToken(
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        is_revoked=False,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def validate_and_rotate_refresh_token(
    db: Session,
    raw_token: str,
) -> tuple[User, str]:
    from app.core.security import create_refresh_token

    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    token_h = hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_h).first()

    if rt is None or rt.is_revoked:
        raise invalid_exc

    now_utc = datetime.now(timezone.utc)
    expires = rt.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if now_utc > expires:
        raise invalid_exc

    user = rt.user  # load relationship before flush expires the object

    # Step 1 — revoke old token (not committed yet)
    rt.is_revoked = True
    db.flush()

    # Step 2 — generate + store new token in the same transaction
    new_raw, new_hash, new_expires = create_refresh_token()
    new_rt = RefreshToken(
        token_hash=new_hash,
        user_id=user.id,
        expires_at=new_expires,
        created_at=now_utc,
        is_revoked=False,
    )
    db.add(new_rt)
    db.commit()  # single commit: old revoked + new stored atomically

    return user, new_raw


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    """Mark a refresh token as revoked (called on logout)."""
    token_h = hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_h).first()
    if rt and not rt.is_revoked:
        rt.is_revoked = True
        db.commit()