# Product Context: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. Problem Space

The Model Context Protocol (MCP) offers a powerful standard for LLMs to interact with external tools and data sources. However, managing multiple MCP servers, understanding their capabilities, and orchestrating tasks that utilize them can be complex and require significant technical setup.

- Users need a way to easily configure and view available MCP servers.
- Executing simple tasks (like navigating a browser or fetching data) often involves manual command-line interaction or custom scripting.
- Orchestrating complex workflows involving multiple MCP tools requires dedicated agent frameworks, which themselves might lack user-friendly interfaces.
- Determining *which* MCP tools are needed for a high-level user request requires manual analysis or sophisticated AI logic.

## 2. Proposed Solution

MCP Router provides a graphical user interface to bridge this gap. It acts as a central hub for:

- **Discoverability:** Displaying configured MCP servers and potentially their capabilities.
- **Interaction:** Allowing users to directly invoke specific MCP actions (like browser navigation) or submit higher-level prompts.
- **Orchestration:** Integrating with the Upsonic agent framework to manage complex tasks defined by user prompts.
- **Intelligence:** (Future) Using an LLM to analyze prompts and automatically select the appropriate MCP tools for Upsonic to orchestrate.

## 3. User Experience Goals

- **Simplicity:** Abstract away the complexities of direct MCP interaction and Upsonic setup.
- **Clarity:** Provide clear feedback on task execution, status, and results.
- **Flexibility:** Allow both direct MCP interaction (for simple tasks/debugging) and higher-level prompt-based task initiation.
- **Control:** Give users visibility into the configured servers and the status of their running tasks.

## 4. Key Features from User Perspective

- **Browser Control:** Input a URL, navigate, see the page state (via accessibility snapshot), and potentially trigger basic actions (click/type).
- **Prompt-Driven Tasks:** Enter a natural language prompt (e.g., "Summarize the key points on playwright.dev"). The application (using Upsonic) figures out the steps (navigate, get content, summarize) and executes them.
- **Task Monitoring:** See a list of running and completed tasks, their status, and any output/results.
- **Server Overview:** View the list of MCP servers the application is configured to use.
- **Settings:** Configure application behavior (e.g., themes, potentially API keys if needed later). 