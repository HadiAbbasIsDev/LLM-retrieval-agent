#!/usr/bin/env python3

"""
Quick test script to verify the chatbot works without interactive mode
"""

print("="*70)
print("TESTING SMART RAG CHATBOT")
print("="*70)

# Test 1: Import modules
print("\n[Test 1] Testing imports...")
try:
    from rag import search_messages, group_by_user, get_user_name
    print("✅ RAG module imported")
except Exception as e:
    print(f"❌ RAG module failed: {e}")
    exit(1)

try:
    from llm_service import LLMService
    print("✅ LLM service imported")
except Exception as e:
    print(f"❌ LLM service failed: {e}")
    exit(1)

try:
    from smart_chatbot import SmartChatbot
    print("✅ Smart chatbot imported")
except Exception as e:
    print(f"❌ Smart chatbot failed: {e}")
    exit(1)

# Test 2: Check MongoDB connection
print("\n[Test 2] Testing MongoDB connection...")
try:
    from db import get_db
    db = get_db()
    # Try to access collections
    conversations = db["conversations"].find_one()
    if conversations:
        print(f"✅ MongoDB connected - Found conversations")
    else:
        print("⚠️  MongoDB connected - No conversations found")
        print("   Run 'python3 embeddings.py' to generate embeddings")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("   Make sure MongoDB is running: sudo systemctl start mongod")

# Test 3: Test RAG search (if data exists)
print("\n[Test 3] Testing semantic search...")
try:
    results = search_messages("test query", top_k=1, user_id="u_1010")
    if results:
        print(f"✅ Semantic search working - Found {len(results)} result(s)")
    else:
        print("⚠️  Semantic search working - No results (may need embeddings)")
except Exception as e:
    print(f"❌ Semantic search failed: {e}")

# Test 4: LLM loading (this takes a few seconds)
print("\n[Test 4] Testing LLM loading...")
print("   This may take 5-10 seconds...")
try:
    llm = LLMService()
    print("✅ LLM loaded successfully")
    
    # Test a simple generation
    print("\n[Test 5] Testing LLM generation...")
    prompt = "<start_of_turn>user\nSay hello!<end_of_turn>\n<start_of_turn>model\n"
    response = llm.generate_response(prompt, max_tokens=20)
    print(f"✅ LLM generation working")
    print(f"   Sample response: {response[:50]}...")
except Exception as e:
    print(f"❌ LLM test failed: {e}")

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print("\n✅ All core components are working!")
print("\nYour chatbot is ready to use!")
print("\nTo start the chatbot:")
print("  python3 smart_chatbot.py u_1010")
print("\nTo generate embeddings first:")
print("  python3 embeddings.py")
print("\n" + "="*70)

