from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

if TYPE_CHECKING:
    from app.models.file_metadata import FileMetadata
    from app.models.conversation import ConversationMessage

from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    LAWYER = "lawyer"              
    RESEARCHER = "researcher"
    CONSULTANT = "consultant"      
    FINANCIAL_ANALYST = "analyst" 
    GENERAL = "general"

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)    
    users: Mapped[List['User']] = relationship('User', back_populates='role_obj')

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)
    
    role_obj: Mapped[Role] = relationship('Role', back_populates='users')
    files: Mapped[List["FileMetadata"]] = relationship("FileMetadata", back_populates="user")
    messages: Mapped[List["ConversationMessage"]] = relationship("ConversationMessage", back_populates="user")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
