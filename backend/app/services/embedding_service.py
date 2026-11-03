import httpx
import time

from app.core.config import EMBEDDING_SERVICE_URL


class EmbeddingService:

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or EMBEDDING_SERVICE_URL).rstrip("/")
        self.client = httpx.Client(timeout=300.0)


    def close(self):
        self.client.close()


    def generate_embeddings(
        self,
        chunks: list[str],
    ) -> list[list[float]]:

        if not chunks:
            return []

        last_error: Exception | None = None

        for attempt in range(5):
            try:
                response = self.client.post(
                    f"{self.base_url}/embeddings",
                    json={"chunks": chunks},
                )
                response.raise_for_status()

                payload = response.json()
                return payload["embeddings"]
            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                last_error = exc
                if attempt == 4:
                    break

                time.sleep(2 ** attempt)

        raise RuntimeError("Embedding service is not reachable") from last_error