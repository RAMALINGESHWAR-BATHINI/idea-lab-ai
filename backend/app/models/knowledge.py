"""Knowledge models: Document, DocumentChunk (pgvector), Research, WebSource."""
from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AccessLevel, DocumentType


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An institutional document tracked by the knowledge base."""

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    doc_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type"),
        default=DocumentType.OTHER,
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploaded_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Document {self.title}>"


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A vector-embedded slice of a document, used for semantic retrieval."""

    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    document: Mapped[Document] = relationship(back_populates="chunks")

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding_provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.embedding_dimension), nullable=True
    )
    # Denormalised access level so retrieval can filter without a join.
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.INTERNAL,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<DocumentChunk doc={self.document_id} #{self.chunk_index}>"


class Research(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A research output (paper, patent, thesis)."""

    __tablename__ = "research"

    title: Mapped[str] = mapped_column(String(400), index=True, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(200), nullable=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Research {self.title}>"


class WebSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A public web source that has been fetched and cached for citation."""

    __tablename__ = "web_sources"

    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fetched_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(
        SAEnum(AccessLevel, name="access_level"),
        default=AccessLevel.PUBLIC,
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<WebSource {self.url}>"
