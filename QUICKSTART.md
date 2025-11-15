# 🚀 Quick Start Guide

## Setup (First Time Only)

### Option 1: Quick Install (Recommended)
```bash
./install.sh
```

This will install CPU-only versions (no CUDA) of all dependencies.

### Option 2: Manual Install
```bash
# Install PyTorch CPU-only first
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install other packages
pip install pymongo==4.6.1 numpy==1.24.3 sentence-transformers>=2.3.1 llama-cpp-python>=0.2.32
```

### Verify Setup
```bash
python3 test_setup.py
```

## Usage

### Basic Usage
```bash
# Start chatbot (will ask for user ID)
python3 smart_chatbot.py

# Start with specific user
python3 smart_chatbot.py u_1010
```

### Example Queries
```
Whom did I talk about cats to?
What did I discuss with Anas?
When did I last mention work?
Show me conversations about vacation
```

### Run Examples
```bash
python3 example_usage.py
```

## File Overview

| File | Purpose |
|------|---------|
| `smart_chatbot.py` | 🤖 Main chatbot application |
| `rag.py` | 🔍 Retrieval and search logic |
| `llm_service.py` | 🧠 LLM integration (Gemma) |
| `embeddings.py` | 📊 Generate embeddings |
| `db.py` | 🗄️ Database connection |
| `test_setup.py` | ✅ Verify setup |
| `example_usage.py` | 📚 Usage examples |

## Common Commands

```bash
# Generate embeddings for new messages
python3 embeddings.py

# Test RAG retrieval only (no LLM)
python3 rag.py

# Run chatbot interactively
python3 smart_chatbot.py u_1010

# See usage examples
python3 example_usage.py
```

## Troubleshooting

### MongoDB not running
```bash
sudo systemctl start mongod
# or
sudo service mongod start
```

### Missing dependencies
```bash
pip install -r requirements.txt
```

### No embeddings found
```bash
python3 embeddings.py
```

## Architecture Flow

```
User Query
    ↓
[Embedding Generation]
    ↓
[Semantic Search in MongoDB]
    ↓
[Retrieve Top-K Matches]
    ↓
[Filter by User]
    ↓
[LLM Context Building]
    ↓
[Response Generation]
    ↓
Natural Language Answer
```

## Example Session

```bash
$ python3 smart_chatbot.py u_1010

🤖 SMART RAG CHATBOT - Interactive Mode
======================================================================

Welcome, Hadi!

Hadi 💬: whom did I talk about cats to?

[Step 1] Searching for relevant conversations...
Found 5 relevant messages

[Step 2] Enriching results with user names...

[Step 3] Generating response using LLM...

🤖 Chatbot: Based on your conversation history, you talked about cats
with Anas Abdullah on October 23rd, 2025. You asked why cats sleep so
much, mentioning that your cat naps 14-16 hours a day.

----------------------------------------------------------------------

Hadi 💬: exit

Goodbye! 👋
```

## Tips

1. **Be specific**: "What did I discuss with John about the project?" works better than "tell me about John"

2. **Natural language**: Ask questions as you would to a human

3. **Context matters**: The chatbot uses semantic search, so synonyms work well

4. **User privacy**: Each user can only see their own conversations

5. **Performance**: First query may be slow due to model loading

## Next Steps

- Add more conversations to MongoDB
- Run `embeddings.py` to generate embeddings
- Try different query styles
- Check `example_usage.py` for advanced usage

---

For detailed documentation, see `README.md`

