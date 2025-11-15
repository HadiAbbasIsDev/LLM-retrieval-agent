#!/usr/bin/env python3
"""Quick test to see the new format"""

from smart_chatbot import SmartChatbot

print("Testing new conversation snippet format...\n")

# Simulate what happens when you ask a question
chatbot = SmartChatbot()

# Test with user u_1010 (Hadi)
response = chatbot.process_query("cats", "u_1010", top_k=10)

print("\n" + "="*70)
print("NEW FORMAT - ACTUAL CHAT SNIPPETS")
print("="*70)
print(response)
print("="*70)

