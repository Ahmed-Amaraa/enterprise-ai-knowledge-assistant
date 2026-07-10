from sqlalchemy import ForeignKey, Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        index=True
    )

    content: Mapped[str] = mapped_column(Text)

    chunk_index: Mapped[int] = mapped_column(Integer, index=True)
    token_count: Mapped[int] = mapped_column(Integer, nullable=True)

    # pgvector will replace this type below
    embedding_vector: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
    message_chunks = relationship("MessageChunk", back_populates="chunk")