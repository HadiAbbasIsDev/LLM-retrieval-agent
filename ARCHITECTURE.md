# 🏗️ Smart RAG Chatbot - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SMART RAG CHATBOT                              │
│                                                                       │
│  User Query: "Whom did I talk about cats to?"                       │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. Natural Language Understanding                            │  │
│  │     - Parse user intent                                       │  │
│  │     - Extract key entities (user, topic, time)               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                   EMBEDDING & RETRIEVAL LAYER                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  2. Query Embedding (BGE-small-en)                           │  │
│  │     "cats" → [0.23, -0.45, 0.67, ..., 0.12] (384-dim)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             │                                        │
│                             v                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  3. Semantic Search (Cosine Similarity)                      │  │
│  │     - Compare with all user's message embeddings            │  │
│  │     - Filter: (sender_id = user OR receiver_id = user)      │  │
│  │     - Rank by similarity score                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  MongoDB: chatbotDB                                          │  │
│  │                                                              │  │
│  │  Collection: conversations                                   │  │
│  │  ┌────────────────────────────────────────────────────┐    │  │
│  │  │ _id, conv_id, sender_id, receiver_id,             │    │  │
│  │  │ sender_name, receiver_name, message, timestamp     │    │  │
│  │  └────────────────────────────────────────────────────┘    │  │
│  │                                                              │  │
│  │  Collection: embeddings                                      │  │
│  │  ┌────────────────────────────────────────────────────┐    │  │
│  │  │ _id, embedding[384], sender_id, receiver_id,       │    │  │
│  │  │ timestamp, message                                  │    │  │
│  │  └────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                   CONTEXT ENRICHMENT LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  4. Retrieve Top-K Messages (k=10)                          │  │
│  │     Result 1: "cats sleep 14-16 hours" (similarity: 0.89)   │  │
│  │     Result 2: "my cat is lazy" (similarity: 0.76)           │  │
│  │     ...                                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             │                                        │
│                             v                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  5. Group by Conversation Partner                           │  │
│  │     Anas Abdullah (u_1002): 3 matches                       │  │
│  │     John Doe (u_1003): 1 match                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                   LLM GENERATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  6. Prompt Construction                                      │  │
│  │     ┌────────────────────────────────────────────────┐      │  │
│  │     │ System: You are a helpful assistant...         │      │  │
│  │     │ User: Hadi                                      │      │  │
│  │     │ Question: Whom did I talk about cats to?       │      │  │
│  │     │ Context:                                        │      │  │
│  │     │   1. Conversation with Anas: "cats sleep..."   │      │  │
│  │     │   2. Conversation with Anas: "my cat..."       │      │  │
│  │     └────────────────────────────────────────────────┘      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             │                                        │
│                             v                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  7. LLM Response Generation (Gemma-1.1-7B)                  │  │
│  │     Model: gemma-1.1-7b-it.Q4_K_M.gguf                      │  │
│  │     Context: 4096 tokens                                     │  │
│  │     Temperature: 0.7                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             v
┌────────────────────────────────────────────────────────────────────┐
│                       RESPONSE LAYER                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  8. Natural Language Response                                │  │
│  │                                                              │  │
│  │  "Based on your conversation history, you talked about      │  │
│  │   cats with Anas Abdullah on October 23rd, 2025. You        │  │
│  │   mentioned that your cat sleeps 14-16 hours a day and      │  │
│  │   asked why cats sleep so much."                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Embedding Model (BGE-small-en)
- **Type**: Sentence Transformer
- **Dimension**: 384
- **Purpose**: Convert text to semantic vectors
- **Location**: `models/embeddings/bge-small-en/`
- **Speed**: ~100 embeddings/second on CPU

### 2. Vector Search
- **Algorithm**: Cosine Similarity
- **Formula**: `similarity = dot(a, b) / (||a|| * ||b||)`
- **Range**: -1 to 1 (higher = more similar)
- **Threshold**: Typically > 0.6 for relevance

