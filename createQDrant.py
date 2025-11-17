from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

# Load model to get correct dimension
model = SentenceTransformer('/home/it-admin/Desktop/SmartApp_Clone/EmbedModel')
vector_size = model.get_sentence_embedding_dimension()

print(f"Creating collection with vector size: {vector_size}")

client = QdrantClient(url="http://localhost:6333")

client.recreate_collection(
    collection_name="embeddings",
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
)

print(f"✅ Collection 'embeddings' created with dimension {vector_size}!")
