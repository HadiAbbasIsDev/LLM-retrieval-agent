from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
import re

# DB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["chatbotDB"]
embed_col = db["embeddings"]
conv_col = db["conversations"]

# Load local embedding model
model = SentenceTransformer("/home/it-admin/Desktop/SmartApp_Clone/EmbedModel")

# Load cross-encoder for re-ranking (lightweight, accurate)
print("Loading re-ranker model...")
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
print("Re-ranker loaded!")

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def extract_keywords(text):
    """Extract keywords from query (simple approach)"""
    # Remove common words
    stop_words = {'i', 'me', 'my', 'we', 'our', 'did', 'do', 'does', 'have', 'has', 
                  'is', 'are', 'was', 'were', 'to', 'the', 'a', 'an', 'with', 'about',
                  'anyone', 'someone', 'talk', 'talked', 'discuss', 'discussed'}
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords

def keyword_match_score(query, message):
    """Calculate keyword match score between query and message"""
    query_keywords = extract_keywords(query)
    
    if not query_keywords:
        return 0.0
    
    message_lower = message.lower()
    matches = sum(1 for kw in query_keywords if kw in message_lower)
    
    return matches / len(query_keywords)

def search_messages(query, top_k=5, user_id=None, min_similarity=0.3):
    """
    Search for messages based on semantic similarity.
    
    Args:
        query: The search query
        top_k: Number of top results to return
        user_id: Filter results to only conversations involving this user
        min_similarity: Minimum similarity threshold (0-1). Default 0.3
    """
    # Embed the user query
    query_embed = model.encode(query).tolist()

    results = []

    # Build filter query for user-specific search
    filter_query = {}
    if user_id:
        filter_query = {
            "$or": [
                {"sender_id": user_id},
                {"receiver_id": user_id}
            ]
        }

    # Compare with filtered embeddings
    for emb in embed_col.find(filter_query):
        sim = cosine_similarity(query_embed, emb["embedding"])
        
        # Calculate keyword match score as additional signal
        kw_score = keyword_match_score(query, emb["message"])
        
        # Hybrid score: semantic similarity boosted by keyword match
        # If keywords match well, lower the semantic threshold requirement
        hybrid_score = sim
        if kw_score > 0.5:  # If more than 50% of keywords match
            hybrid_score = sim*0.6 + kw_score*0.4
        
        # Only include if hybrid score is above threshold
        if hybrid_score >= min_similarity or (hybrid_score >= 0.25):
            results.append({
                "conversation_id": emb["_id"],
                "message": emb["message"],
                "sender_id": emb["sender_id"],
                "receiver_id": emb["receiver_id"],
                "timestamp": emb.get("timestamp"),
                "similarity": float(sim),
                "keyword_score": float(kw_score),
                "hybrid_score": float(hybrid_score)
            })

    # Sort by hybrid score and get top candidates for re-ranking
    results = sorted(results, key=lambda x: x.get("hybrid_score", x["similarity"]), reverse=True)[:top_k * 2]
    
    if not results:
        return []
    
    # Re-rank using cross-encoder for better relevance
    # Cross-encoder looks at query+document together (more accurate than bi-encoder)
    query_doc_pairs = [[query, result["message"]] for result in results]
    rerank_scores = reranker.predict(query_doc_pairs)
    
    # Add rerank scores to results
    for i, result in enumerate(results):
        result["rerank_score"] = float(rerank_scores[i])
    
    # Filter by rerank score threshold (cross-encoder scores range from -10 to 10)
    # Keep results with score > -1.0 (allows relevant results through)
    filtered_results = [r for r in results if r["rerank_score"] > -1.0]
    
    # Sort by rerank score (this is the most accurate ranking)
    filtered_results = sorted(filtered_results, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
    
    return filtered_results

def group_by_user(results, current_user_id):
    user_map = {}

    for r in results:
        # Determine the other person in the chat
        if r["sender_id"] == current_user_id:
            other = r["receiver_id"]
        else:
            other = r["sender_id"]

        if other not in user_map:
            user_map[other] = []

        user_map[other].append(r)

    return user_map

def get_user_name(user_id):
    """Get user name from conversations collection"""
    # Try to find as sender
    conv = conv_col.find_one({"sender_id": user_id})
    if conv:
        return conv.get("sender_name", user_id)
    
    # Try to find as receiver
    conv = conv_col.find_one({"receiver_id": user_id})
    if conv:
        return conv.get("receiver_name", user_id)
    
    return user_id

if __name__ == "__main__":
    query = input("Search: ")
    current_user = input("Your user ID (e.g., u_1010): ")
    
    raw_results = search_messages(query, user_id=current_user)
    grouped = group_by_user(raw_results, current_user_id=current_user)

    print("\nGrouped Results by User:")
    for user, msgs in grouped.items():
        user_name = get_user_name(user)
        print(f"\n{user_name} ({user}): {len(msgs)} matches")
        for msg in msgs:
            print(f"  - {msg['message'][:100]}... (similarity: {msg['similarity']:.3f})")