#!/usr/bin/env python3

"""
Smart RAG Chatbot for retrieving and answering questions about conversations
"""

from rag import search_messages, group_by_user, get_user_name
from llm_service import LLMService
from db import get_db
from datetime import datetime
import sys

class SmartChatbot:
    """
    Intelligent chatbot that can answer questions about user's conversation history
    using RAG (Retrieval-Augmented Generation)
    """
    
    def __init__(self):
        print("Initializing Smart Chatbot...")
        self.llm = LLMService()
        self.db = get_db()
        self.conversations = self.db["conversations"]
        print("Chatbot ready!")
    
    def enrich_results_with_names(self, results):
        """
        Enrich search results with sender and receiver names from conversations collection
        """
        enriched = []
        for result in results:
            # Find the original conversation to get names
            conv = self.conversations.find_one({"_id": result["conversation_id"]})
            
            if conv:
                result["sender_name"] = conv.get("sender_name", result["sender_id"])
                result["receiver_name"] = conv.get("receiver_name", result["receiver_id"])
            else:
                result["sender_name"] = result["sender_id"]
                result["receiver_name"] = result["receiver_id"]
            
            enriched.append(result)
        
        return enriched
    
    def get_current_user_name(self, user_id):
        """Get the name of the current user"""
        return get_user_name(user_id)
    
    def format_conversation_snippets(self, results, current_user_id, max_display=2):
        """Format actual conversation snippets grouped by person (for display only)"""
        grouped = group_by_user(results, current_user_id)
        
        output = []
        for other_user_id, msgs in grouped.items():
            other_user_name = get_user_name(other_user_id)
            output.append(f"\nYou chatted with {other_user_name}:")
            
            # Show only top max_display messages (concise view for user)
            for msg in msgs[:max_display]:
                sender_name = msg.get('sender_name', msg['sender_id'])
                message_text = msg['message']
                # Truncate if too long
                if len(message_text) > 200:
                    message_text = message_text[:200] + "..."
                output.append(f"   {sender_name}: \"{message_text}\"")
            
            # Add indicator if there are more messages
            if len(msgs) > max_display:
                output.append(f"   ... and {len(msgs) - max_display} more messages")
        
        return "\n".join(output)
    
    def process_query(self, query, user_id, top_k=10):
        """
        Process a user query and return an intelligent response
        
        Args:
            query: Natural language question from the user
            user_id: ID of the user asking the question
            top_k: Number of relevant conversations to retrieve
        
        Returns:
            A natural language response answering the user's question
        """
        print(f"\nProcessing query: '{query}'")
        print(f"User: {user_id}")
        
        # Step 1: Retrieve relevant conversations using semantic search
        print("\n[Step 1] Searching for relevant conversations...")
        # Use moderate similarity threshold (0.3) - let re-ranker do the heavy filtering
        # Retrieve more results for LLM context (top_k * 2) but will display fewer
        results = search_messages(query, top_k=top_k * 2, user_id=user_id, min_similarity=0.3)
        
        if not results:
            return "I couldn't find any relevant conversations in your history."
        
        # Additional check: if even the best match is weak after re-ranking, don't show results
        best_result = results[0] if results else None
        if best_result:
            best_rerank = best_result.get('rerank_score', -999)
            best_similarity = best_result.get('similarity', 0)
            best_keyword = best_result.get('keyword_score', 0)
            
            # Rerank score threshold (cross-encoder scores vary)
            # Adjusted to 0.3 to allow more relevant results through
            # 0.3-1.0 = relevant, >1.0 = highly relevant
            if best_rerank < 0.3:
                return f"I couldn't find any relevant conversations about this topic in your history.\n(Relevance score: {best_rerank:.2f}, semantic: {best_similarity:.2f}, keywords: {best_keyword:.2f})"
        
        print(f"Found {len(results)} relevant messages")
        
        # Step 2: Enrich results with names
        print("[Step 2] Enriching results with user names...")
        enriched_results = self.enrich_results_with_names(results)
        
        # Step 3: Show actual conversation snippets (limited for display)
        print("[Step 3] Formatting conversation snippets...")
        # Only display top 2 messages per person for concise view
        snippets = self.format_conversation_snippets(enriched_results, user_id, max_display=2)
        
        # Step 4: Get LLM to answer the specific question
        print("[Step 4] Generating answer to your question...")
        current_user_name = self.get_current_user_name(user_id)
        # Pass ALL enriched_results to LLM for full context (not just displayed ones)
        llm_answer = self.llm.answer_query(query, enriched_results, current_user_name)
        
        # Combine snippets and LLM answer
        full_response = snippets + "\n\nAnswer: " + llm_answer
        
        return full_response
    
    def display_results_summary(self, results, current_user_id):
        """Display a summary of retrieved results grouped by user"""
        grouped = group_by_user(results, current_user_id)
        
        print("\n" + "="*70)
        print("RETRIEVED CONVERSATIONS SUMMARY")
        print("="*70)
        
        for user_id, msgs in grouped.items():
            user_name = get_user_name(user_id)
            print(f"\n📱 Conversations with {user_name} ({user_id}): {len(msgs)} matches")
            
            for i, msg in enumerate(msgs, 1):
                timestamp = msg.get('timestamp', 'Unknown')
                if timestamp and timestamp != 'Unknown':
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M') if hasattr(timestamp, 'strftime') else str(timestamp)
                
                print(f"\n  {i}. Similarity: {msg['similarity']:.3f}")
                print(f"     Time: {timestamp}")
                print(f"     Message: {msg['message'][:150]}{'...' if len(msg['message']) > 150 else ''}")
        
        print("\n" + "="*70 + "\n")
    
    def interactive_mode(self, user_id=None):
        """
        Run the chatbot in interactive mode
        
        Args:
            user_id: Optional user ID. If not provided, will ask for it.
        """
        print("\n" + "="*70)
        print("🤖 SMART RAG CHATBOT - Interactive Mode")
        print("="*70)
        print("\nAsk questions about your conversations!")
        print("Examples:")
        print("  - 'Whom did I talk about cats to?'")
        print("  - 'What did I discuss with Anas?'")
        print("  - 'When did I last mention work?'")
        print("\nType 'quit' or 'exit' to stop.")
        print("="*70 + "\n")
        
        # Get user ID if not provided
        if user_id is None:
            user_id = input("Enter your user ID (e.g., u_1010): ").strip()
        
        user_name = self.get_current_user_name(user_id)
        print(f"\nWelcome, {user_name}!\n")
        
        while True:
            try:
                # Get user query
                query = input(f"\n{user_name} : ").strip()
                
                if query.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if not query:
                    continue
                
                # Process the query
                # Retrieve more messages (15) for better LLM context
                response = self.process_query(query, user_id, top_k=15)
                
                # Display response
                print(f"\n Chatbot: {response}\n")
                print("-" * 70)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a different query.\n")
    
    def query_once(self, query, user_id, show_summary=True):
        """
        Process a single query and return the response
        
        Args:
            query: The question to ask
            user_id: The user's ID
            show_summary: Whether to show the retrieved conversations summary
        
        Returns:
            The chatbot's response
        """
        # Retrieve and process
        results = search_messages(query, top_k=10, user_id=user_id)
        
        if show_summary and results:
            enriched = self.enrich_results_with_names(results)
            self.display_results_summary(enriched, user_id)
        
        # Generate response
        response = self.process_query(query, user_id)
        
        return response


def main():
    """Main function to run the chatbot"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python smart_chatbot.py [user_id]")
            print("\nOptional arguments:")
            print("  user_id    Your user ID (e.g., u_1010)")
            print("\nIf no user_id is provided, you will be prompted to enter it.")
            return
        
        user_id = sys.argv[1]
    else:
        user_id = None
    
    # Create and run chatbot
    chatbot = SmartChatbot()
    chatbot.interactive_mode(user_id=user_id)


if __name__ == "__main__":
    main()

