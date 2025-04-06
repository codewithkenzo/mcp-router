# Project Brief: MCP Router

**Version:** 0.1
**Date:** 2024-04-06

## 1. Overview

MCP Router is a web-based frontend application designed to provide a user interface for interacting with various Model Context Protocol (MCP) servers. It aims to simplify the process of managing MCP configurations, executing tasks that leverage MCP tools (like browser automation, code execution, information retrieval), and potentially orchestrating complex workflows using an agent framework (Upsonic).

## 2. Goals

- Provide a unified interface for managing and interacting with different MCP servers.
- Enable browser automation tasks (navigation, interaction, scraping) via the Playwright MCP server.
- Allow users to query language models (e.g., via OpenRouter) through an appropriate MCP or direct integration.
- Integrate the Upsonic agent framework to orchestrate multi-step tasks involving multiple MCP tools.
- Implement AI-driven analysis of user prompts to determine the necessary MCP tools for a given task.
- Offer features for managing agents (or task templates), servers, and task history.
- Persist user settings and configurations.

## 3. Scope

- **Core Functionality:**
    - Frontend UI (Next.js/React/TypeScript).
    - Backend API routes (Next.js) for handling frontend requests.
    - Integration with configured MCP servers (initially Playwright, potentially others like GitHub, HackerNews).
    - Basic browser automation UI (URL bar, navigation, snapshot display).
    - Basic query interface for LLMs.
    - Upsonic agent framework integration (likely via a separate Python service).
    - Task management UI (list, status, results).
    - Server configuration display.
- **Out of Scope (Initially):**
    - Advanced agent creation/debugging UI.
    - Real-time collaborative features.
    - Complex scheduling beyond simple task execution.
    - User authentication/multi-user support.

## 4. Target Users

- Developers or power users working with MCP.
- Users needing a simplified interface for browser automation or interacting with various AI tools via MCP.
- Individuals experimenting with agentic workflows using MCP and Upsonic.

## 5. Success Metrics

- Successful execution of browser tasks via the UI and Playwright MCP.
- Successful execution of Upsonic tasks initiated from the UI.
- User ability to view configured MCP servers.
- User ability to track the status and results of initiated tasks. 