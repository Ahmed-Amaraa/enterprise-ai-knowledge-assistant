import os

SECRET_KEY = ""
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
}

CHUNK_SIZE = 514
CHUNK_OVERLAP = 100

COLLECTION_NAME = "enterprise_documents"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_SERVICE_URL = "http://embedding-service:8001"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HF_Token = os.getenv("HF_Token")