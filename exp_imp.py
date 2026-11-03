from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


'''client = QdrantClient(
    host="localhost",
    port=6333
)'''


client = QdrantClient(path="./qdrant_data")

collection_name = "enterprise_documents"

scroll = client.scroll(
    collection_name=collection_name,
    limit=5000,
    with_vectors=True,
    with_payload=True,
)

points = scroll[0]

print(f'len(points): {len(points)}')


new_points = [
    PointStruct(
        id=p.id,
        vector=p.vector,
        payload=p.payload,
    )
    for p in points
]

docker_client = QdrantClient(
    host="localhost",
    port=6333
)

'''collections = docker_client.get_collections()

for c in collections.collections:
    print(c.name)'''

if docker_client.collection_exists("enterprise_documents"):
    docker_client.delete_collection("enterprise_documents")
docker_client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=1024,   # BGE-M3 embedding dimension
        distance=Distance.COSINE,
    ),
)

docker_client.upsert(
    collection_name=collection_name,
    points=new_points,
)

print(f'Collection "{collection_name}" created and points upserted successfully.')


client.close()