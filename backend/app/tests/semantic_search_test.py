from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import time
from google.genai.errors import ServerError
from google import genai
from app.core.config import (
    COLLECTION_NAME,
    GEMINI_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
)

def generate_answer(client, model, prompt):

    retries = 5

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text

        except ServerError as e:
            if "503" in str(e):
                wait = 2 ** attempt
                print(f"Gemini busy. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e

    raise Exception("Gemini unavailable after retries")




model = SentenceTransformer("BAAI/bge-m3")
c = genai.Client(
    api_key=GEMINI_API_KEY
)

'''for model in c.models.list():
    print(model.name)'''

#question = "What is Medianet?"
question = "Citer les Critères de segmentation ?"

query_vector = model.encode(
    question,
    normalize_embeddings=True
).tolist()


client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)

'''collections = client.get_collections()

for c in collections.collections:
    print(c.name)'''

results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=5
)

context = ""

for result in results.points:
    print("Score:", result.score)
    print("Source:", result.payload["source"])
    if result.score < 0.5:
        continue
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


'''response = c.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
)

answer = response.text

print(answer)

client.close()'''

m = "gemini-3-flash-preview"

text = generate_answer(c, m, prompt)

print("Generated answer:\n", text)