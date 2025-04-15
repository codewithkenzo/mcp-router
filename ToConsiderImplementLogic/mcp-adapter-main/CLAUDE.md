# MCP Adapter Development Guidelines

## Build/Test Commands
- Setup: `pip install -e .` (installs package in development mode)
- Run all tests: `./run_tests.sh`
- Run single test: `python tests/core/test_tools.py` or `python -m unittest tests.core.test_tools.TestTool.test_tool_init`
- Run with coverage: `python -m coverage run -m unittest discover tests`

## Code Style
- **Imports**: Standard libs first, then third-party, then local (separated by newlines)
- **Types**: Use type hints for all function parameters and return values
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error handling**: Always use try/except/finally blocks, validate tool calls before execution
- **Documentation**: Module-level docstrings, function docstrings with parameter descriptions
- **Structure**: Wrap code in async functions, use proper client cleanup in finally blocks
- **Testing**: Each module should have corresponding test module in tests/ directory

## Best Practices
- Always validate tool_name and tool_args before using them
- Always close clients in finally blocks
- Use descriptive client_name values
- Log session start/end with proper status
- Add proper docstrings to all public methods