# MCP Adapter Tests

This directory contains tests for the MCP adapter project.

## Running Tests

To run the tests with coverage, use the `run_tests.py` script in the project root:

```bash
python run_tests.py
```

If you don't have the coverage package installed, install it first:

```bash
pip install coverage
```

## Test Structure

- `core/`: Tests for core components (client, tools, orchestrator, logger)
- `llm/`: Tests for LLM adapters (OpenAI, Gemini)

## Coverage Goals

The goal is to achieve at least 80% code coverage across the project.

## Writing Tests

When writing tests:

1. Focus on testing edge cases and error handling
2. Use mocks for external dependencies
3. Ensure tests are isolated and don't depend on each other
4. Include both positive and negative test cases
5. Test async functions properly using event loops