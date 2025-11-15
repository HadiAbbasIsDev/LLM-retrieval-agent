#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║     SMART RAG CHATBOT - CPU-ONLY INSTALLATION                    ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[1/3] Installing PyTorch (CPU-only)...${NC}"
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo -e "\n${YELLOW}[2/3] Installing other dependencies...${NC}"
pip install pymongo==4.6.1 numpy==1.24.3 sentence-transformers>=2.3.1 llama-cpp-python>=0.2.32

echo -e "\n${YELLOW}[3/3] Verifying installation...${NC}"
python3 -c "from rag import search_messages; from llm_service import LLMService; from smart_chatbot import SmartChatbot; print('✓ All modules working!')"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  INSTALLATION COMPLETE!                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure MongoDB is running: sudo systemctl start mongod"
echo "2. Generate embeddings: python3 embeddings.py"
echo "3. Run chatbot: python3 smart_chatbot.py u_1010"
echo ""

