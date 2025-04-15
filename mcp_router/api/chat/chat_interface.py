"""
Chat interface for MCP Router API.
Provides a simple web interface for interacting with LLM providers.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..api_manager import APIManager

logger = logging.getLogger(__name__)

class ChatInterface:
    """
    Chat interface for MCP Router API.
    Provides a simple web interface for interacting with LLM providers.
    """
    
    def __init__(self, api_manager: APIManager, host: str = "127.0.0.1", port: int = 8000):
        """
        Initialize the chat interface.
        
        Args:
            api_manager: The API manager instance.
            host: The host to bind to.
            port: The port to bind to.
        """
        self.api_manager = api_manager
        self.host = host
        self.port = port
        self.app = FastAPI(title="MCP Router Chat Interface")
        self.setup_routes()
        
    def setup_routes(self):
        """
        Set up the FastAPI routes.
        """
        # Set up static files and templates
        static_dir = Path(__file__).parent / "static"
        templates_dir = Path(__file__).parent / "templates"
        
        # Create directories if they don't exist
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create a simple index.html template if it doesn't exist
        index_html = templates_dir / "index.html"
        if not index_html.exists():
            with open(index_html, "w") as f:
                f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Router Chat Interface</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #chat-container {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        #provider-selector {
            margin-bottom: 10px;
        }
        #message-form {
            display: flex;
        }
        #message-input {
            flex-grow: 1;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-right: 10px;
        }
        button {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .user-message {
            background-color: #e6f7ff;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .assistant-message {
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>MCP Router Chat Interface</h1>
    
    <div id="provider-selector">
        <label for="provider">Select Provider:</label>
        <select id="provider">
            <!-- Will be populated dynamically -->
        </select>
        
        <label for="model" style="margin-left: 10px;">Model:</label>
        <select id="model">
            <!-- Will be populated dynamically -->
        </select>
    </div>
    
    <div id="chat-container"></div>
    
    <form id="message-form">
        <input type="text" id="message-input" placeholder="Type your message..." required>
        <button type="submit">Send</button>
    </form>
    
    <script>
        // Connect to WebSocket
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const chatContainer = document.getElementById('chat-container');
        const messageForm = document.getElementById('message-form');
        const messageInput = document.getElementById('message-input');
        const providerSelect = document.getElementById('provider');
        const modelSelect = document.getElementById('model');
        
        // Handle WebSocket connection open
        ws.onopen = function(event) {
            console.log('WebSocket connection established');
            
            // Request available providers
            ws.send(JSON.stringify({
                type: 'get_providers'
            }));
        };
        
        // Handle WebSocket messages
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'providers') {
                // Populate provider selector
                providerSelect.innerHTML = '';
                data.providers.forEach(provider => {
                    const option = document.createElement('option');
                    option.value = provider;
                    option.textContent = provider;
                    providerSelect.appendChild(option);
                });
                
                // Request models for the first provider
                if (data.providers.length > 0) {
                    ws.send(JSON.stringify({
                        type: 'get_models',
                        provider: data.providers[0]
                    }));
                }
            } else if (data.type === 'models') {
                // Populate model selector
                modelSelect.innerHTML = '';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.id;
                    modelSelect.appendChild(option);
                });
            } else if (data.type === 'message') {
                // Add message to chat
                const messageDiv = document.createElement('div');
                messageDiv.className = data.role === 'user' ? 'user-message' : 'assistant-message';
                messageDiv.textContent = data.content;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        };
        
        // Handle WebSocket errors
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        // Handle WebSocket connection close
        ws.onclose = function(event) {
            console.log('WebSocket connection closed');
        };
        
        // Handle form submission
        messageForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const message = messageInput.value.trim();
            if (message) {
                // Send message to server
                ws.send(JSON.stringify({
                    type: 'chat',
                    provider: providerSelect.value,
                    model: modelSelect.value,
                    message: message
                }));
                
                // Clear input
                messageInput.value = '';
            }
        });
        
        // Handle provider change
        providerSelect.addEventListener('change', function() {
            // Request models for the selected provider
            ws.send(JSON.stringify({
                type: 'get_models',
                provider: providerSelect.value
            }));
        });
    </script>
</body>
</html>
                """)
        
        # Set up static files
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Set up templates
        templates = Jinja2Templates(directory=str(templates_dir))
        
        # Set up routes
        @self.app.get("/", response_class=HTMLResponse)
        async def get_index(request: Request):
            return templates.TemplateResponse("index.html", {"request": request})
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message["type"] == "get_providers":
                        # Get available providers
                        providers = self.api_manager.get_available_providers()
                        await websocket.send_json({
                            "type": "providers",
                            "providers": providers
                        })
                    
                    elif message["type"] == "get_models":
                        # Get available models for the provider
                        provider = message["provider"]
                        try:
                            models = await self.api_manager.get_available_models(provider)
                            await websocket.send_json({
                                "type": "models",
                                "models": models
                            })
                        except Exception as e:
                            logger.error(f"Error getting models for provider {provider}: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Error getting models: {str(e)}"
                            })
                    
                    elif message["type"] == "chat":
                        # Process chat message
                        provider = message["provider"]
                        model = message.get("model")
                        user_message = message["message"]
                        
                        # Send user message to client
                        await websocket.send_json({
                            "type": "message",
                            "role": "user",
                            "content": user_message
                        })
                        
                        try:
                            # Generate response
                            response = await self.api_manager.generate_text(
                                provider=provider,
                                prompt=user_message,
                                model=model
                            )
                            
                            # Send assistant message to client
                            await websocket.send_json({
                                "type": "message",
                                "role": "assistant",
                                "content": response
                            })
                        except Exception as e:
                            logger.error(f"Error generating text: {e}")
                            await websocket.send_json({
                                "type": "message",
                                "role": "assistant",
                                "content": f"Error: {str(e)}"
                            })
            
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
    
    def run(self):
        """
        Run the chat interface.
        """
        uvicorn.run(self.app, host=self.host, port=self.port)
    
    async def start_background(self):
        """
        Start the chat interface in the background.
        """
        config = uvicorn.Config(self.app, host=self.host, port=self.port)
        server = uvicorn.Server(config)
        await server.serve()
