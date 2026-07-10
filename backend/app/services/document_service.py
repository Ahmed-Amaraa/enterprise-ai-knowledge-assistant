import os

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import ALLOWED_FILE_TYPES
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.file_storage import save_file


class DocumentService:

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)

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
            status="uploaded",
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