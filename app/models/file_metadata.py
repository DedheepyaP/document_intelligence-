from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="files")

    def __repr__(self):
        return f"<FileMetadata(id={self.id}, filename={self.filename}, user_id={self.user_id})>"
