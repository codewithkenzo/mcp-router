# Active Context: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. Current Focus

-   Transitioning from direct MCP control via the UI to an agentic approach using Upsonic.
-   Planning the integration of the Upsonic framework (likely via a separate Python service).
-   Defining the backend API endpoints (Next.js) required to interact with the Upsonic service.
-   Refining the frontend UI to support prompt-based task initiation and task monitoring.
-   Initializing the project's Memory Bank documentation.

## 2. Recent Changes

-   Implemented backend API routes for direct Playwright MCP interaction:
    -   `/api/browser/navigate`
    -   `/api/browser/snapshot`
    -   `/api/browser/execute` (supporting basic `click` and `type` commands)
-   Created a server-side helper `executeMcpCommand` to handle MCP process spawning and communication.
-   Updated the `BrowserTab` component to use the new navigation and snapshot APIs.
-   Replaced screenshot display with raw accessibility snapshot JSON display.
-   Temporarily disabled instruction input box in `BrowserTab`.
-   Created initial Memory Bank files (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`).

## 3. Next Steps (High Level)

1.  **Complete Memory Bank Initialization:** Create `progress.md`.
2.  **Define Upsonic APIs:** Implement the placeholder Next.js API routes (`/api/upsonic/analyze`, `/api/upsonic/run`, `/api/upsonic/status/[taskId]`). These will initially return mock data or errors until the Python service exists.
3.  **Update Frontend (Query Tab):** Modify the `QueryTab` (or primary input area) to capture user prompts and call the new Upsonic API endpoints (`analyze` -> `run`).
4.  **Implement Task Tab:** Create or update `TasksTab` to poll the `/api/upsonic/status` endpoint and display task progress.
5.  **(Parallel/Later) Implement Upsonic Service (Python):** Build the actual Python/FastAPI service.

## 4. Active Decisions & Considerations

-   **Upsonic Service:** Confirming the approach of using a separate Python/FastAPI service for Upsonic orchestration is the most practical way forward given Upsonic's Python focus.
-   **Prompt Analysis:** How will the `/api/upsonic/analyze` step work? Will it be a simple keyword mapping initially, or require an actual LLM call? If LLM, which one and how will it be invoked (e.g., OpenRouter)?
-   **Tool Mapping:** How will the Python Upsonic service dynamically map MCP servers from `mcp.json` to Upsonic tools?
-   **Browser Tab Role:** How will the `BrowserTab` function alongside the agentic workflow? Primarily for viewing results/snapshots, or retain some direct control?

## 5. Blockers

-   None currently, proceeding with planning and initial API/UI scaffolding. 