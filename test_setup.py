#!/usr/bin/env python3

"""
Test script to verify the Smart RAG Chatbot setup
"""

import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    tests = [
        ("pymongo", "MongoDB driver"),
        ("sentence_transformers", "Sentence Transformers"),
        ("numpy", "NumPy"),
        ("llama_cpp", "Llama.cpp Python bindings"),
    ]
    
    failed = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"  ✓ {description} ({module})")
        except ImportError as e:
            print(f"  ✗ {description} ({module}): {str(e)}")
            failed.append(module)
    
    return len(failed) == 0, failed


def test_mongodb():
    """Test MongoDB connection"""
    print("\nTesting MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()  # Force connection
        print("  ✓ MongoDB connection successful")
        
        # Check database and collections
        db = client["chatbotDB"]
        collections = db.list_collection_names()
        
        if "conversations" in collections:
            count = db["conversations"].count_documents({})
            print(f"  ✓ 'conversations' collection found ({count} documents)")
        else:
            print("  ✗ 'conversations' collection not found")
            return False
        
        if "embeddings" in collections:
            count = db["embeddings"].count_documents({})
            print(f"  ✓ 'embeddings' collection found ({count} documents)")
            if count == 0:
                print("    ⚠ Warning: No embeddings found. Run 'python3 embeddings.py' first.")
        else:
            print("  ⚠ 'embeddings' collection not found (will be created when you run embeddings.py)")
        
        return True
    except Exception as e:
        print(f"  ✗ MongoDB connection failed: {str(e)}")
        return False


def test_models():
    """Test if model files exist"""
    print("\nTesting model files...")
    
    import os
    
    # Check LLM model
    llm_path = "/home/it-admin/Desktop/SmartApp_Clone/LLM/gemma-1.1-7b-it.Q4_K_M.gguf"
    if os.path.exists(llm_path):
        size_mb = os.path.getsize(llm_path) / (1024 * 1024)
        print(f"  ✓ LLM model found ({size_mb:.1f} MB)")
    else:
        print(f"  ✗ LLM model not found at: {llm_path}")
        return False
    
    # Check embedding model
    embed_path = "/home/it-admin/Desktop/SmartApp_Clone/models/embeddings/bge-small-en"
    if os.path.exists(embed_path):
        print(f"  ✓ Embedding model directory found")
        
        required_files = ["model.safetensors", "config.json", "tokenizer.json"]
        for file in required_files:
            file_path = os.path.join(embed_path, file)
            if os.path.exists(file_path):
                print(f"    ✓ {file}")
            else:
                print(f"    ✗ {file} not found")
                return False
    else:
        print(f"  ✗ Embedding model not found at: {embed_path}")
        return False
    
    return True


def test_embedding_model():
    """Test if embedding model loads correctly"""
    print("\nTesting embedding model loading...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('/home/it-admin/Desktop/SmartApp_Clone/models/embeddings/bge-small-en')
        
        # Test encoding
        test_text = "Hello, this is a test."
        embedding = model.encode(test_text)
        
        print(f"  ✓ Embedding model loaded successfully")
        print(f"  ✓ Test embedding generated (dimension: {len(embedding)})")
        return True
    except Exception as e:
        print(f"  ✗ Failed to load embedding model: {str(e)}")
        return False


def test_llm_model():
    """Test if LLM model loads correctly (optional, can be slow)"""
    print("\nTesting LLM model loading (this may take a minute)...")
    
    try:
        from llama_cpp import Llama
        
        llm = Llama(
            model_path="/home/it-admin/Desktop/SmartApp_Clone/LLM/gemma-1.1-7b-it.Q4_K_M.gguf",
            n_ctx=512,  # Smaller context for testing
            n_threads=2,
            n_gpu_layers=0,
            verbose=False
        )
        
        # Test generation
        output = llm("Hello", max_tokens=5, echo=False)
        
        print(f"  ✓ LLM model loaded successfully")
        print(f"  ✓ Test generation completed")
        return True
    except Exception as e:
        print(f"  ✗ Failed to load LLM model: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║        SMART RAG CHATBOT - SETUP VERIFICATION                    ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    results = []
    
    # Test imports
    success, failed = test_imports()
    results.append(("Imports", success))
    if not success:
        print(f"\n⚠ Missing packages: {', '.join(failed)}")
        print("Install them with: pip install -r requirements.txt")
        return
    
    # Test MongoDB
    results.append(("MongoDB", test_mongodb()))
    
    # Test model files
    results.append(("Model Files", test_models()))
    
    # Test embedding model
    results.append(("Embedding Model", test_embedding_model()))
    
    # Ask if user wants to test LLM (slow)
    print("\nThe LLM test can take 30-60 seconds to load the model.")
    response = input("Do you want to test LLM loading? (y/n): ").strip().lower()
    if response == 'y':
        results.append(("LLM Model", test_llm_model()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✓ All tests passed! Your setup is ready.")
        print("\nTo start the chatbot, run:")
        print("  python3 smart_chatbot.py u_1010")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
    
    print()


if __name__ == "__main__":
    main()

