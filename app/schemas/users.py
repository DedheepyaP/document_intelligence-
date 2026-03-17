from pydantic import BaseModel, field_validator

from app.models.user import UserRole


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}

    @field_validator("role", mode="before")
    def get_role_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v


class RoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    def validate_role(cls, v):
        allowed_roles = [role.value for role in UserRole]
        if v not in allowed_roles:
            raise ValueError(f"Invalid role. Allowed roles: {', '.join(allowed_roles)}")
        return v
