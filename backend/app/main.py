from fastapi import FastAPI
from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, SessionLocal
import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.rag import router as rag_router
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.vector_store import VectorStore
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE documents ALTER COLUMN user_id DROP NOT NULL"))
        connection.execute(text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS feedback VARCHAR(16)"))

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

    app.state.vector_store = VectorStore()

    # Application startup
    #print("Application started")

    yield

    # Application shutdown
    #print("Closing Qdrant client")
    app.state.vector_store.close()

app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(rag_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}