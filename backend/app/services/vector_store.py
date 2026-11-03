import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.core.config import (
    COLLECTION_NAME,
    QDRANT_HOST,
    QDRANT_PORT,
)


class VectorStore:

    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

    def add_document_chunks(
        self,
        document_id: int,
        source: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:

        points = []

        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

            points.append(
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"document:{document_id}:chunk:{index}")),
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "chunk_index": index,
                        "source": source,
                        "text": chunk,
                        "type": "uploaded_document",
                    },
                )
            )

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    def close(self):
        self.client.close()