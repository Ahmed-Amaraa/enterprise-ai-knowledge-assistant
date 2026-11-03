from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from huggingface_hub import InferenceClient
import os
#from app.core.config import HF_TOKEN


class EmbeddingRequest(BaseModel):
    chunks: list[str] = Field(default_factory=list)


class EmbeddingResponse(BaseModel):
    embeddings: list[list[float]]


app = FastAPI()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable is not set")


# Initialize Hugging Face client once when the application starts
@app.on_event("startup")
def startup_event():
    app.state.embedding_client = InferenceClient(
        provider="hf-inference",
        api_key=HF_TOKEN,
    )

    app.state.embedding_model = "BAAI/bge-m3"


def _get_embedding_client(app: FastAPI) -> InferenceClient:
    return app.state.embedding_client


@app.post("/embeddings", response_model=EmbeddingResponse)
def generate_embeddings(payload: EmbeddingRequest):

    if not payload.chunks:
        return EmbeddingResponse(embeddings=[])

    client = _get_embedding_client(app)
    model = app.state.embedding_model

    embeddings = []

    for chunk in payload.chunks:
        embedding = client.feature_extraction(
            chunk,
            model=model,
        )

        embeddings.append(embedding.tolist())

    return EmbeddingResponse(
        embeddings=embeddings
    )


@app.get("/health")
def health():
    return {"status": "ok"}





'''
def _load_model(app: FastAPI):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="sentence-transformers is not installed in the embedding service",
        ) from exc

    app.state.model = SentenceTransformer("BAAI/bge-m3")
    return app.state.model


def _get_model(app: FastAPI):
    model = getattr(app.state, "model", None)

    if model is None:
        return _load_model(app)

    return model


@app.post("/embeddings", response_model=EmbeddingResponse)
def generate_embeddings(payload: EmbeddingRequest):
    if not payload.chunks:
        return EmbeddingResponse(embeddings=[])

    model = _get_model(app)
    embeddings = model.encode(
        payload.chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
    )

    return EmbeddingResponse(embeddings=embeddings.tolist())


@app.get("/health")
def health():
    return {"status": "ok"}'''

