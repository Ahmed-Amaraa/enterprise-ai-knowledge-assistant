from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from google import genai
from backend.app.core.config import COLLECTION_NAME, GEMINI_API_KEY

model = SentenceTransformer("BAAI/bge-m3")
c = genai.Client(
    api_key=GEMINI_API_KEY
)

'''for model in c.models.list():
    print(model.name)'''

question = "What is Medianet?"

query_vector = model.encode(
    question,
    normalize_embeddings=True
).tolist()


client = QdrantClient(
    host="localhost",
    port=6333
)

results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=5
)

context = ""

for result in results.points:
    print("Score:", result.score)
    print("Source:", result.payload["source"])

    context += result.payload["text"]
    context += "\n\n"

prompt = f"""
You are an enterprise knowledge assistant.

Answer only using the context below.
If the answer is not in the context, say:
"I don't have enough information."

Context:
{context}

Question:
{question}

Answer:
"""


response = c.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
)

answer = response.text

print(answer)

client.close()
    