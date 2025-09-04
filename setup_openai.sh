#!/bin/bash

# AI Society - GPT-4.1-mini Configuration Setup Script
# This script helps you configure and test the OpenAI meta-routing system

set -e

echo "🚀 AI Society        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )-4.1-mini Setup"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "config/router_config.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the AI Society root directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Configuration Steps:${NC}"
echo "1. Set up OpenAI API key"
echo "2. Configure model selection"
echo "3. Test Ollama connection"
echo "4. Validate configuration"
echo ""

# Step 1: OpenAI API Key Setup
echo -e "${YELLOW}🔑 Step 1: OpenAI API Key Setup${NC}"
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not found in environment${NC}"
    echo "You can set it by:"
    echo "  export OPENAI_API_KEY=your-api-key-here"
    echo "Or create a .env file with your API key"
    echo ""
    read -p "Do you want to set the API key now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " api_key
        export OPENAI_API_KEY="$api_key"
        echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.bashrc
        echo -e "${GREEN}✅ API key set for this session and added to ~/.bashrc${NC}"
    fi
else
    echo -e "${GREEN}✅ OPENAI_API_KEY found in environment${NC}"
fi

# Step 2: Configuration Check
echo -e "${YELLOW}⚙️  Step 2: Checking Configuration${NC}"

# Check if GPT-4o-mini is enabled
if grep -q '"enabled": true' config/router_config.json; then
    echo -e "${GREEN}✅ OpenAI meta-routing is enabled${NC}"
else
    echo -e "${YELLOW}⚠️  Enabling OpenAI meta-routing...${NC}"
    # Update the config to enable it
    python3 -c "
import json
with open('config/router_config.json', 'r') as f:
    config = json.load(f)
config['openai_meta_routing']['enabled'] = True
with open('config/router_config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
    echo -e "${GREEN}✅ OpenAI meta-routing enabled${NC}"
fi

# Step 3: Test Ollama Connection
echo -e "${YELLOW}🔗 Step 3: Testing Ollama Connection${NC}"

OLLAMA_HOST=$(python3 -c "
import json
with open('config/router_config.json', 'r') as f:
    config = json.load(f)
print(config['ollama_config']['host'])
")

echo "Testing connection to: $OLLAMA_HOST"

if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama connection successful${NC}"
    
    # Show available models
    echo -e "${BLUE}📦 Available Ollama models:${NC}"
    curl -s "$OLLAMA_HOST/api/tags" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    models = data.get('models', [])
    if models:
        for model in models[:5]:  # Show first 5
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = round(size / 1024 / 1024 / 1024, 1) if size > 0 else 0
            print(f'  • {name} ({size_gb}GB)')
        if len(models) > 5:
            print(f'  ... and {len(models) - 5} more models')
    else:
        print('  No models found')
except:
    print('  Unable to parse model list')
"
else
    echo -e "${RED}❌ Cannot connect to Ollama at $OLLAMA_HOST${NC}"
    echo "Please check:"
    echo "  1. Ollama is running: ollama serve"
    echo "  2. Host address is correct in config/router_config.json"
    echo "  3. Firewall allows connection"
fi

# Step 4: Configuration Test
echo -e "${YELLOW}🧪 Step 4: Testing Configuration${NC}"

echo "Creating test script..."

cat > test_gpt4o_config.py << 'EOF'
#!/usr/bin/env python3
"""Test GPT-4o-mini configuration"""

import json
import os
import sys
import requests
from pathlib import Path

def test_config():
    """Test the configuration files"""
    print("🔍 Testing configuration...")
    
    # Check main config
    config_path = Path("config/router_config.json")
    if not config_path.exists():
        print("❌ router_config.json not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Check OpenAI settings
    openai_config = config.get("openai_meta_routing", {})
    if not openai_config.get("enabled"):
        print("❌ OpenAI meta-routing not enabled")
        return False
    
    print("✅ OpenAI meta-routing enabled")
    
    if openai_config.get("model") != "gpt-4.1-mini":
        print(f"⚠️  Model is {openai_config.get('model')}, expected gpt-4.1-mini")
    else:
        print("✅ GPT-4.1-mini configured")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    if api_key == "your_openai_api_key_here":
        print("❌ Please set a real OpenAI API key")
        return False
    
    print("✅ API key is set")
    
    # Test API key (optional)
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        print("✅ OpenAI API connection successful")
    except ImportError:
        print("⚠️  OpenAI library not installed (pip install openai)")
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
    
    # Check Ollama config
    ollama_config = config.get("ollama_config", {})
    ollama_host = ollama_config.get("host", "http://localhost:11434")
    
    try:
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama connection successful ({len(models)} models available)")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
    
    return True

def show_config_summary():
    """Show a summary of the current configuration"""
    print("\n📊 Configuration Summary:")
    print("=" * 50)
    
    with open("config/router_config.json") as f:
        config = json.load(f)
    
    openai_config = config.get("openai_meta_routing", {})
    print(f"OpenAI Model: {openai_config.get('model', 'Not set')}")
    print(f"Meta-routing: {'✅ Enabled' if openai_config.get('enabled') else '❌ Disabled'}")
    print(f"Cache decisions: {'✅ Yes' if openai_config.get('cache_decisions') else '❌ No'}")
    print(f"Max requests/hour: {openai_config.get('cost_optimization', {}).get('max_requests_per_hour', 'Not set')}")
    
    ollama_config = config.get("ollama_config", {})
    print(f"Ollama host: {ollama_config.get('host', 'Not set')}")
    
    print(f"Auto download: {'✅ Yes' if config.get('auto_download') else '❌ No'}")
    print(f"Performance tracking: {'✅ Yes' if config.get('performance_tracking') else '❌ No'}")

if __name__ == "__main__":
    if test_config():
        show_config_summary()
        print("\n🎉 Configuration test completed!")
        print("\nNext steps:")
        print("1. Run: ./start.sh")
        print("2. Open: http://localhost:8000")
        print("3. Test with queries like 'Write a Python function' or 'Solve 2x + 5 = 15'")
    else:
        print("\n❌ Configuration has issues. Please fix them before proceeding.")
        sys.exit(1)
EOF

python3 test_gpt4o_config.py

# Cleanup
rm -f test_gpt4o_config.py

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "1. Run: ./start.sh"
echo "2. Open: http://localhost:8000"
echo "3. Test with queries like:"
echo "   • 'Write a Python function to sort a list'"
echo "   • 'Solve the equation 2x + 5 = 15'"
echo "   • 'Write a short story about AI'"
echo ""
echo -e "${YELLOW}Configuration files created:${NC}"
echo "• config/router_config.json - Main configuration"
echo "• config/model_selection.json - Model selection strategies"
echo "• config/api_config.env - Environment variables template"
echo ""
echo -e "${BLUE}To monitor routing decisions:${NC}"
echo "tail -f logs/app.log | grep -E '(routing|openai|model)'"
