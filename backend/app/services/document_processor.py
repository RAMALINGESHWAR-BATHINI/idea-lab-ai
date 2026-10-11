"""Document processing service: extraction, chunking, embedding.

Handles the lifecycle of a document from upload to vector-indexed chunks.
Private (non-public) document content is never sent to an external provider
when the embedding provider is cloud-based — embeddings are always generated
locally (Ollama) by default.
"""
from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import EmbeddingProvider
from app.ai.registry import get_embeddings
from app.core.config import settings
from app.core.errors import ProviderError
from app.core.logging import get_logger
from app.models.knowledge import Document, DocumentChunk
from app.models.enums import AccessLevel, DocumentProcessingStatus

logger = get_logger(__name__)

# Target tokens per chunk (roughly 4 chars/token for English).
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50
MAX_CHUNK_CHARS = CHUNK_SIZE_TOKENS * 4


@dataclass
class ProcessedChunk:
    content: str
    token_count: int
    chunk_index: int


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars per token for English)."""
    return max(1, len(text) // 4)


def extract_text_from_bytes(
    data: bytes, content_type: str, filename: str
) -> str:
    """Extract text content from uploaded file bytes.

    Supports PDF, plain text, markdown, and HTML. Binary office formats
    are not fully parsed but we extract what we can.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if content_type == "text/plain" or ext in ("txt",):
        return data.decode("utf-8", errors="replace")

    if content_type == "text/markdown" or ext == "md":
        return data.decode("utf-8", errors="replace")

    if content_type == "application/pdf" or ext == "pdf":
        try:
            import pypdf  # type: ignore
        except ImportError:
            try:
                from PyPDF2 import PdfReader  # type: ignore
                from io import BytesIO
            except ImportError:
                logger.warning("pdf_extraction_unavailable", reason="no pdf library")
                return ""
            reader = PdfReader(BytesIO(data))
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
        from io import BytesIO

        reader = pypdf.PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if content_type.startswith("text/html") or ext in ("html", "htm"):
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return data.decode("utf-8", errors="replace")
        soup = BeautifulSoup(data, "html.parser")
        return soup.get_text(separator="\n", strip=True)

    # Fallback: try to decode as text.
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = MAX_CHUNK_CHARS, overlap: int = 500) -> list[ProcessedChunk]:
    """Split text into overlapping chunks for embedding.

    Preserves paragraph boundaries where possible.
    """
    if not text.strip():
        return []

    # Normalise whitespace and split on paragraph breaks.
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[ProcessedChunk] = []
    current = ""
    index = 0

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(ProcessedChunk(
                    content=current,
                    token_count=_estimate_tokens(current),
                    chunk_index=index,
                ))
                index += 1
            # If the paragraph itself exceeds chunk_size, split it.
            if len(para) > chunk_size:
                words = para.split()
                sub_chunk = ""
                for word in words:
                    if len(sub_chunk) + len(word) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk} {word}" if sub_chunk else word
                    else:
                        if sub_chunk:
                            chunks.append(ProcessedChunk(
                                content=sub_chunk,
                                token_count=_estimate_tokens(sub_chunk),
                                chunk_index=index,
                            ))
                            index += 1
                        sub_chunk = word
                current = sub_chunk
            else:
                current = para

    if current:
        chunks.append(ProcessedChunk(
            content=current,
            token_count=_estimate_tokens(current),
            chunk_index=index,
        ))

    # Renumber after potential sub-chunking.
    for i, chunk in enumerate(chunks):
        chunk.chunk_index = i

    return chunks


async def embed_chunks(
    chunks: list[ProcessedChunk],
    embedding_provider: EmbeddingProvider | None = None,
    access_level: AccessLevel = AccessLevel.INTERNAL,
) -> list[tuple[ProcessedChunk, list[float] | None]]:
    """Embed text chunks using the configured provider.

    Returns tuples of (chunk, embedding_or_none).
    """
    if not chunks:
        return []

    if embedding_provider is None:
        embedding_provider = get_embeddings()

    # Check whether the embedding provider is cloud-based and content is private.
    provider_name = embedding_provider.name
    is_cloud = provider_name == "gemini"
    is_private = access_level not in (AccessLevel.PUBLIC,)

    if is_cloud and is_private and not settings.debug:
        logger.warning(
            "refusing_cloud_embedding_for_private_content",
            provider=provider_name,
            access_level=access_level.value,
        )
        # Return chunks without embeddings — they can't be semantically searched.
        return [(chunk, None) for chunk in chunks]

    texts = [c.content for c in chunks]
    try:
        embeddings = await embedding_provider.embed(texts)
    except ProviderError as exc:
        logger.warning("embedding_failed", error=str(exc))
        return [(chunk, None) for chunk in chunks]

    return list(zip(chunks, embeddings))


async def process_document(
    session: AsyncSession,
    document: Document,
    content: str,
    *,
    embedding_provider: EmbeddingProvider | None = None,
) -> int:
    """Process a document: chunk, embed, and store chunks.

    Returns the number of chunks created.
    """
    document.processing_status = DocumentProcessingStatus.PROCESSING
    await session.flush()

    chunks = chunk_text(content)
    if not chunks:
        document.is_indexed = False
        document.processing_status = DocumentProcessingStatus.FAILED
        await session.commit()
        return 0

    embedded = await embed_chunks(
        chunks,
        embedding_provider=embedding_provider,
        access_level=document.access_level,
    )

    # Clear any existing chunks (re-indexing).
    from sqlalchemy import delete
    await session.execute(
        delete(DocumentChunk).where(DocumentChunk.document_id == document.id)
    )

    for chunk, embedding in embedded:
        db_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            token_count=chunk.token_count,
            embedding_provider=embedding_provider.name if embedding_provider else "none",
            embedding=embedding,
            access_level=document.access_level,
        )
        session.add(db_chunk)

    document.is_indexed = all(e is not None for _, e in embedded)
    document.processing_status = (
        DocumentProcessingStatus.INDEXED
        if document.is_indexed
        else DocumentProcessingStatus.PROCESSING
    )
    await session.commit()
    return len(chunks)


def compute_file_hash(data: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(data).hexdigest()
