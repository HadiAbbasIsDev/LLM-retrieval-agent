#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║        SMART RAG CHATBOT - SETUP SCRIPT                          ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if MongoDB is running
echo -e "${YELLOW}[1/5] Checking MongoDB...${NC}"
if systemctl is-active --quiet mongod; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
elif pgrep -x mongod > /dev/null; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}✗ MongoDB is not running${NC}"
    echo "Please start MongoDB:"
    echo "  sudo systemctl start mongod"
    echo "  or"
    echo "  sudo service mongod start"
    exit 1
fi

# Check Python version
echo -e "\n${YELLOW}[2/5] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Install dependencies
echo -e "\n${YELLOW}[3/5] Installing Python dependencies...${NC}"
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Check if model files exist
echo -e "\n${YELLOW}[4/5] Checking model files...${NC}"

# Check LLM model
if [ -f "LLM/gemma-1.1-7b-it.Q4_K_M.gguf" ]; then
    echo -e "${GREEN}✓ LLM model found${NC}"
else
    echo -e "${RED}✗ LLM model not found at LLM/gemma-1.1-7b-it.Q4_K_M.gguf${NC}"
fi

# Check embedding model
if [ -d "models/embeddings/bge-small-en" ]; then
    echo -e "${GREEN}✓ Embedding model found${NC}"
else
    echo -e "${RED}✗ Embedding model not found at models/embeddings/bge-small-en${NC}"
fi

# Generate embeddings
echo -e "\n${YELLOW}[5/5] Generate embeddings for existing conversations?${NC}"
echo "This will read all messages from MongoDB and create embeddings."
read -p "Do you want to generate embeddings now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 embeddings.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Embeddings generated successfully${NC}"
    else
        echo -e "${RED}✗ Failed to generate embeddings${NC}"
    fi
else
    echo "Skipped. You can run 'python3 embeddings.py' later."
fi

# Setup complete
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    SETUP COMPLETE!                                ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "To start the chatbot, run:"
echo -e "${GREEN}  python3 smart_chatbot.py${NC}"
echo ""
echo "Or specify a user ID:"
echo -e "${GREEN}  python3 smart_chatbot.py u_1010${NC}"
echo ""
echo "For examples, run:"
echo -e "${GREEN}  python3 example_usage.py${NC}"
echo ""
echo "For help, see README.md"
echo ""

