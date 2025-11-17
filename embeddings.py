#!/usr/bin/env python3

from sentence_transformers import SentenceTransformer
from db import get_db
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from bson import ObjectId

# Load local embedding model (same as in rag.py)
print("Loading embedding model...")
model = SentenceTransformer('/home/it-admin/Desktop/SmartApp_Clone/EmbedModel')
print(f"Embedding model loaded! Dimension: {model.get_sentence_embedding_dimension()}")

# Connect to Qdrant
print("Connecting to Qdrant...")
qdrant = QdrantClient(url="http://localhost:6333")
print("Connected to Qdrant!")

COLLECTION_NAME = "embeddings"


def clear_old_embeddings():
    """Clear old embeddings from Qdrant"""
    try:
        qdrant.delete_collection(collection_name=COLLECTION_NAME)
        print(f"🗑️ Deleted old '{COLLECTION_NAME}' collection from Qdrant.")
    except Exception as e:
        print(f"Note: Collection might not exist yet: {e}")


def generate_and_store_embeddings():
    """Generate embeddings and store in Qdrant"""
    db = get_db()
    conversations = db["conversations"]

    print("🔍 Fetching messages from MongoDB...")
    messages = list(conversations.find())

    print(f"Found {len(messages)} messages. Generating embeddings...\n")

    points = []
    for idx, msg in enumerate(messages):
        message_id = str(msg["_id"])  # Convert ObjectId to string
        text = msg["message"]

        # Generate embedding (same encoding as rag.py)
        vector = model.encode(text).tolist()

        # Create Qdrant point with payload containing metadata
        point = PointStruct(
            id=idx,  # Qdrant uses integer IDs
            vector=vector,
            payload={
                "message_id": message_id,
                "message": text,
                "sender_id": msg["sender_id"],
                "receiver_id": msg["receiver_id"],
                "timestamp": msg["timestamp"].isoformat() if hasattr(msg.get("timestamp"), "isoformat") else str(msg.get("timestamp")),
            }
        )
        points.append(point)

        print(f"✅ Prepared embedding {idx+1}/{len(messages)} for message ID: {message_id}")

    # Batch upsert to Qdrant
    print(f"\n📤 Uploading {len(points)} embeddings to Qdrant...")
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    print("\n🎉 Embedding generation and upload complete!")
    print(f"📊 Total embeddings in Qdrant: {qdrant.count(collection_name=COLLECTION_NAME).count}")


if __name__ == "__main__":
    #clear_old_embeddings()
    generate_and_store_embeddings()