### 3. LLM (Gemma-1.1-7B)
- **Type**: Instruction-tuned language model
- **Quantization**: Q4_K_M (4-bit)
- **Size**: ~4.5 GB
- **Location**: `LLM/gemma-1.1-7b-it.Q4_K_M.gguf`
- **Context Window**: 4096 tokens
- **Framework**: llama.cpp via Python bindings

### 4. Database (MongoDB)
- **Database**: chatbotDB
- **Collections**: 
  - `conversations`: Raw chat messages
  - `embeddings`: Vector representations
- **Indexes**: 
  - `sender_id`: For user filtering
  - `receiver_id`: For user filtering

## Data Flow

### Offline Phase (Pre-processing)
```
MongoDB Conversations
        ↓
  [embeddings.py]
        ↓
   BGE-small-en
        ↓
  384-dim vectors
        ↓
MongoDB Embeddings
```

### Online Phase (Query Processing)
```
User Query
    ↓
Embedding Generation
    ↓
Vector Search (with user filter)
    ↓
Top-K Retrieval
    ↓
Context Building
    ↓
LLM Generation
    ↓
Response
```

## Privacy & Security

### User Isolation
```python
# MongoDB query ensures users only see their own data
filter_query = {
    "$or": [
        {"sender_id": user_id},
        {"receiver_id": user_id}
    ]
}
```

### Local Processing
- ✓ All embeddings generated locally
- ✓ All LLM inference runs locally
- ✓ No external API calls
- ✓ No data leaves your machine

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate single embedding | ~10ms | BGE-small-en on CPU |
| Search 1000 embeddings | ~50ms | Cosine similarity |
| LLM first load | ~5-10s | Loading 4GB model |
| LLM generation (100 tokens) | ~5-15s | Depends on CPU |
| End-to-end query | ~8-20s | First query (includes load time) |
| Subsequent queries | ~3-8s | Model already loaded |

## Scalability Considerations

### Current Implementation
- ✓ Works well for: <100K messages
- ⚠ May be slow for: >1M messages
- ✗ Not suitable for: >10M messages

### Optimization Options

1. **Vector Database**
   - Replace cosine similarity loop with FAISS/Annoy
   - Sub-millisecond search for millions of vectors

2. **Batch Processing**
   - Generate embeddings in batches
   - Process multiple queries in parallel

3. **Caching**
   - Cache frequently accessed embeddings
   - Cache LLM responses for common queries

4. **GPU Acceleration**
   - Enable GPU layers in LLM
   - Use GPU for embedding generation

## Extension Points

### 1. Add New Data Sources
```python
# In embeddings.py
def generate_from_source(source_name):
    # Fetch data from new source
    # Generate embeddings
    # Store in MongoDB
```

### 2. Custom Retrieval Strategies
```python
# In rag.py
def search_with_filters(query, filters):
    # Time range filtering
    # Topic filtering
    # User group filtering
```

### 3. Multi-modal Support
```python
# Future enhancement
def embed_image(image_path):
    # Use CLIP or similar
    # Generate image embeddings
```

## Technology Stack

```
┌─────────────────────────────────────┐
│     Application Layer                │
│  - smart_chatbot.py (Main UI)       │
│  - example_usage.py (Examples)      │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│     Business Logic Layer             │
│  - rag.py (Retrieval)               │
│  - llm_service.py (Generation)      │
│  - embeddings.py (Pre-processing)   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│     Data Layer                       │
│  - db.py (MongoDB connector)        │
│  - MongoDB (Data storage)           │
└─────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────┐
│     Model Layer                      │
│  - BGE-small-en (Embeddings)        │
│  - Gemma-1.1-7B (LLM)              │
└─────────────────────────────────────┘
```

## File Responsibilities

| File | Purpose | Dependencies |
|------|---------|--------------|
| `db.py` | MongoDB connection | pymongo |
| `embeddings.py` | Generate embeddings | db.py, sentence-transformers |
| `rag.py` | Semantic search | db.py, numpy |
| `llm_service.py` | LLM inference | llama-cpp-python |
| `smart_chatbot.py` | Main application | All above |
| `test_setup.py` | Verification | All modules |
| `example_usage.py` | Usage examples | smart_chatbot.py |

---

For implementation details, see the source code and comments in each file.

