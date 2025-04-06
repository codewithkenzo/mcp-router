# MCP Router

MCP Router is a powerful system for interacting with Model Context Protocol (MCP) servers with OpenRouter LLM integration. It provides an elegant web interface for managing MCP servers, executing agent-based tasks, and orchestrating complex workflows using the Upsonic framework.

[![GitHub license](https://img.shields.io/github/license/kenzo/mcp-router)](https://github.com/kenzo/mcp-router/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Node.js Version](https://img.shields.io/badge/node-18%2B-brightgreen)](https://nodejs.org/)

<p align="center">
  <img src="https://raw.githubusercontent.com/username/mcp-router/main/assets/logo.png" alt="MCP Router Logo" width="200">
</p>

## 🚀 Features

- **MCP Server Management**: Add, edit, and remove MCP servers with intuitive UI
- **OpenRouter Integration**: Query OpenRouter models directly for AI-assisted tasks
- **Browser Automation**: Control browser actions via Playwright MCP
- **Agentic Workflows**: Orchestrate complex multi-step workflows with Upsonic
- **Intelligent Task Analysis**: Automatically determine which tools are needed for tasks
- **Task Monitoring**: Track status and results of all tasks in real-time
- **Modern UI**: Built with Next.js, React, TypeScript, and shadcn/ui components

## 🏗️ Architecture

The project consists of two main components:

1. **Frontend**: Next.js web application (TypeScript/React)
   - Modern UI with shadcn/ui components and Tailwind CSS
   - API routes for communicating with the Python backend
   - Browser automation interface
   - Task monitoring dashboard

2. **Backend**: Python-based API server
   - MCP server management and communication
   - Upsonic integration for agentic workflows
   - OpenRouter integration for LLM capabilities
   - Task orchestration and monitoring

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**
- **Docker** (optional, recommended for running MCP servers)

## 🔧 Installation

### Clone the repository
```bash
git clone https://github.com/username/mcp-router.git
cd mcp-router
```

### Install Python backend
```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Install Next.js frontend
```bash
cd frontend
npm install
# or
yarn install
```

## 🚀 Usage

### Start the Python backend
```bash
# From the project root with virtual environment activated
python -m mcp_router
```

### Start the Next.js frontend
```bash
# From the frontend directory
npm run dev
# or
yarn dev
```

Then open your browser and navigate to [http://localhost:3000](http://localhost:3000).

## 🧩 Components

### Python Backend

The Python backend handles:
- MCP server configuration management
- Communication with MCP servers (Playwright, etc.)
- Integration with the Upsonic agent framework
- Task state management and reporting
- OpenRouter API integration

```
mcp_router/
├── __init__.py
├── main.py
├── cli/           # Command line interface
├── core/          # Core MCP and Upsonic integration
├── server_management/ # MCP server management
└── utils/         # Utility functions
```

### Next.js Frontend

The frontend provides:
- Modern, responsive UI
- API routes for communicating with Python backend
- Browser automation interface
- Task status dashboard
- Server configuration display

```
frontend/
├── public/
├── src/
│   ├── app/
│   │   ├── api/  # Next.js API routes
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── tabs/
│   │   └── ui/
│   ├── context/
│   └── lib/
└── package.json
```

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
- [shadcn/ui](https://ui.shadcn.com/) for the accessible UI components
- [Next.js](https://nextjs.org/) for the React framework 