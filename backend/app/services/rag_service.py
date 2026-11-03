import time

from google import genai
from google.genai.errors import ServerError
from qdrant_client import QdrantClient

from app.core.config import (
    COLLECTION_NAME,
    GEMINI_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from app.processing.preprocessing import clean_text
from app.processing.chunking import split_text
from .embedding_service import EmbeddingService


class RagService:

    def __init__(self):

        # Gemini client
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        # Qdrant client
        self.qdrant_client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        # Embedding service
        self.embedding_service = EmbeddingService()

    # --------------------------------------------------
    # 1. CLEAN + CHUNK
    # --------------------------------------------------

    def chunk(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ) -> list[str]:

        cleaned_text = clean_text(text)

        return split_text(
            cleaned_text,
            chunk_size,
            chunk_overlap,
        )

    # --------------------------------------------------
    # 2. GENERATE QUERY EMBEDDING
    # --------------------------------------------------

    def embed_query(
        self,
        question: str,
    ) -> list[float]:

        embeddings = self.embedding_service.generate_embeddings(
            [question]
        )

        if not embeddings:
            raise ValueError(
                "Embedding service returned no embeddings."
            )

        return embeddings[0]

    # --------------------------------------------------
    # 3. SEARCH QDRANT
    # --------------------------------------------------

    def search_chunks(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ):

        response = self.qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        )

        return response.points

    # --------------------------------------------------
    # 4. BUILD CONTEXT
    # --------------------------------------------------

    def build_context(
        self,
        results,
        min_score: float = 0.35,
    ) -> str:

        context_parts = []

        for i, result in enumerate(results, 1):

            # Same behavior as standalone script
            if result.score < min_score:
                continue

            payload = result.payload or {}

            source = payload.get(
                "source",
                "Unknown",
            )

            text = payload.get(
                "text",
                "",
            )

            context_parts.append(
                f"""
[Chunk {i}]
Source: {source}

Text:
{text}
"""
            )

        return "\n\n".join(context_parts)

    # --------------------------------------------------
    # 5. BUILD PROMPT
    # --------------------------------------------------

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:

        return f"""
            You are an enterprise knowledge assistant.

            Your task is to answer the user's question using ONLY the provided context.

            Rules:
            1. Do not use outside knowledge.
            2. Do not invent or infer facts that are not supported by the context.
            3. If the context does not contain enough information to answer the question, respond exactly:
            "I don't have enough information."
            4. Give a concise and accurate answer.
            5. When possible, mention the source of the information.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """


    # --------------------------------------------------
    # 6. GENERATE ANSWER
    # --------------------------------------------------

    def generate_answer(
        self,
        prompt: str,
        model: str = "gemini-3-flash-preview",
    ) -> str:

        retries = 5

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                return response.text

            except ServerError as exc:

                if "503" not in str(exc):
                    raise

                wait = 2 ** attempt

                print(
                    f"Gemini busy. "
                    f"Retrying in {wait}s..."
                )

                time.sleep(wait)

        raise RuntimeError(
            "Gemini unavailable after retries"
        )

    # --------------------------------------------------
    # 7. COMPLETE RAG PIPELINE
    # --------------------------------------------------

    def answer_question(
        self,
        question: str,
    ) -> str:

        # Step 1
        query_vector = self.embed_query(
            question
        )

        # Step 2
        results = self.search_chunks(
            query_vector=query_vector,
            top_k=5,
        )

        # Step 3
        context = self.build_context(
            results,
            min_score=0.5,
        )

        # Step 4
        prompt = self.build_prompt(
            question=question,
            context=context,
        )

        # Step 5
        answer = self.generate_answer(
            prompt=prompt,
        )

        return answer