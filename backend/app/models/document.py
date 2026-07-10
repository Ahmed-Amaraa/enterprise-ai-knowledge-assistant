from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base
from sqlalchemy import func


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)

    title: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)

    file_size: Mapped[int] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String, default="uploaded")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")