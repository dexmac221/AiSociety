from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import threading
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    import ollama
    from daemon.model_discovery import ModelDiscoveryDaemon
    from routing.enhanced_intelligent_router import EnhancedIntelligentRouter
    from memory.hybrid_memory import HybridMemorySystem
    
    # Configure Ollama client for remote host
    import json
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'router_config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        # Check for new ollama_config format first, then fallback to old ollama_host
        ollama_host = config.get('ollama_config', {}).get('host') or config.get('ollama_host', 'http://localhost:11434')
        ollama._client._base_url = ollama_host
        print(f"🔗 Configured Ollama for: {ollama_host}")
        
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

app = FastAPI(title="AI Society - Dynamic Model Router", version="1.0.0")

# Initialize router
try:
    print(f"🔍 Web app working directory: {os.getcwd()}")
    print(f"🔍 Web app config path: {os.path.abspath('config/router_config.json')}")
    print(f"🔍 Config exists: {os.path.exists('config/router_config.json')}")
    
    router = EnhancedIntelligentRouter()
    print("✅ Enhanced Router with OpenAI meta-routing initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize enhanced router: {e}")
    router = None

# Conversation memory for each session
# ConversationMemory has been replaced with HybridMemorySystem

# Connection manager for WebSocket with conversation memory
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.conversations: Dict[str, HybridMemorySystem] = {}
        
        # Create memory data directory if it doesn't exist
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory')
        os.makedirs(memory_dir, exist_ok=True)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Create a unique session ID for this connection
        session_id = f"session_{len(self.conversations)}_{int(time.time())}"
        
        # Initialize hybrid memory system for this session
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory')
        self.conversations[session_id] = HybridMemorySystem(
            session_id=session_id,
            memory_dir=memory_dir
        )
        
        # Store session_id in websocket for later retrieval
        websocket.session_id = session_id
        
        return session_id

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # Clean up old conversations (keep last 50 sessions)
        if len(self.conversations) > 50:
            oldest_sessions = sorted(self.conversations.keys())[:len(self.conversations) - 50]
            for session_id in oldest_sessions:
                del self.conversations[session_id]

    def get_conversation(self, session_id: str) -> HybridMemorySystem:
        """Get conversation memory for a session"""
        return self.conversations.get(session_id)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get_chat_interface():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Society - Dynamic Model Router</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                /* Light theme variables */
                --bg-primary: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                --bg-container: white;
                --bg-header: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --bg-status: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
                --bg-chat: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
                --bg-input: white;
                --bg-message-user: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --bg-message-assistant: white;
                --bg-suggestion: rgba(255,255,255,0.15);
                --bg-suggestion-hover: rgba(255,255,255,0.25);
                --bg-suggestions-bar: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --text-primary: #333;
                --text-secondary: #495057;
                --text-muted: #6c757d;
                --text-white: white;
                --text-status: #495057;
                --border-primary: #e9ecef;
                --border-secondary: #dee2e6;
                --shadow-primary: rgba(0,0,0,0.1);
                --shadow-secondary: rgba(0,0,0,0.2);
                --accent-primary: #667eea;
                --accent-secondary: #764ba2;
            }
            
            [data-theme="dark"] {
                /* Dark theme variables */
                --bg-primary: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                --bg-container: #16213e;
                --bg-header: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                --bg-status: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
                --bg-chat: linear-gradient(to bottom, #16213e 0%, #1a1a2e 100%);
                --bg-input: #1e3c72;
                --bg-message-user: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --bg-message-assistant: #1e3c72;
                --bg-suggestion: rgba(255,255,255,0.1);
                --bg-suggestion-hover: rgba(255,255,255,0.2);
                --bg-suggestions-bar: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                --text-primary: #e9ecef;
                --text-secondary: #ced4da;
                --text-muted: #adb5bd;
                --text-white: white;
                --text-status: #ced4da;
                --border-primary: #2a3f5f;
                --border-secondary: #1e3c72;
                --shadow-primary: rgba(0,0,0,0.3);
                --shadow-secondary: rgba(0,0,0,0.5);
                --accent-primary: #667eea;
                --accent-secondary: #764ba2;
            }

            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: var(--bg-primary);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                transition: all 0.3s ease;
            }
            
            .container {
                width: 100vw;
                height: 100vh;
                max-width: none;
                background: var(--bg-container);
                border-radius: 0;
                box-shadow: none;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                transition: all 0.3s ease;
            }
            
            .header {
                background: var(--bg-header);
                color: var(--text-white);
                padding: 25px;
                text-align: center;
                position: relative;
                overflow: hidden;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: repeating-linear-gradient(
                    45deg,
                    transparent,
                    transparent 10px,
                    rgba(255,255,255,0.05) 10px,
                    rgba(255,255,255,0.05) 20px
                );
                animation: slide 20s linear infinite;
            }
            
            @keyframes slide {
                0% { transform: translate(-50%, -50%); }
                100% { transform: translate(-40%, -40%); }
            }
            
            .header-content {
                position: relative;
                z-index: 2;
                flex: 1;
                text-align: center;
            }
            
            .theme-toggle {
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.2);
                color: var(--text-white);
                padding: 8px 12px;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 14px;
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                gap: 6px;
                z-index: 3;
                position: relative;
            }
            
            .theme-toggle:hover {
                background: rgba(255,255,255,0.25);
                transform: scale(1.05);
            }
            
            .theme-icon {
                font-size: 16px;
                transition: transform 0.3s ease;
            }
            
            .theme-toggle:hover .theme-icon {
                transform: rotate(180deg);
            }
            
            .header h1 { 
                font-size: 32px; 
                margin-bottom: 10px;
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p { 
                opacity: 0.95; 
                font-size: 16px;
                font-weight: 300;
            }
            
            #status-bar {
                background: var(--bg-status-bar);
                padding: 12px 25px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 14px;
                flex-shrink: 0;
                color: white;
                font-weight: 500;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #ff4757;
                animation: pulse 2s infinite;
                margin-right: 8px;
            }
            
            .status-dot.connected {
                background: #2ed573;
                animation: none;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #ff6b6b;
                animation: pulse 2s infinite;
            }
            
            .status-dot.connected {
                background: #51cf66;
            }
            
            .tech-info-toggle {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                color: var(--text-white);
                padding: 6px 12px;
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .tech-info-toggle:hover {
                background: rgba(255,255,255,0.2);
                transform: translateY(-1px);
            }
            
            #model-count {
                color: white;
                font-weight: 500;
                opacity: 0.95;
            }
            
            #status-text {
                color: white;
                font-weight: 500;
            }
            
            .tech-panel {
                background: var(--bg-tech-panel, linear-gradient(135deg, #2c3e50 0%, #34495e 100%));
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding: 15px 25px;
                transition: all 0.3s ease;
                overflow: hidden;
            }
            
            .tech-panel.hidden {
                max-height: 0;
                padding: 0 25px;
                opacity: 0;
            }
            
            .tech-panel:not(.hidden) {
                max-height: 200px;
                opacity: 1;
            }
            
            .tech-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
            }
            
            .tech-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 12px;
                backdrop-filter: blur(10px);
            }
            
            .tech-card h4 {
                margin: 0 0 8px 0;
                font-size: 14px;
                color: var(--text-white);
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .tech-card div {
                display: flex;
                flex-direction: column;
                gap: 4px;
                font-size: 12px;
                color: rgba(255,255,255,0.8);
            }
            
            .tech-card span span {
                color: var(--accent-blue);
                font-weight: 600;
            }
            
            @media (max-width: 768px) {
                .tech-grid {
                    grid-template-columns: 1fr;
                }
                
                .tech-panel:not(.hidden) {
                    max-height: 400px;
                }
            }            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background: #28a745;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            #chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 25px;
                background: var(--bg-chat);
                scroll-behavior: smooth;
                transition: all 0.3s ease;
            }
            
            #chat-container::-webkit-scrollbar {
                width: 6px;
            }
            
            #chat-container::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }
            
            #chat-container::-webkit-scrollbar-thumb {
                background: #c1c1c1;
                border-radius: 3px;
            }
            
            #chat-container::-webkit-scrollbar-thumb:hover {
                background: #a8a8a8;
            }
            
            .message {
                margin: 20px 0;
                display: flex;
                align-items: flex-start;
                animation: messageSlide 0.4s ease-out;
                opacity: 0;
                animation-fill-mode: forwards;
            }
            
            @keyframes messageSlide {
                from { 
                    opacity: 0; 
                    transform: translateY(20px) scale(0.95); 
                }
                to { 
                    opacity: 1; 
                    transform: translateY(0) scale(1); 
                }
            }
            
            .message.user { 
                justify-content: flex-end; 
            }
            
            .message-content {
                max-width: 75%;
                padding: 16px 20px;
                border-radius: 20px;
                position: relative;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                line-height: 1.5;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 6px;
                margin-left: 60px;
            }
            
            .message.assistant .message-content {
                background: var(--bg-message-assistant);
                border: 1px solid var(--border-primary);
                border-bottom-left-radius: 6px;
                margin-right: 60px;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .model-info {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
                margin-bottom: 8px;
                padding: 4px 12px;
                background: rgba(0,0,0,0.1);
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            
            .message.assistant .model-info {
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                color: #1565c0;
                border: 1px solid #bbdefb;
            }
            
            /* Dark mode styles for model info */
            [data-theme="dark"] .message.assistant .model-info {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: #ffffff;
                border: 1px solid #3f51b5;
            }
            
            .optimization-info {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 11px;
                margin-top: 6px;
                padding: 3px 8px;
                background: linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%);
                color: #e65100;
                border-radius: 8px;
                border: 1px solid #ffcc02;
                opacity: 0.9;
            }
            
            /* Dark mode styles for optimization info */
            [data-theme="dark"] .optimization-info {
                background: linear-gradient(135deg, #424242 0%, #616161 100%);
                color: #ffab00;
                border: 1px solid #ff8f00;
            }
            
            .memory-info {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 11px;
                margin-top: 6px;
                padding: 3px 8px;
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                color: #1565c0;
                border-radius: 8px;
                border: 1px solid #42a5f5;
                opacity: 0.9;
            }
            
            .memory-enabled {
                font-weight: 600;
                color: #0d47a1;
            }
            
            .query-enhanced {
                font-weight: 600;
                color: #ff6f00;
            }
            
            .query-comparison {
                margin: 8px 0;
                padding: 8px;
                background: linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%);
                border-radius: 8px;
                border-left: 4px solid #4caf50;
                font-size: 12px;
            }
            
            .query-original {
                color: #666;
                font-style: italic;
                margin-bottom: 4px;
            }
            
            .query-optimized {
                color: #2e7d32;
                font-weight: 500;
            }
            
            .query-label {
                font-weight: 600;
                font-size: 10px;
                text-transform: uppercase;
                margin-right: 4px;
            }
            
            .model-icon {
                font-size: 14px;
            }
            
            #input-container {
                padding: 25px;
                background: var(--bg-input);
                border-top: 2px solid var(--border-secondary);
                display: flex;
                gap: 15px;
                align-items: center;
                transition: all 0.3s ease;
            }
            
            #message-input {
                flex: 1;
                padding: 16px 20px;
                border: 2px solid var(--border-primary);
                border-radius: 30px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: var(--bg-container);
                color: var(--text-primary);
                outline: none;
            }
            
            #message-input:focus {
                border-color: var(--accent-primary);
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            #message-input::placeholder {
                color: var(--text-muted);
            }
            
            #send-btn {
                padding: 16px 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 30px;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 120px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            #send-btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            #send-btn:active { 
                transform: translateY(0);
            }
            
            #send-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }
            
            .typing-indicator {
                display: inline-flex;
                align-items: center;
                padding: 16px 20px;
                background: var(--bg-message-assistant);
                border: 1px solid var(--border-primary);
                border-radius: 20px;
                border-bottom-left-radius: 6px;
                margin-right: 60px;
                box-shadow: 0 4px 15px var(--shadow-primary);
                transition: all 0.3s ease;
                color: var(--text-primary);
            }
            
            /* Dark mode styling for typing indicator */
            [data-theme="dark"] .typing-indicator {
                color: #ffffff;
            }
            
            .typing-dots {
                display: flex;
                gap: 4px;
                margin-left: 8px;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { 
                    opacity: 0.3; 
                    transform: scale(0.8); 
                }
                30% { 
                    opacity: 1; 
                    transform: scale(1.2); 
                }
            }
            
            .welcome-message {
                text-align: center;
                color: var(--text-muted);
                font-style: italic;
                margin: 40px 0;
                padding: 30px;
                background: var(--bg-container);
                border-radius: 15px;
                border: 2px dashed var(--border-secondary);
                transition: all 0.3s ease;
            }
            
            .welcome-message h3 {
                color: var(--text-secondary);
                margin-bottom: 10px;
                font-size: 20px;
            }
            
            #messages-area {
                flex: 1;
                overflow-y: auto;
                padding-top: 20px;
            }
            
            #messages-area::-webkit-scrollbar {
                width: 6px;
            }
            
            #messages-area::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 3px;
            }
            
            #messages-area::-webkit-scrollbar-thumb {
                background: #c1c1c1;
                border-radius: 3px;
            }
            
            #messages-area::-webkit-scrollbar-thumb:hover {
                background: #a8a8a8;
            }
            
            #suggestions-bar {
                background: var(--bg-suggestions-bar);
                padding: 15px 25px;
                border-top: 1px solid rgba(255,255,255,0.1);
                flex-shrink: 0;
                transition: all 0.3s ease;
            }
            
            .suggestions-container {
                display: flex;
                gap: 12px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .suggestion-item {
                background: var(--bg-suggestion);
                backdrop-filter: blur(10px);
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
                color: var(--text-white);
                font-size: 14px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .suggestion-item:hover {
                background: var(--bg-suggestion-hover);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px var(--shadow-secondary);
            }
            
            .suggestion-icon {
                font-size: 16px;
            }
            
            .suggestion-text {
                font-weight: 500;
            }
            
            .example-queries {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 15px;
            }
            
            .example-query {
                background: #e3f2fd;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 13px;
                color: #1565c0;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .example-query:hover {
                background: #bbdefb;
                transform: translateY(-1px);
            }
            
            @media (max-width: 768px) {
                .container {
                    height: 100vh;
                    border-radius: 0;
                }
                
                .header {
                    padding: 20px;
                    flex-direction: column;
                    gap: 15px;
                }
                
                .header-content {
                    text-align: center;
                }
                
                .header h1 {
                    font-size: 24px;
                }
                
                .theme-toggle {
                    align-self: center;
                    font-size: 12px;
                    padding: 6px 10px;
                }
                
                .message-content {
                    max-width: 85%;
                }
                
                .suggestions-container {
                    flex-direction: column;
                    gap: 8px;
                }
                
                .suggestion-item {
                    justify-content: center;
                    padding: 10px 16px;
                }
                
                #suggestions-bar {
                    padding: 12px 15px;
                }
                
                #input-container {
                    padding: 15px;
                    gap: 10px;
                }
                
                #message-input {
                    font-size: 16px;
                    padding: 12px 16px;
                }
                
                #send-btn {
                    padding: 12px 20px;
                    min-width: 80px;
                    font-size: 14px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-content">
                    <h1>🤖 AI Society</h1>
                    <p>Dynamic Model Router - Democratizing AI Access</p>
                </div>
                <button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark/light theme">
                    <span class="theme-icon" id="theme-icon">🌙</span>
                    <span id="theme-text">Dark</span>
                </button>
            </div>
            
            <div id="status-bar">
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span id="status-text">Initializing system...</span>
                </div>
                <div id="model-count">Models: Loading...</div>
                <button class="tech-info-toggle" onclick="toggleTechInfo()" title="Toggle technical information">
                    <span id="tech-icon">📊</span>
                    <span>Tech Info</span>
                </button>
            </div>
            
            <div id="tech-panel" class="tech-panel hidden">
                <div class="tech-grid">
                    <div class="tech-card">
                        <h4>🧠 Memory System</h4>
                        <div id="memory-stats">
                            <span>Short-term: <span id="memory-short">0</span> entries</span>
                            <span>Token usage: <span id="memory-tokens">0%</span></span>
                            <span>Context: <span id="memory-context">Standard</span></span>
                        </div>
                    </div>
                    <div class="tech-card">
                        <h4>🎯 Current Model</h4>
                        <div id="model-stats">
                            <span>Active: <span id="active-model">None</span></span>
                            <span>Type: <span id="model-type">N/A</span></span>
                            <span>Context: <span id="model-context">N/A</span></span>
                            <span>Size: <span id="model-size">N/A</span></span>
                        </div>
                    </div>
                    <div class="tech-card">
                        <h4>⚡ Performance</h4>
                        <div id="perf-stats">
                            <span>Last response: <span id="response-time">0ms</span></span>
                            <span>Routing method: <span id="routing-method">Standard</span></span>
                            <span>Confidence: <span id="routing-confidence">N/A</span></span>
                        </div>
                    </div>
                    <div class="tech-card">
                        <h4>🖥️ System</h4>
                        <div id="system-stats">
                            <span>Available models: <span id="total-models">0</span></span>
                            <span>Local models: <span id="local-models">0</span></span>
                            <span>Session: <span id="session-id">Loading...</span></span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="chat-container">
                <div class="welcome-message" id="welcome-message">
                    <h3>Welcome to AI Society! 🌟</h3>
                    <p>I intelligently route your queries to the best specialized models from Ollama's library.</p>
                    <p>This hybrid approach uses minimal resources while providing access to powerful AI capabilities.</p>
                </div>
                
                <div id="messages-area"></div>
            </div>
            
            <!-- Persistent Suggestions Bar -->
            <div id="suggestions-bar">
                <div class="suggestions-container">
                    <div class="suggestion-item" onclick="sendExampleQuery('Write a Python function to sort a list')">
                        <span class="suggestion-icon">💻</span>
                        <span class="suggestion-text">Coding Help</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('Explain quantum computing simply')">
                        <span class="suggestion-icon">🧠</span>
                        <span class="suggestion-text">Complex Topics</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('What is 15 * 23 + 89?')">
                        <span class="suggestion-icon">🔢</span>
                        <span class="suggestion-text">Math Problems</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('Debug this JavaScript error: Cannot read property of undefined')">
                        <span class="suggestion-icon">🐛</span>
                        <span class="suggestion-text">Debug Code</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('Translate this to French: Hello, how are you today?')">
                        <span class="suggestion-icon">🌍</span>
                        <span class="suggestion-text">Translation</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('Write a creative story about AI and humans')">
                        <span class="suggestion-icon">✨</span>
                        <span class="suggestion-text">Creative Writing</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('Analyze this data pattern: [1,4,9,16,25,36]')">
                        <span class="suggestion-icon">📊</span>
                        <span class="suggestion-text">Data Analysis</span>
                    </div>
                    <div class="suggestion-item" onclick="sendExampleQuery('How do neural networks learn?')">
                        <span class="suggestion-icon">🤖</span>
                        <span class="suggestion-text">AI/ML Topics</span>
                    </div>
                </div>
            </div>
            
            <div id="input-container">
                <input type="text" id="message-input" placeholder="Ask anything... I'll route to the perfect model!" maxlength="2000">
                <button id="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            let ws;
            let isConnected = false;
            let typingIndicator = null;
            let messageCount = 0;
            
            const chatContainer = document.getElementById('chat-container');
            const messagesArea = document.getElementById('messages-area');
            const messageInput = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');
            const statusText = document.getElementById('status-text');
            const modelCount = document.getElementById('model-count');
            const welcomeMessage = document.getElementById('welcome-message');
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const host = window.location.host || '192.168.1.62:8000';
                ws = new WebSocket(`${protocol}//${host}/ws`);
                
                ws.onopen = function() {
                    isConnected = true;
                    const statusDot = document.querySelector('.status-dot');
                    statusDot.classList.add('connected');
                    statusText.textContent = 'Connected - Ready to chat!';
                    updateModelCount();
                    updateTechInfo();
                    removeWelcomeMessage();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleResponse(data);
                };
                
                ws.onclose = function() {
                    isConnected = false;
                    const statusDot = document.querySelector('.status-dot');
                    statusDot.classList.remove('connected');
                    statusText.textContent = 'Disconnected - Attempting to reconnect...';
                    
                    // Attempt to reconnect after 3 seconds
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    isConnected = false;
                    const statusDot = document.querySelector('.status-dot');
                    statusDot.classList.remove('connected');
                    statusText.textContent = 'Connection error - Please refresh the page';
                };
            }
            
            function handleResponse(data) {
                // Handle connection status
                if (data.status === 'connected') {
                    statusText.textContent = `Connected with Memory Enabled`;
                    
                    // Store session ID for tech panel
                    if (data.session_id) {
                        window.sessionId = data.session_id;
                    }
                    
                    return;
                }
                
                // Handle status messages
                if (data.status === 'processing') {
                    // Update typing indicator with progress and memory info
                    if (typingIndicator) {
                        let memoryInfo = '';
                        if (data.memory_messages) {
                            memoryInfo = ` (${data.memory_messages} messages in memory)`;
                        }
                        
                        typingIndicator.querySelector('.typing-indicator').innerHTML = `
                            <span>🔄 ${data.message}${memoryInfo}</span>
                            <div class="typing-dots">
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                            </div>
                        `;
                    }
                    statusText.textContent = data.message;
                    return;
                }
                
                // Remove typing indicator
                if (typingIndicator) {
                    typingIndicator.remove();
                    typingIndicator = null;
                }
                
                // Handle error responses
                if (data.error) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message assistant';
                    messageDiv.innerHTML = `
                        <div class="message-content" style="border-left: 4px solid #ff4444;">
                            <div class="model-info" style="background: #ffebee; color: #c62828;">
                                <span class="model-icon">⚠️</span>
                                <span>Error</span>
                            </div>
                            <div>${escapeHtml(data.message)}</div>
                        </div>
                    `;
                    messagesArea.appendChild(messageDiv);
                    scrollToBottom();
                    
                    // Re-enable input
                    messageInput.disabled = false;
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send';
                    statusText.textContent = 'Error occurred - Ready to try again';
                    return;
                }
                
                // Add assistant message
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message assistant';
                const messageText = data.message || data.response || 'No response received';
                
                // Create model info with optimization details
                let modelInfoHtml = `
                    <div class="model-info">
                        <span class="model-icon">🎯</span>
                        <span>${data.model}</span>
                        <span style="margin-left: 8px; opacity: 0.7;">
                            ${data.response_time_ms}ms
                        </span>
                    </div>
                `;
                
                // Add query optimization info and comparison if available
                let queryComparisonHtml = '';
                let memoryInfoHtml = '';
                
                if (data.query_enhanced) {
                    const optimizationType = data.optimization_applied || 'enhanced';
                    modelInfoHtml += `
                        <div class="optimization-info">
                            <span>🔧</span>
                            <span class="query-enhanced">Query ${optimizationType}</span>
                            <span style="opacity: 0.8;">by ${data.meta_model || 'OpenAI'}</span>
                        </div>
                    `;
                    
                    // Show query comparison
                    queryComparisonHtml = `
                        <div class="query-comparison">
                            <div class="query-original">
                                <span class="query-label">Original:</span>${escapeHtml(data.original_query || 'N/A')}
                            </div>
                            <div class="query-optimized">
                                <span class="query-label">Enhanced:</span>${escapeHtml(data.optimized_query || 'N/A')}
                            </div>
                        </div>
                    `;
                }
                
                // Add memory information if available
                if (data.memory_enabled && data.conversation_length > 1) {
                    const contextUsed = data.context_used ? 'Context applied' : 'Direct query';
                    memoryInfoHtml = `
                        <div class="memory-info">
                            <span>🧠</span>
                            <span class="memory-enabled">${data.conversation_length} messages</span>
                            <span style="opacity: 0.8;">${contextUsed}</span>
                        </div>
                    `;
                }
                
                messageDiv.innerHTML = `
                    <div class="message-content">
                        ${modelInfoHtml}
                        ${memoryInfoHtml}
                        ${queryComparisonHtml}
                        <div>${formatMessage(messageText)}</div>
                    </div>
                `;
                
                messagesArea.appendChild(messageDiv);
                scrollToBottom();
                
                // Update status with optimization and memory info
                let statusText = `Last: ${data.model}`;
                if (data.specializations_used) {
                    const specs = data.specializations_used.join(', ');
                    statusText += ` (${specs})`;
                }
                if (data.query_enhanced) {
                    statusText += ` - Query optimized`;
                }
                if (data.memory_enabled && data.conversation_length) {
                    statusText += ` - Memory: ${data.conversation_length} msgs`;
                }
                statusText += ` - ${data.response_time_ms}ms`;
                
                document.getElementById('status-text').textContent = statusText;
                
                // Store technical information for tech panel
                window.lastMemoryStats = {
                    memory_messages: data.memory_messages || data.conversation_length || 0,
                    token_usage_percent: ((data.memory_messages || 0) / 20) * 100, // Rough estimate
                    context_used: data.context_used || false
                };
                
                window.lastModelInfo = {
                    model: data.model,
                    specializations: data.specializations_used || [],
                    context: data.model_info?.context || 'N/A',
                    size: data.model_info?.size || 'N/A'
                };
                
                window.lastPerformance = {
                    response_time: data.response_time_ms,
                    routing_method: data.routing_method,
                    confidence: data.confidence || data.routing_confidence
                };
                
                // Update tech panel if visible
                const techPanel = document.getElementById('tech-panel');
                if (techPanel && !techPanel.classList.contains('hidden')) {
                    updateTechInfo();
                }
                
                // Re-enable input
                messageInput.disabled = false;
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                messageInput.focus();
            }
            
            function formatMessage(text) {
                // Basic formatting for code blocks and line breaks
                return text
                    .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                    .replace(/`([^`]+)`/g, '<code>$1</code>')
                    .replace(/\\n/g, '<br>');
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            function sendMessage(message = null) {
                const query = message || messageInput.value.trim();
                if (!query || !isConnected) return;
                
                // Hide welcome message after first message (but keep suggestions)
                if (messageCount === 0 && welcomeMessage) {
                    welcomeMessage.style.opacity = '0';
                    welcomeMessage.style.transform = 'scale(0.9)';
                    welcomeMessage.style.transition = 'all 0.3s ease';
                    setTimeout(() => {
                        welcomeMessage.style.display = 'none';
                    }, 300);
                }
                
                // Add user message to messages area
                const userDiv = document.createElement('div');
                userDiv.className = 'message user';
                userDiv.innerHTML = `
                    <div class="message-content">${escapeHtml(query)}</div>
                `;
                messagesArea.appendChild(userDiv);
                
                // Add typing indicator
                typingIndicator = document.createElement('div');
                typingIndicator.className = 'message assistant';
                typingIndicator.innerHTML = `
                    <div class="typing-indicator">
                        <span>🤔 Selecting best model</span>
                        <div class="typing-dots">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                `;
                messagesArea.appendChild(typingIndicator);
                
                scrollToBottom();
                
                // Send message
                ws.send(query);
                
                // Clear and disable input
                messageInput.value = '';
                messageInput.disabled = true;
                sendBtn.disabled = true;
                sendBtn.textContent = 'Thinking...';
                
                // Update status
                statusText.textContent = 'Processing query and selecting optimal model...';
                
                messageCount++;
            }
            
            function sendExampleQuery(query) {
                messageInput.value = query;
                sendMessage();
            }
            
            function scrollToBottom() {
                setTimeout(() => {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }, 100);
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            async function updateModelCount() {
                try {
                    console.log('🔍 Fetching model count from /api/stats...');
                    const response = await fetch('/api/stats');
                    console.log('📡 Response status:', response.status);
                    
                    const result = await response.json();
                    console.log('📊 Stats response:', result);
                    
                    if (result.status === 'success' && result.data) {
                        const stats = result.data;
                        const total = stats.total_models || stats.total_models_available || 0;
                        const local = stats.local_models || 0;
                        const newText = `Models: ${local}/${total} local`;
                        console.log('✅ Setting model count to:', newText);
                        modelCount.textContent = newText;
                    } else if (result.data) {
                        // Handle direct stats response (legacy format)
                        const total = result.data.total_models || result.data.total_models_available || 0;
                        const local = result.data.local_models || 0;
                        const newText = `Models: ${local}/${total} local`;
                        console.log('✅ Setting model count (legacy) to:', newText);
                        modelCount.textContent = newText;
                    } else if (result.error) {
                        console.log('❌ API returned error:', result.error);
                        modelCount.textContent = 'Models: Router not ready';
                    } else {
                        console.log('⚠️ Unexpected response format:', result);
                        modelCount.textContent = 'Models: Loading...';
                    }
                } catch (error) {
                    console.error('💥 Error fetching stats:', error);
                    modelCount.textContent = 'Models: Connection error';
                }
            }
            
            // Event listeners
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // Auto-resize input
            messageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 100) + 'px';
            });
            
            // Initialize connection
            connectWebSocket();
            
            // Initialize data loading
            updateModelCount(); // Call immediately on page load
            updateTechInfo();   // Call immediately on page load
            
            // Theme management
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Update theme toggle button
                updateThemeButton(newTheme);
            }
            
            function updateThemeButton(theme) {
                const themeIcon = document.getElementById('theme-icon');
                const themeText = document.getElementById('theme-text');
                
                if (theme === 'dark') {
                    themeIcon.textContent = '☀️';
                    themeText.textContent = 'Light';
                } else {
                    themeIcon.textContent = '🌙';
                    themeText.textContent = 'Dark';
                }
            }
            
            function initializeTheme() {
                // Check for saved theme preference or default to 'light'
                const savedTheme = localStorage.getItem('theme');
                const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                
                let theme = 'light'; // Default to light theme
                
                if (savedTheme) {
                    theme = savedTheme;
                } else if (systemPrefersDark) {
                    theme = 'dark';
                }
                
                document.documentElement.setAttribute('data-theme', theme);
                updateThemeButton(theme);
            }
            
            // Technical information panel
            function toggleTechInfo() {
                const techPanel = document.getElementById('tech-panel');
                const techIcon = document.getElementById('tech-icon');
                
                if (techPanel.classList.contains('hidden')) {
                    techPanel.classList.remove('hidden');
                    techIcon.textContent = '📈';
                    updateTechInfo();
                } else {
                    techPanel.classList.add('hidden');
                    techIcon.textContent = '📊';
                }
            }
            
            function updateTechInfo() {
                // Fetch latest system stats
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(result => {
                        if (result.status === 'success' && result.data) {
                            const stats = result.data;
                            document.getElementById('total-models').textContent = stats.total_models || 0;
                            document.getElementById('local-models').textContent = stats.local_models || 0;
                            document.getElementById('session-id').textContent = stats.active_sessions > 0 ? `Active (${stats.active_sessions})` : 'Ready';
                        } else {
                            // Handle error case
                            document.getElementById('total-models').textContent = 'Error';
                            document.getElementById('local-models').textContent = 'Error';
                            document.getElementById('session-id').textContent = 'Error';
                        }
                    })
                    .catch(error => {
                        console.log('Stats fetch failed:', error);
                        document.getElementById('total-models').textContent = 'N/A';
                        document.getElementById('local-models').textContent = 'N/A';
                        document.getElementById('session-id').textContent = 'Offline';
                    });

                // Update memory stats if available
                if (window.lastMemoryStats) {
                    document.getElementById('memory-short').textContent = window.lastMemoryStats.memory_messages || 0;
                    document.getElementById('memory-tokens').textContent = Math.round(window.lastMemoryStats.token_usage_percent || 0) + '%';
                    document.getElementById('memory-context').textContent = window.lastMemoryStats.context_used ? 'Enhanced' : 'Standard';
                }

                // Update model stats if available
                if (window.lastModelInfo) {
                    document.getElementById('active-model').textContent = window.lastModelInfo.model || 'None';
                    document.getElementById('model-type').textContent = window.lastModelInfo.specializations?.[0] || 'N/A';
                    document.getElementById('model-context').textContent = window.lastModelInfo.context || 'N/A';
                    document.getElementById('model-size').textContent = window.lastModelInfo.size || 'N/A';
                }
                if (window.lastPerformance) {
                    document.getElementById('response-time').textContent = window.lastPerformance.response_time + 'ms';
                    document.getElementById('routing-method').textContent = window.lastPerformance.routing_method || 'Standard';
                    document.getElementById('routing-confidence').textContent = window.lastPerformance.confidence ? Math.round(window.lastPerformance.confidence * 100) + '%' : 'N/A';
                }
                
                // Update system stats
                document.getElementById('session-id').textContent = window.sessionId ? window.sessionId.substring(0, 12) + '...' : 'Loading...';
            }
            
            // Initialize theme on load
            initializeTheme();
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem('theme')) {
                    const theme = e.matches ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', theme);
                    updateThemeButton(theme);
                }
            });
            
            // Update model count periodically
            setInterval(updateModelCount, 30000); // Every 30 seconds
            
            // Update tech info periodically (only if panel is visible)
            setInterval(() => {
                const techPanel = document.getElementById('tech-panel');
                if (!techPanel.classList.contains('hidden')) {
                    updateTechInfo();
                }
            }, 15000); // Every 15 seconds
            
            // CSS animation for fade out
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeOut {
                    from { opacity: 1; transform: scale(1); }
                    to { opacity: 0; transform: scale(0.95); }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    session_id = await manager.connect(websocket)
    conversation = manager.get_conversation(session_id)
    
    # Send welcome message with session info
    await websocket.send_json({
        'status': 'connected',
        'message': f'Connected! Session: {session_id[:12]}... Memory enabled.',
        'model': 'system',
        'response_time_ms': 0,
        'session_id': session_id
    })
    
    try:
        while True:
            # Receive message
            query = await websocket.receive_text()
            
            if not router:
                await websocket.send_json({
                    'error': 'Router not initialized',
                    'message': 'System is starting up, please try again in a moment.',
                    'model': 'system',
                    'response_time_ms': 0
                })
                continue

            try:
                # Add user message to conversation memory
                await conversation.add_message('user', query)
                
                # Create context-aware query using conversation history
                context_query = await conversation.get_context_for_query(query)
                conversation_summary = conversation.get_conversation_summary()
                
                # Send processing status with memory info
                await websocket.send_json({
                    'status': 'processing',
                    'message': f'Processing with hybrid memory... {conversation_summary}',
                    'model': 'system',
                    'response_time_ms': 0,
                    'memory_messages': len(conversation.messages),
                    'context_length': len(context_query)
                })
                
                # Enhanced context for router
                enhanced_context = {
                    'session_id': session_id,
                    'conversation_history': conversation.messages[-3:],  # Last 3 messages
                    'conversation_summary': conversation_summary,
                    'message_count': len(conversation.messages),
                    'previous_model': conversation.messages[-2].get('model') if len(conversation.messages) >= 2 else None
                }
                
                # Process query with router using context-aware query
                print(f"🧠 Using hybrid memory: {len(conversation.messages)} messages in memory")
                print(f"📝 Context query: {context_query[:100]}...")
                
                result = router.query_model(context_query, model_name=None, context=enhanced_context)
                print(f"📋 Result from router: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                
                # Add assistant response to conversation memory
                assistant_response = result.get('response', result.get('message', ''))
                await conversation.add_message(
                    'assistant', 
                    assistant_response, 
                    model=result.get('model'),
                    metadata={
                        'routing_method': result.get('routing_method'),
                        'confidence': result.get('confidence'),
                        'query_enhanced': result.get('query_enhanced', False)
                    }
                )
                
                # Add memory information to result
                result.update({
                    'session_id': session_id,
                    'memory_enabled': True,
                    'conversation_length': len(conversation.messages),
                    'context_used': len(context_query) > len(query),
                    'conversation_summary': conversation_summary
                })
                
                # Send response
                print(f"📤 Sending WebSocket response with memory context...")
                await websocket.send_json(result)
                print(f"✅ WebSocket response sent successfully")
                
            except Exception as e:
                print(f"❌ Error in WebSocket endpoint: {e}")
                import traceback
                traceback.print_exc()
                
                error_response = {
                    'error': str(e),
                    'message': f'Sorry, I encountered an error: {str(e)}. Please try again.',
                    'model': 'error-handler',
                    'response_time_ms': 0,
                    'specializations_used': [],
                    'session_id': session_id,
                    'memory_enabled': True
                }
                await websocket.send_json(error_response)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"🔌 WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/stats")
async def get_stats():
    """Get system statistics for dashboard"""
    print("📊 Stats API called!")
    try:
        if not router:
            print("❌ Stats API error: Router not initialized")
            return {
                "status": "error",
                "message": "Router not initialized",
                "timestamp": datetime.now().isoformat()
            }
        
        # Get router stats with error handling
        router_stats = {}
        try:
            router_stats = router.get_stats() if hasattr(router, 'get_stats') else {}
            print(f"🔍 Router stats retrieved successfully: {list(router_stats.keys())}")
        except Exception as stats_error:
            print(f"⚠️ Router get_stats() failed: {stats_error}")
            # Fallback to manual calculation
            model_registry = router.model_registry if hasattr(router, 'model_registry') else {}
            router_stats = {
                'total_models_available': len(model_registry),
                'local_models': sum(1 for m in model_registry.values() if m.get('is_local', False)),
                'downloadable_models': len(model_registry) - sum(1 for m in model_registry.values() if m.get('is_local', False)),
                'queries_processed': len(getattr(router, 'performance_history', [])),
                'average_response_time': 0,
                'most_used_specializations': {}
            }
        
        # Get model registry safely
        model_registry = router.model_registry if hasattr(router, 'model_registry') else {}
        
        stats = {
            "total_models": router_stats.get('total_models_available', len(model_registry)),
            "local_models": router_stats.get('local_models', 0),
            "total_models_available": router_stats.get('total_models_available', len(model_registry)),
            "active_sessions": len(manager.conversations),
            "memory_enabled": True,
            "gpu_info": "RTX 3090 Compatible",
            "system_status": "operational",
            "queries_processed": router_stats.get('queries_processed', 0),
            "average_response_time": router_stats.get('average_response_time', 0)
        }
        
        print(f"📊 Returning stats: {stats}")
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Stats API error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return {
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/models")
async def get_models():
    """Get current model registry"""
    if not router:
        return {"error": "Router not initialized"}
    
    try:
        return {
            "models": router.model_registry,
            "stats": router.get_stats()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/recommendations")
async def get_recommendations():
    """Get recommended models to download"""
    if not router:
        return {"error": "Router not initialized"}
    
    try:
        recommendations = router.get_model_recommendations()
        return {"recommendations": recommendations}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/refresh")
async def refresh_models():
    """Manually trigger model registry refresh"""
    if not router:
        return {"error": "Router not initialized"}
    
    try:
        router.refresh_model_registry()
        stats = router.get_stats()
        return {
            "status": "success", 
            "message": "Model registry refreshed successfully",
            "stats": stats
        }
    except Exception as e:
        return {"error": f"Failed to refresh: {str(e)}"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        models = ollama.list()
        ollama_status = "connected"
        model_count = len(models['models'])
    except:
        ollama_status = "disconnected"
        model_count = 0
    
    return {
        "status": "healthy" if router else "initializing",
        "ollama_status": ollama_status,
        "local_models": model_count,
        "router_initialized": router is not None,
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 AI Society starting up...")
    print("📊 System Status:")
    print(f"   - Router: {'✅ Initialized' if router else '❌ Failed to initialize'}")
    
    if router:
        stats = router.get_stats()
        print(f"   - Models Available: {stats['total_models_available']}")
        print(f"   - Local Models: {stats['local_models']}")
    
    print("🌐 Web interface available at:")
    print("   - Local: http://localhost:8000") 
    print("   - Network: http://192.168.1.62:8000")

if __name__ == "__main__":
    print("="*50)
    print("🤖 AI Society - Dynamic Model Router")
    print("="*50)
    print("🎯 Democratizing AI Access with Efficient Routing")
    print("⚡ Optimized for RTX 3090 GPU")
    print("🔄 Dynamic Model Discovery from Ollama Library")
    print("="*50)
    
    # Check if Ollama is running
    try:
        ollama.list()
        print("✅ Ollama connection verified")
    except Exception as e:
        print(f"⚠️  Ollama not accessible: {e}")
        print("   Please ensure Ollama is running: 'ollama serve'")
    
    print("\n🌐 Starting web server...")
    print("📡 Available at:")
    print("   - Local: http://localhost:8000")
    print("   - Network: http://192.168.1.62:8000")
    print("   - API Docs: http://192.168.1.62:8000/docs")
    print("   - Health Check: http://192.168.1.62:8000/api/health")
    print("")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=False  # Reduce console noise
    )
