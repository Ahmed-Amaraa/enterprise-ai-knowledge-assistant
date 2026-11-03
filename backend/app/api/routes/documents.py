from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    try:
        document = service.upload_document(file, user_id=current_user.id)
        background_tasks.add_task(service.process_document_background, document.id)
        return document
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = DocumentService(db)
    return DocumentListResponse(
        documents=service.list_documents(
            user_id=user_id,
            skip=skip,
            limit=limit,
            search=search,
        )
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    try:
        return service.get_document(document_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{document_id}", response_model=DocumentResponse)
async def rename_document(
    document_id: int,
    payload: DocumentUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    try:
        return service.rename_document(document_id, payload.title, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    try:
        service.delete_document(document_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return {"message": "Document deleted successfully"}