#!/usr/bin/env python3

from sentence_transformers import SentenceTransformer
from db import get_db


# Load local embedding model (same as in rag.py)
print("Loading embedding model...")
model = SentenceTransformer('/home/it-admin/Desktop/SmartApp_Clone/EmbedModel')
print("Embedding model loaded!")


def clear_old_embeddings():
    db = get_db()
    embeddings = db["embeddings"]
    deleted = embeddings.delete_many({})
    print(f"🗑️ Deleted {deleted.deleted_count} old embeddings.")


def generate_and_store_embeddings():
    db = get_db()
    conversations = db["conversations"]
    embeddings = db["embeddings"]

    print("🔍 Fetching messages...")
    messages = list(conversations.find())

    print(f"Found {len(messages)} messages. Generating embeddings...\n")

    for msg in messages:
        message_id = msg["_id"]
        text = msg["message"]

        # Generate embedding (same encoding as rag.py)
        vector = model.encode(text).tolist()

        embeddings.insert_one({
            "_id": message_id,
            "embedding": vector,
            "sender_id": msg["sender_id"],
            "receiver_id": msg["receiver_id"],
            "timestamp": msg["timestamp"],
            "message": text,
        })

        print(f"✅ Stored embedding for message ID: {message_id}")

    print("\n🎉 Embedding generation complete!")


if __name__ == "__main__":
    clear_old_embeddings()
    generate_and_store_embeddings()
