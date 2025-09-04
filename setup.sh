#!/bin/bash
#
# AI Society Setup Script
# 
# This script sets up the complete AI Society environment including:
# - Python virtual environment
# - Required dependencies
# - Ollama installation and configuration
# - Essential model downloads
# - System validation
#
# Usage: ./setup.sh
# Author: AI Society Contributors
# License: MIT
#

set -e  # Exit on any error

echo "🚀 AI Society - Dynamic Model Router Setup"
echo "=============================================="
echo ""

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Check if we're in the right directory
check_project_directory() {
    if [ ! -f "requirements.txt" ] || [ ! -f "web/app.py" ]; then
        log_error "Please run this script from the AI Society project directory"
        log_info "The directory should contain requirements.txt and web/app.py"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    log_info "System Requirements Check"
    echo "--------------------------------"

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -gt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]); then
            log_success "Python 3: $PYTHON_VERSION"
        else
            log_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi

    # Check if Ollama is installed
    if command -v ollama &> /dev/null; then
        log_success "Ollama: Installed"
    else
        log_warning "Ollama not found. Installing Ollama..."
        if curl -fsSL https://ollama.com/install.sh | sh; then
            log_success "Ollama installed successfully"
        else
            log_error "Failed to install Ollama"
            exit 1
        fi
    fi

    # Check available disk space (require at least 10GB for models)
    AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
    REQUIRED_SPACE=10485760  # 10GB in KB
    
    if [ "$AVAILABLE_SPACE" -gt "$REQUIRED_SPACE" ]; then
        log_success "Disk space: $(($AVAILABLE_SPACE / 1048576))GB available"
    else
        log_warning "Low disk space: $(($AVAILABLE_SPACE / 1048576))GB available (10GB+ recommended)"
    fi
}

echo ""
echo -e "${BLUE}🔧 Environment Setup${NC}"
echo "----------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${CYAN}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${CYAN}🔌 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${CYAN}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${CYAN}📦 Installing Python packages...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All packages installed successfully${NC}"
else
    echo -e "${RED}❌ Some packages failed to install${NC}"
    echo -e "${YELLOW}💡 Try running: pip install --upgrade pip setuptools wheel${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🤖 Ollama Setup${NC}"
echo "----------------"

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${YELLOW}🚀 Starting Ollama...${NC}"
    ollama serve &
    sleep 3
    
    if pgrep -x "ollama" > /dev/null; then
        echo -e "${GREEN}✅ Ollama started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Ollama${NC}"
        echo -e "${YELLOW}💡 Try running manually: ollama serve${NC}"
        exit 1
    fi
fi

# Download essential models
echo -e "${CYAN}📥 Downloading essential models (this may take a while)...${NC}"
echo ""

# Array of essential models to download
essential_models=(
    "llama3.2:3b"
    "phi3:mini" 
    "qwen2.5-coder:7b"
)

for model in "${essential_models[@]}"; do
    echo -e "${CYAN}📥 Downloading $model...${NC}"
    if ollama pull $model; then
        echo -e "${GREEN}✅ $model downloaded successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to download $model, skipping...${NC}"
    fi
    echo ""
done

# Create data directory
echo -e "${CYAN}📁 Creating data directory...${NC}"
mkdir -p data

# Fix import paths by creating __init__.py files
echo -e "${CYAN}🔧 Setting up Python modules...${NC}"
touch src/__init__.py
touch src/daemon/__init__.py
touch src/routing/__init__.py

echo ""
echo -e "${BLUE}🧪 Testing System${NC}"
echo "------------------"

# Test Ollama connection
echo -e "${CYAN}🔍 Testing Ollama connection...${NC}"
if ollama list > /dev/null 2>&1; then
    MODEL_COUNT=$(ollama list | tail -n +2 | wc -l)
    echo -e "${GREEN}✅ Ollama connection successful${NC}"
    echo -e "${GREEN}📊 Available models: $MODEL_COUNT${NC}"
else
    echo -e "${RED}❌ Ollama connection failed${NC}"
    exit 1
fi

# Test Python imports
echo -e "${CYAN}🔍 Testing Python imports...${NC}"
cd src
python3 -c "
try:
    from daemon.model_discovery import ModelDiscoveryDaemon
    from routing.intelligent_router import IntelligentModelRouter
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
cd ..

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "==================="
echo ""
echo -e "${PURPLE}🚀 To start AI Society:${NC}"
echo -e "${CYAN}   1. ${NC}Ensure Ollama is running: ${YELLOW}ollama serve${NC}"
echo -e "${CYAN}   2. ${NC}Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "${CYAN}   3. ${NC}Run the application: ${YELLOW}python web/app.py${NC}"
echo -e "${CYAN}   4. ${NC}Open browser to: ${YELLOW}http://localhost:8000${NC}"
echo ""
echo -e "${PURPLE}📊 System Info:${NC}"
echo -e "${CYAN}   - Models Downloaded: ${NC}$(ollama list | tail -n +2 | wc -l)"
echo -e "${CYAN}   - Web Interface: ${NC}http://localhost:8000"
echo -e "${CYAN}   - API Docs: ${NC}http://localhost:8000/docs"
echo -e "${CYAN}   - Health Check: ${NC}http://localhost:8000/api/health"
echo ""
echo -e "${PURPLE}🛠️  Additional Commands:${NC}"
echo -e "${CYAN}   - View logs: ${NC}python web/app.py"
echo -e "${CYAN}   - Test router: ${NC}python src/routing/intelligent_router.py"
echo -e "${CYAN}   - Download more models: ${NC}ollama pull <model-name>"
echo -e "${CYAN}   - List models: ${NC}ollama list"
echo ""
echo -e "${GREEN}Happy AI routing! 🤖✨${NC}"
