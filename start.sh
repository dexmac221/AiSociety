#!/bin/bash

echo "🚀 Starting AI Society - Dynamic Model Router"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the AI Society project directory${NC}"
    exit 1
fi

# Check if setup was completed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup first...${NC}"
    chmod +x setup.sh
    ./setup.sh
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}🚀 Starting Ollama server...${NC}"
    ollama serve &
    sleep 3
    
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✅ Ollama started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Ollama${NC}"
        echo -e "${YELLOW}💡 Please run manually: ollama serve${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Ollama is already running${NC}"
fi

# Check for models (but don't auto-download)
echo -e "${BLUE}🔍 Checking available models...${NC}"
MODELS_AVAILABLE=$(ollama list | tail -n +2 | wc -l)

if [ $MODELS_AVAILABLE -eq 0 ]; then
    echo -e "${YELLOW}� No models found locally - will download on first request${NC}"
    echo -e "${BLUE}💡 System will intelligently download the best model for each query${NC}"
else
    echo -e "${GREEN}📊 Found $MODELS_AVAILABLE model(s) available locally${NC}"
fi

# Create necessary directories
mkdir -p data
mkdir -p logs

# Create __init__.py files for Python modules
touch src/__init__.py
touch src/daemon/__init__.py  
touch src/routing/__init__.py

# Set Python path
export PYTHONPATH="${PWD}/src:$PYTHONPATH"

echo -e "${GREEN}🌐 Starting web server...${NC}"
echo -e "${BLUE}📊 Available at: ${NC}"
echo -e "${BLUE}   - Local: http://localhost:8000${NC}"
echo -e "${BLUE}   - Network: http://192.168.1.62:8000${NC}"
echo -e "${BLUE}📚 API docs at: http://192.168.1.62:8000/docs${NC}"
echo -e "${BLUE}🏥 Health check: http://192.168.1.62:8000/api/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the application
cd web && python app.py
