# AI Society Dynamic Model Router

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
