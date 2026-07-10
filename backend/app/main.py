from fastapi import FastAPI
from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, SessionLocal
import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE documents ALTER COLUMN user_id DROP NOT NULL"))

    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()

        if not demo_user:
            auth_service = AuthService(UserRepository(db))
            auth_service.register_user(
                email="demo@example.com",
                username="demo",
                password="demo1234",
                full_name="Demo User",
            )
    finally:
        db.close()


app.include_router(auth_router)
app.include_router(documents_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}