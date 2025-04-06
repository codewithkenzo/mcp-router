# MCP Router

MCP Router is a Python package for interacting with Model Context Protocol (MCP) servers with OpenRouter LLM integration. It provides a backend for managing MCP servers, executing agent-based tasks, and orchestrating complex workflows using the Upsonic framework.

[![GitHub license](https://img.shields.io/github/license/kenzo/mcp-router)](https://github.com/kenzo/mcp-router/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

## 🚀 Features

- **MCP Server Management**: Add, edit, and remove MCP servers
- **OpenRouter Integration**: Query OpenRouter models directly for AI-assisted tasks
- **Upsonic Integration**: Orchestrate complex multi-step workflows with Upsonic
- **Intelligent Task Analysis**: Automatically determine which tools are needed for tasks
- **MCP Protocol Support**: Standardized interaction with MCP servers
- **API Framework**: Expose functionality via REST API endpoints

## 🏗️ Architecture

The package is structured as follows:

```
mcp_router/
├── __init__.py
├── main.py
├── cli/           # Command line interface
├── core/          # Core MCP and Upsonic integration
├── server_management/ # MCP server management
└── utils/         # Utility functions
```

## 📋 Prerequisites

- **Python 3.8+**
- **Docker** (optional, recommended for running MCP servers)

## 🔧 Installation

### Clone the repository
```bash
git clone https://github.com/codewithkenzo/mcp-router.git
cd mcp-router
```

### Install Python package
```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## 🚀 Usage

### Use as a module
```python
import mcp_router

# Initialize an MCP server manager
server_manager = mcp_router.core.server_manager.ServerManager()

# Get available MCP servers
servers = server_manager.get_servers()

# Use OpenRouter integration
from mcp_router.core import openrouter
response = openrouter.query("Tell me about MCP")
```

### Run the CLI
```bash
# From the project root with virtual environment activated
python -m mcp_router.cli.cli --help
```

## 🧩 Components

### MCP Server Management

The server management module handles:
- Reading MCP server configuration from `~/.cursor/mcp.json`
- Starting and stopping MCP servers
- Communicating with MCP servers

### Upsonic Integration

The Upsonic integration allows for:
- Creating agentic workflows with MCP tools
- Analyzing tasks to determine required tools
- Executing multi-step tasks with various MCP capabilities

### OpenRouter Integration

The OpenRouter module provides:
- Access to multiple LLM providers through a single API
- Query generation and response handling
- Token usage tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.github.io/) for the MCP specification
- [OpenRouter](https://openrouter.ai/) for providing access to various LLM models
- [Upsonic](https://github.com/upsonic/upsonic) for the agent framework 