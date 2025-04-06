# Technical Context: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. Core Technologies

-   **Frontend Framework:** Next.js (v14+ App Router) with React (v18+)
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS with shadcn/ui components
-   **Agent Framework:** Upsonic (Python)
-   **Backend Service (Upsonic):** Python (v3.9+) with FastAPI (Proposed)
-   **Process Management (Node.js):** Node.js `child_process` module (used in `executeMcpCommand`)
-   **Package Manager:** npm

## 2. Key Libraries & Tools

-   **Frontend:**
    -   `react`, `react-dom`
    -   `next`
    -   `tailwindcss`
    -   `lucide-react` (Icons)
    -   `@radix-ui/*` (Primitives for shadcn/ui)
    -   `class-variance-authority`, `clsx`, `tailwind-merge` (Styling helpers)
    -   `sonner` or built-in `useToast` (Notifications)
-   **Backend (Next.js API):**
    -   Built-in Next.js API route handlers
    -   Node.js built-in modules (`child_process`, `fs`, `path`, `os`)
-   **Upsonic Service (Python - Proposed):**
    -   `upsonic`
    -   `fastapi`
    -   `uvicorn` (ASGI server)
    -   `pydantic` (Data validation)

## 3. Development Setup

-   **Prerequisites:**
    -   Node.js (v18+ recommended)
    -   npm
    -   Python (v3.9+ for Upsonic service)
    -   pip (Python package installer)
    -   Docker (Optional but recommended for running MCP servers and the Upsonic service consistently)
-   **Installation:**
    1.  Clone the repository.
    2.  Navigate to the `frontend` directory.
    3.  Run `npm install`.
    4.  (If implementing Python service) Set up a Python virtual environment (`python -m venv .venv`, `source .venv/bin/activate`) and install Python requirements (`pip install -r requirements.txt`).
-   **Running Locally:**
    1.  Start the Next.js development server: `npm run dev` (from `frontend` directory).
    2.  (If implementing Python service) Start the FastAPI server: `uvicorn main:app --reload` (adjust command based on file structure).
    3.  Ensure required MCP servers (e.g., Playwright) can be started (check `~/.cursor/mcp.json` configuration and necessary dependencies like `npx`, `docker`). Playwright might require `npx playwright install` initially.

## 4. Configuration

-   **MCP Servers:** Defined in `~/.cursor/mcp.json`. The application reads this file at runtime to determine how to launch MCP servers.
-   **Environment Variables:** Potentially needed for API keys (e.g., OpenRouter, GitHub PAT for specific MCPs), database connections (if added later), or Upsonic service URL.

## 5. Constraints & Considerations

-   **Cross-Service Communication:** The Next.js backend needs to communicate reliably with the proposed Python Upsonic service (likely via HTTP requests).
-   **Process Spawning:** The `executeMcpCommand` function relies on the ability to spawn external processes (`npx`, `uvx`, `docker`) from the Node.js environment. Permissions and PATH environment variables might be relevant.
-   **State Management:** Frontend state complexity might increase. Consider dedicated state management libraries (Zustand, Jotai) if React context/state becomes unwieldy.
-   **Error Handling:** Robust error handling is needed across the frontend, Next.js API, Upsonic service, and MCP interactions.
-   **Security:** Environment variables (like API keys) must be handled securely. Direct execution of arbitrary commands based on user input should be avoided.
-   **Upsonic Integration:** The specific implementation details of integrating Upsonic (dynamic tool loading based on `mcp.json`, task state management) need careful design within the Python service. 