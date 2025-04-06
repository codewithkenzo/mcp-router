# Progress: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. What Works

-   **Core Frontend Structure:** Basic Next.js application with Tailwind CSS and shadcn/ui is set up.
-   **Tab Navigation:** UI includes tabs for different sections (Browser, Models, Agents, etc. - though most are placeholders).
-   **Theme Toggle:** Dark/Light mode switching works.
-   **Direct Playwright Interaction (Backend):**
    -   The `executeMcpCommand` helper successfully reads `~/.cursor/mcp.json` and spawns MCP processes.
    -   API routes (`/api/browser/navigate`, `/api/browser/snapshot`, `/api/browser/execute`) correctly call `executeMcpCommand` to interact with the Playwright MCP server.
-   **Direct Playwright Interaction (Frontend):**
    -   The `BrowserTab` component can initiate navigation via the backend API.
    -   It can trigger and display the raw JSON of an accessibility snapshot from the current page in the controlled browser.
    -   Basic back/forward/refresh controls are functional (triggering navigation/snapshotting).
-   **Memory Bank:** Initial documentation files created.

## 2. What's Left to Build (Immediate Focus - Upsonic Integration)

-   **Upsonic API Scaffolding (Next.js):** Create placeholder API routes for `/api/upsonic/analyze`, `/api/upsonic/run`, `/api/upsonic/status/[taskId]`.
-   **Frontend Prompt Input:** Modify a UI section (likely `QueryTab` or a new central input) to accept general prompts.
-   **Frontend Task Initiation:** Connect the prompt input to call the `/analyze` and `/run` Upsonic APIs.
-   **Frontend Task Monitoring:** Implement the `TasksTab` to poll the `/status` API and display task information.
-   **Upsonic Service (Python):** The entire separate service needs to be designed and built.
    -   FastAPI setup.
    -   Upsonic library integration.
    -   Dynamic tool loading from `mcp.json`.
    -   API endpoint logic (run task, get status).
-   **Prompt Analysis Logic:** Implement the actual logic for the `/analyze` step (simple keyword mapping or LLM call).

## 3. What's Left to Build (Longer Term - Based on Original Plan)

-   Real Model Integration (`ModelsTab`, `QueryTab`, `lib/api.ts`)
-   Agent Management (`AgentsTab`, `lib/agents.ts`)
-   Server Management (`ServersTab`, `lib/servers.ts`, backend API for listing servers)
-   Settings & Configuration (`SettingsTab`, `lib/settings.ts`)
-   MCP Modules Management (`McpModulesTab`, `lib/mcp-modules.ts`)
-   Enhanced Browser UI (visual snapshot rendering, interactive elements)
-   General Improvements (responsive design, auth, tests, etc.)

## 4. Current Status

-   Phase 1 (Setup & Documentation) of the Upsonic integration plan is nearing completion.
-   Direct browser control functionality is partially implemented and working at a basic level.
-   The project is ready to begin scaffolding the API and UI components for Upsonic-based task orchestration.

## 5. Known Issues

-   The `BrowserTab` currently displays raw snapshot JSON, which is not user-friendly.
-   No actual task orchestration or prompt analysis is implemented yet.
-   Error handling might need further refinement across different layers.
-   The Python Upsonic service does not exist.
-   Other tabs (Models, Agents, Servers) contain only mock data/UI. 