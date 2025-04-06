# System Patterns: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. High-Level Architecture

MCP Router follows a multi-component architecture:

1.  **Frontend:** A Single Page Application (SPA) built with Next.js/React, providing the user interface.
2.  **Backend API (Next.js):** API routes within the Next.js application that handle requests from the frontend.
3.  **Upsonic Service (Python - Proposed):** A separate background service responsible for managing and executing agentic tasks using the Upsonic framework.
4.  **MCP Servers:** External processes (run via npx, uvx, Docker) that expose tool capabilities according to the Model Context Protocol.

```mermaid
flowchart TD
    User --> FE[Frontend UI (Next.js/React)]
    FE --> API[Backend API (Next.js)]

    subgraph Direct MCP Interaction
        API -- JSON-RPC Request --> MCPExec[lib/mcp/execute.ts]
        MCPExec -- Spawns Process --> MCPServers[(MCP Servers)]
        MCPServers -- JSON-RPC Response --> MCPExec
        MCPExec --> API
    end

    subgraph Agentic Workflow (Upsonic)
        API -- Task Request --> UpsonicSvc[Upsonic Service (Python/FastAPI)]
        UpsonicSvc -- Configures/Runs --> UpsonicLib[Upsonic Library]
        UpsonicLib -- Manages/Calls --> MCPExecUpsonic[MCP Execution (within Upsonic)]
        MCPExecUpsonic -- Spawns Process --> MCPServers
        MCPServers -- Response --> MCPExecUpsonic
        MCPExecUpsonic --> UpsonicLib
        UpsonicLib -- Results --> UpsonicSvc
        UpsonicSvc -- Status/Results --> API
    end

    API --> FE
```

## 2. Key Components & Interactions

-   **Frontend (`frontend/src`):** Handles UI rendering, state management (React state, potentially Zustand/Jotai later), and calls to the Next.js backend API.
-   **Backend API (`frontend/src/app/api`):**
    -   Provides endpoints for direct MCP interaction (e.g., `/api/browser/...`). These use the `executeMcpCommand` helper.
    -   Provides endpoints for Upsonic task management (e.g., `/api/upsonic/...`). These will act as intermediaries, forwarding requests to the Python Upsonic Service.
-   **MCP Execution Helper (`frontend/src/lib/mcp/execute.ts`):** A server-side utility in the Next.js backend responsible for reading `~/.cursor/mcp.json`, spawning the appropriate MCP server process, sending a JSON-RPC request, and parsing the response. This is used for *direct* MCP calls from the API.
-   **Upsonic Service (Python - Proposed):**
    -   Runs independently (e.g., as a Docker container or background process).
    -   Exposes a simple API (e.g., using FastAPI) for starting tasks, getting status, etc.
    -   Uses the Upsonic Python library to define and run tasks.
    -   Reads `~/.cursor/mcp.json` to dynamically configure Upsonic tools corresponding to the available MCP servers.
    -   Handles the interaction with MCP servers *within the context of an Upsonic task*.
-   **MCP Servers:** Configured via `~/.cursor/mcp.json`. These are the actual tools (Playwright, GitHub, etc.) that perform actions.

## 3. Data Flow (Upsonic Task)

1.  User enters a prompt in the Frontend UI.
2.  Frontend calls the Next.js `/api/upsonic/analyze` endpoint (implementation TBD, might involve LLM call).
3.  Analyze endpoint returns a structured task definition.
4.  Frontend calls the Next.js `/api/upsonic/run` endpoint with the task definition.
5.  Next.js API calls the Python Upsonic Service's "run task" endpoint.
6.  Upsonic Service creates an Upsonic `Task` object, configuring tools based on `mcp.json` and the analyzed prompt.
7.  Upsonic library executes the task, potentially calling multiple MCP servers via its own execution logic.
8.  Frontend periodically polls the Next.js `/api/upsonic/status/[taskId]` endpoint.
9.  Next.js API calls the Python Upsonic Service's "get status" endpoint.
10. Upsonic Service returns the current status and any results.
11. Frontend updates the UI.

## 4. Design Patterns

-   **API Layer:** Backend-for-Frontend (BFF) pattern using Next.js API routes.
-   **Service Separation:** Decoupling the core agent logic (Python/Upsonic) from the web frontend/API layer (Node.js/Next.js).
-   **Configuration-Driven:** MCP server interactions are driven by the `~/.cursor/mcp.json` configuration file.
-   **Agentic Orchestration:** Utilizing the Upsonic framework for managing multi-step, tool-using tasks. 