# 🤖 Smart RAG Chatbot

An intelligent chatbot that uses Retrieval-Augmented Generation (RAG) to answer questions about your conversation history. Built with local LLM (Gemma) and semantic search using embeddings.

## 📋 Features

- **Semantic Search**: Find conversations based on meaning, not just keywords
- **Natural Language Queries**: Ask questions naturally like "Whom did I talk about cats to?"
- **User-Specific Privacy**: Each user can only see their own conversations
- **Local LLM**: Uses Gemma-1.1-7B for intelligent response generation
- **Embedding-based Retrieval**: Uses BGE-small-en for fast and accurate semantic search

## 🏗️ Architecture

```
┌─────────────┐
│   User Query│
└──────┬──────┘
       │
       v
┌─────────────────────────────┐
│  Semantic Search (RAG)      │
│  - Embed query              │
│  - Find similar messages    │
│  - Filter by user           │
└──────────┬──────────────────┘
           │
           v
┌─────────────────────────────┐
│  MongoDB Database           │
│  - conversations collection │
│  - embeddings collection    │
└──────────┬──────────────────┘
           │
           v
┌─────────────────────────────┐
│  LLM Response Generation    │
│  - Context from retrieval   │
│  - Natural language answer  │
└──────────┬──────────────────┘
           │
           v
    ┌──────────┐
    │ Response │
    └──────────┘
```

## 🗄️ Database Schema

### Conversations Collection
```javascript
{
  _id: ObjectId,
  conv_id: String,
  sender_id: String,
  receiver_id: String,
  sender_name: String,
  receiver_name: String,
  message: String,
  timestamp: ISODate
}
```

### Embeddings Collection
```javascript
{
  _id: ObjectId,  // Same as conversation _id
  embedding: Array[Float],  // 384-dimensional vector
  sender_id: String,
  receiver_id: String,
  timestamp: ISODate,
  message: String
}
```

## 📦 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up MongoDB

Make sure MongoDB is running on `localhost:27017` with a database named `chatbotDB` containing:
- `conversations` collection with your chat data
- `embeddings` collection (will be populated)

### 3. Verify Model Files

Ensure you have:
- LLM model at: `LLM/gemma-1.1-7b-it.Q4_K_M.gguf`
- Embedding model at: `models/embeddings/bge-small-en/`

## 🚀 Usage

### Step 1: Generate Embeddings (First Time Only)

Before using the chatbot, generate embeddings for your conversations:

```bash
python embeddings.py
```

This will:
- Read all messages from the `conversations` collection
- Generate embeddings using the BGE-small-en model
- Store them in the `embeddings` collection

### Step 2: Run the Smart Chatbot

#### Interactive Mode

```bash
python smart_chatbot.py
```

Or specify your user ID directly:

```bash
python smart_chatbot.py u_1010
```

#### Example Queries

```
Whom did I talk about cats to?
What did I discuss with Anas about work?
When did I last mention vacation?
Show me conversations about programming
Who asked me about my weekend plans?
```

### Step 3: Test Basic RAG (Optional)

Test the basic retrieval system without LLM:

```bash
python rag.py
```

## 📁 File Structure

```
SmartApp_Clone/
├── db.py                    # MongoDB connection setup
├── embeddings.py            # Generate and store embeddings
├── rag.py                   # Core RAG retrieval logic
├── llm_service.py           # LLM integration (Gemma)
├── smart_chatbot.py         # Main chatbot application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LLM/
│   └── gemma-1.1-7b-it.Q4_K_M.gguf
└── models/
    └── embeddings/
        └── bge-small-en/    # Embedding model files
```

## 🔧 Configuration

### Database Configuration (`db.py`)

```python
# MongoDB connection string
client = MongoClient("mongodb://localhost:27017/")
db = client["chatbotDB"]
```

### LLM Configuration (`llm_service.py`)

```python
# Adjust these parameters based on your hardware
n_ctx=4096,        # Context window size
n_threads=4,       # CPU threads
n_gpu_layers=0,    # GPU layers (0 for CPU only)
```

### Retrieval Configuration (`rag.py`)

```python
# Adjust number of results retrieved
top_k=10  # Number of most similar messages to retrieve
```

## 💡 How It Works

### 1. **Embedding Generation**
- Each message is converted to a 384-dimensional vector using BGE-small-en
- Vectors capture semantic meaning of the text
- Stored in MongoDB for fast retrieval

### 2. **Semantic Search**
- User query is converted to the same embedding space
- Cosine similarity computed between query and all messages
- Messages filtered to show only user's conversations
- Top-K most similar messages retrieved

### 3. **Response Generation**
- Retrieved messages provide context
- Prompt engineered for Gemma model
- LLM generates natural language answer
- Response includes relevant names, dates, and details

## 🎯 Example Interaction

```
🤖 SMART RAG CHATBOT - Interactive Mode
======================================================================

Welcome, Hadi!

Hadi 💬: whom did I talk about cats to?

Processing query: 'whom did I talk about cats to?'
[Step 1] Searching for relevant conversations...
Found 5 relevant messages
[Step 2] Enriching results with user names...
[Step 3] Generating response using LLM...

🤖 Chatbot: Based on your conversation history, you talked about cats 
with Anas Abdullah on October 23rd, 2025. You mentioned that your cat 
sleeps 14-16 hours a day and asked why cats sleep so much.

----------------------------------------------------------------------
```

## 🔒 Privacy & Security

- **User Isolation**: Each user can only query their own conversations
- **Local Processing**: All AI processing happens locally (no external API calls)
- **MongoDB Access Control**: Ensure proper MongoDB authentication in production

## ⚡ Performance Tips

1. **GPU Acceleration**: If you have a GPU, increase `n_gpu_layers` in `llm_service.py`
2. **Batch Embeddings**: Run `embeddings.py` periodically to embed new messages
3. **Index MongoDB**: Create indexes on `sender_id` and `receiver_id` in embeddings collection:

```javascript
db.embeddings.createIndex({ "sender_id": 1 })
db.embeddings.createIndex({ "receiver_id": 1 })
```

## 🐛 Troubleshooting

### "No module named 'llama_cpp'"
```bash
pip install llama-cpp-python
```

### "Model not found"
Check that model paths in the code match your actual file locations.

### "MongoDB connection refused"
Ensure MongoDB is running:
```bash
sudo systemctl start mongod
```

### Out of memory with LLM
Reduce `n_ctx` or use a smaller quantized model.

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Voice query input
- [ ] Web interface
- [ ] Real-time embedding updates
- [ ] Advanced filtering (date ranges, specific users)
- [ ] Conversation summarization
- [ ] Export conversation threads

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

Built with ❤️ using Python, MongoDB, Sentence Transformers, and Llama.cpp

# RAG_BACKEND
