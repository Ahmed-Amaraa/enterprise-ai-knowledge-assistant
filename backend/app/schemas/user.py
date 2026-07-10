from pydantic import BaseModel, EmailStr
from datetime import datetime



class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # important for ORM (SQLAlchemy)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

