from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class MessageChunk(Base):
    __tablename__ = "message_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), index=True)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("chunks.id"), index=True)

    score = mapped_column(Float)

    message = relationship("Message", back_populates="message_chunks")
    chunk = relationship("Chunk", back_populates="message_chunks")