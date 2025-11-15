#!/usr/bin/env python3

"""
Example usage of the Smart RAG Chatbot
Demonstrates different ways to use the chatbot programmatically
"""

from smart_chatbot import SmartChatbot

def example_single_query():
    """Example: Process a single query"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Query")
    print("="*70)
    
    chatbot = SmartChatbot()
    
    # User Hadi (u_1010) asks a question
    user_id = "u_1010"
    query = "whom did I talk about cats to?"
    
    response = chatbot.query_once(query, user_id, show_summary=True)
    
    print(f"\nQuery: {query}")
    print(f"Response: {response}")


def example_multiple_queries():
    """Example: Process multiple queries for the same user"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multiple Queries")
    print("="*70)
    
    chatbot = SmartChatbot()
    user_id = "u_1010"
    
    queries = [
        "whom did I talk about cats to?",
        "what topics did I discuss with Anas?",
        "when did I last mention sleep?"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        response = chatbot.process_query(query, user_id, top_k=5)
        print(f"🤖 Response: {response}")
        print("-" * 70)


def example_different_users():
    """Example: Queries from different users (demonstrating privacy)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Different Users")
    print("="*70)
    
    chatbot = SmartChatbot()
    
    users = [
        {"id": "u_1010", "name": "Hadi", "query": "what did I discuss about cats?"},
        {"id": "u_1002", "name": "Anas", "query": "what did Hadi ask me about?"}
    ]
    
    for user in users:
        print(f"\n👤 User: {user['name']} ({user['id']})")
        print(f"🔍 Query: {user['query']}")
        
        response = chatbot.process_query(user['query'], user['id'], top_k=5)
        print(f"🤖 Response: {response}")
        print("-" * 70)


def example_custom_processing():
    """Example: Custom processing with manual steps"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Processing")
    print("="*70)
    
    from rag import search_messages
    from llm_service import LLMService
    
    # Step 1: Search for relevant messages
    query = "cats and sleep"
    user_id = "u_1010"
    
    print(f"\nSearching for: '{query}'")
    results = search_messages(query, top_k=3, user_id=user_id)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity']:.3f}")
        print(f"   Message: {result['message'][:100]}...")
    
    # Step 2: Use LLM to generate a custom response
    llm = LLMService()
    
    # Create a custom prompt
    custom_prompt = f"""<start_of_turn>user
Based on these messages, what are the main topics discussed?

Messages:
{chr(10).join([f"- {r['message']}" for r in results])}
<end_of_turn>
<start_of_turn>model
"""
    
    response = llm.generate_response(custom_prompt, max_tokens=150)
    print(f"\n🤖 LLM Analysis: {response}")


def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║        SMART RAG CHATBOT - USAGE EXAMPLES                         ║
╚═══════════════════════════════════════════════════════════════════╝

This script demonstrates different ways to use the Smart RAG Chatbot.

Choose an example to run:
1. Single Query
2. Multiple Queries
3. Different Users (Privacy Demo)
4. Custom Processing
5. Interactive Mode (Full Chatbot)
6. Run All Examples

0. Exit
""")
    
    choice = input("Enter your choice (0-6): ").strip()
    
    if choice == "1":
        example_single_query()
    elif choice == "2":
        example_multiple_queries()
    elif choice == "3":
        example_different_users()
    elif choice == "4":
        example_custom_processing()
    elif choice == "5":
        chatbot = SmartChatbot()
        chatbot.interactive_mode(user_id="u_1010")
    elif choice == "6":
        example_single_query()
        example_multiple_queries()
        example_different_users()
        example_custom_processing()
    elif choice == "0":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")
    
    print("\n" + "="*70)
    print("Example completed!")
    print("="*70)


if __name__ == "__main__":
    main()

