import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import ALLOWED_FILE_TYPES
from app.db.session import SessionLocal
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.file_storage import save_file

from app.processing.parsers.parser import extract_text
from app.processing.preprocessing import clean_text
from app.processing.chunking import split_text
from .embedding_service import EmbeddingService
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP

from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository

from .vector_store import VectorStore
from .image_description_service import ImageDescriptionService


class DocumentService:

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService()
        self.image_description_service = ImageDescriptionService()

    def upload_document(
        self,
        file: UploadFile,
        user_id: int | None = None,
    ) -> Document:
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise ValueError("Unsupported file type")

        file_path = save_file(file)
        file_type = ALLOWED_FILE_TYPES[file.content_type]
        file_size = os.path.getsize(file_path)
        title = file.filename or os.path.basename(file_path)

        document = Document(
            user_id=user_id,
            title=title,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            status="processing",
        )

        return self.document_repo.create_document(document)

    def get_document(
        self,
        document_id: int,
    ) -> Document:
        return self._get_document_or_raise(document_id)

    def list_documents(
        self,
        user_id: int | None = None,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[Document]:
        if search:
            return self.document_repo.search_documents(
                query=search,
                user_id=user_id,
                skip=skip,
                limit=limit,
            )

        if user_id is None:
            return self.document_repo.get_all_documents(skip=skip, limit=limit)

        return self.document_repo.get_documents_by_user(user_id, skip=skip, limit=limit)

    def rename_document(
        self,
        document_id: int,
        title: str,
        user_id: int,
    ) -> Document:
        document = self._get_document_or_raise(document_id)

        if document.user_id != user_id:
            raise PermissionError("You do not own this document")

        document.title = title
        return self.document_repo.update_document(document)

    def delete_document(
        self,
        document_id: int,
        user_id: int,
    ) -> None:
        document = self._get_document_or_raise(document_id)

        if document.user_id != user_id:
            raise PermissionError("You do not own this document")

        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)

        self.document_repo.delete_document(document)

    def _get_document_or_raise(self, document_id: int) -> Document:
        document = self.document_repo.get_document_by_id(document_id)

        if not document:
            raise ValueError("Document not found")

        return document

    
    def process_document(
        self,
        document: Document,
    ) -> None:
        """
        Extract and clean document text.
        """

        text = extract_text(document.file_path)

        text = clean_text(text)

        image_descriptions = self.image_description_service.describe_document_images(
            document.file_path
        )
        if image_descriptions:
            text = f"{text}\n\n{image_descriptions}" if text else image_descriptions

        chunks = split_text(
            text,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        embeddings = self.embedding_service.generate_embeddings(chunks)

        self.vector_store.add_document_chunks(
            document_id=document.id,
            source=document.title,
            chunks=chunks,
            embeddings=embeddings,
        )

        document.status = "processed"
        self.document_repo.update_document(document)

    def process_document_background(self, document_id: int) -> None:
        background_db = SessionLocal()
        background_service = DocumentService(background_db)
        try:
            document = background_service._get_document_or_raise(document_id)
            background_service.process_document(document)
        except Exception:
            try:
                failed_document = background_service._get_document_or_raise(document_id)
                failed_document.status = "failed"
                background_service.document_repo.update_document(failed_document)
            except Exception:
                pass
            raise
        finally:
            background_db.close()

        #vector_store.close()

        '''chunk_objects = []

        for chunk_text, embedding in zip(chunks, embeddings):

            chunk_objects.append(
                Chunk(
                    document_id=document.id,
                    content=chunk_text,
                    embedding_vector=embedding,
                )
            )

        self.chunk_repository.create_chunks(
            chunk_objects
        )'''