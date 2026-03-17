import re
from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str = UserRole.GENERAL.value

    @field_validator("role")
    def validate_role(cls, v):
        allowed_roles = [role.value for role in UserRole]
        if v not in allowed_roles:
            raise ValueError(f"Invalid role. Allowed roles: {', '.join(allowed_roles)}")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
