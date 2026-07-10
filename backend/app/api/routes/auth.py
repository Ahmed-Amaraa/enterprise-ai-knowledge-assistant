from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    AccessTokenResponse,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    service = AuthService(UserRepository(db))

    try:
        return service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    service = AuthService(UserRepository(db))

    try:
        return service.login_user(
            email=credentials.email,
            password=credentials.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(UserRepository(db))

    try:
        return service.refresh_access_token(request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    


@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(UserRepository(db))

    try:
        return service.logout(request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )