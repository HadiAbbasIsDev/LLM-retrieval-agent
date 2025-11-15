#!/usr/bin/env python3

from llama_cpp import Llama
import os

class LLMService:
    """Service for interacting with the local LLM"""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = "/home/it-admin/Desktop/SmartApp_Clone/LLM/gemma-1.1-7b-it.Q4_K_M.gguf"
        
        print(f"Loading LLM from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Context window
            n_threads=4,  # Number of CPU threads
            n_gpu_layers=0,  # Set to 0 for CPU, increase if you have GPU
            verbose=False
        )
        print("LLM loaded successfully!")
    
    def generate_response(self, prompt, max_tokens=512, temperature=0.7, top_p=0.9):
        """
        Generate a response from the LLM
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more creative)
            top_p: Nucleus sampling parameter
        """
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            echo=False,
            stop=["</s>", "Human:", "User:"]
        )
        
        return output['choices'][0]['text'].strip()
    
    def create_rag_prompt(self, user_query, context_messages, current_user_name):
        """
        Create a prompt for RAG-based question answering
        
        Args:
            user_query: The user's question
            context_messages: List of relevant retrieved messages
            current_user_name: Name of the current user
        """
        # Build context from retrieved messages
        context = ""
        if context_messages:
            context = "Relevant conversations found:\n\n"
            for i, msg in enumerate(context_messages, 1):
                sender_name = msg.get('sender_name', msg['sender_id'])
                receiver_name = msg.get('receiver_name', msg['receiver_id'])
                message = msg['message']
                timestamp = msg.get('timestamp', 'Unknown time')
                
                context += f"{i}. Conversation between {sender_name} and {receiver_name}\n"
                context += f"   Time: {timestamp}\n"
                context += f"   Message: {message}\n\n"
        else:
            context = "No relevant conversations found in the database.\n\n"
        
        # Create the full prompt with instruction format for Gemma
        prompt = f"""<start_of_turn>user
You are a helpful assistant that answers questions based on conversation history.

User: {current_user_name}
Question: {user_query}

{context}

INSTRUCTIONS: 
- Read the conversations above carefully
- Answer the user's question DIRECTLY and BRIEFLY
- Use information from the actual messages shown
- Keep your answer SHORT (1-2 sentences max)
- Just answer the question, nothing more

Example:
Question: "Did Anas push the changes?"
Answer: "Yes, Anas confirmed he pushed the changes to main."

Now answer the user's question:<end_of_turn>
<start_of_turn>model
"""
        
        return prompt
    
    def answer_query(self, user_query, context_messages, current_user_name):
        """
        Answer a user query using RAG approach
        
        Args:
            user_query: The user's natural language question
            context_messages: Retrieved relevant messages from the database
            current_user_name: Name of the current user asking the question
        """
        prompt = self.create_rag_prompt(user_query, context_messages, current_user_name)
        # Keep answer short - max 100 tokens (about 1-2 sentences)
        response = self.generate_response(prompt, max_tokens=100, temperature=0.5)
        return response


if __name__ == "__main__":
    # Test the LLM service
    llm = LLMService()
    
    # Test with a simple query
    test_messages = [
        {
            "sender_name": "Hadi",
            "receiver_name": "Anas Abdullah",
            "sender_id": "u_1010",
            "receiver_id": "u_1002",
            "message": "Hey Anas! Random question: why do cats sleep so much? Mine naps like 14–16 hours a day.",
            "timestamp": "2025-10-23T12:00:05",
            "similarity": 0.95
        }
    ]
    
    response = llm.answer_query(
        "whom did I talk about cats to?",
        test_messages,
        "Hadi"
    )
    
    print("Response:", response)

