from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from datetime import datetime
import threading
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    import ollama
    from daemon.model_discovery import ModelDiscoveryDaemon
    from routing.enhanced_intelligent_router import EnhancedIntelligentRouter
    
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

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

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
                background: var(--bg-status);
                padding: 12px 25px;
                font-size: 13px;
                color: var(--text-status);
                border-bottom: 1px solid var(--border-secondary);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.3s ease;
            }
            
            .status-indicator {
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
                    <div class="suggestion-item" onclick="sendExampleQuery('Tell me a creative story')">
                        <span class="suggestion-icon">✨</span>
                        <span class="suggestion-text">Creative Writing</span>
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
                    statusText.textContent = 'Connected - Ready to chat!';
                    updateModelCount();
                    removeWelcomeMessage();
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleResponse(data);
                };
                
                ws.onclose = function() {
                    isConnected = false;
                    statusText.textContent = 'Disconnected - Attempting to reconnect...';
                    
                    // Attempt to reconnect after 3 seconds
                    setTimeout(connectWebSocket, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    statusText.textContent = 'Connection error - Please refresh the page';
                };
            }
            
            function handleResponse(data) {
                // Handle status messages
                if (data.status === 'processing') {
                    // Update typing indicator with progress
                    if (typingIndicator) {
                        typingIndicator.querySelector('.typing-indicator').innerHTML = `
                            <span>🔄 ${data.message}</span>
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
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <div class="model-info">
                            <span class="model-icon">🎯</span>
                            <span>${data.model}</span>
                            <span style="margin-left: 8px; opacity: 0.7;">
                                ${data.response_time_ms}ms
                            </span>
                        </div>
                        <div>${formatMessage(messageText)}</div>
                    </div>
                `;
                
                messagesArea.appendChild(messageDiv);
                scrollToBottom();
                
                // Update status
                const specs = data.specializations_used ? data.specializations_used.join(', ') : 'general';
                statusText.textContent = `Last: ${data.model} (${specs}) - ${data.response_time_ms}ms`;
                
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
                    const response = await fetch('/api/stats');
                    const stats = await response.json();
                    modelCount.textContent = `Models: ${stats.local_models}/${stats.total_models_available} local`;
                } catch (error) {
                    modelCount.textContent = 'Models: Loading...';
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
    await manager.connect(websocket)
    context = {'session_id': datetime.now().isoformat()}
    
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
                # Send processing status
                await websocket.send_json({
                    'status': 'processing',
                    'message': 'Analyzing query and selecting optimal model...',
                    'model': 'system',
                    'response_time_ms': 0
                })
                
                # Process query with router
                result = router.query_model(query, model_name=None, context=context)
                print(f"📋 Result from router: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                
                # Update context for next query
                context['previous_model'] = result['model']
                
                # Send response
                print(f"📤 Sending WebSocket response...")
                await websocket.send_json(result)
                print(f"✅ WebSocket response sent successfully")
                
            except Exception as e:
                error_response = {
                    'error': str(e),
                    'message': f'Sorry, I encountered an error: {str(e)}. Please try again.',
                    'model': 'error-handler',
                    'response_time_ms': 0,
                    'specializations_used': []
                }
                await websocket.send_json(error_response)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not router:
        return {"error": "Router not initialized"}
    
    try:
        stats = router.get_stats()
        return stats
    except Exception as e:
        return {"error": str(e)}

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
