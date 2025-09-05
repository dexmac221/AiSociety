#!/usr/bin/env python3
"""
AI Society - Dynamic Model Router

Main entry point for the AI Society application. This script starts the
FastAPI web server with the complete routing system including conversation
memory, multilingual support, and intelligent model selection.

Usage:
    python main.py
    
Or use the convenience script:
    ./start.sh

Author: AI Society Contributors
License: MIT
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Main entry point
if __name__ == "__main__":
    try:
        from web.app import app
        import uvicorn
        
        print("🚀 Starting AI Society...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run setup.sh first to install dependencies")
        sys.exit(1)
