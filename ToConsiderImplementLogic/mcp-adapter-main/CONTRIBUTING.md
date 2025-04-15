# Contributing to MCP Adapter

Thank you for your interest in contributing to MCP Adapter! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please be respectful and considerate of others. We aim to foster an inclusive and welcoming community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
```bash
git clone https://github.com/your-username/mcp-adapter.git
cd mcp-adapter
```
3. **Set up the development environment**:
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode with all extras
pip install -e ".[dev,all]"
```

## Development Workflow

### Branch Naming

- `feature/your-feature-name` - For new features
- `bugfix/issue-description` - For bug fixes
- `docs/what-you-documented` - For documentation improvements
- `refactor/what-you-refactored` - For code refactoring

### Coding Standards

We follow these standards:

1. **Type hints**: Use type hints for all function parameters and return values
2. **Docstrings**: Write clear docstrings for all public modules, functions, classes, and methods
3. **Testing**: Write tests for all new functionality
4. **Code style**: We use Black for code formatting and isort for import sorting

You can check your code with:
```bash
# Format your code
black src tests
isort src tests

# Type checking
mypy src

# Run linters and tests
./run_tests.sh
```

## Pull Request Process

1. **Update the documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass** locally
4. **Create a pull request** with a clear description:
   - What changes you've made
   - Why you've made them
   - Any issues they address

## Testing

Run the test suite:
```bash
./run_tests.sh
```

Or run specific tests:
```bash
python -m unittest tests.core.test_client
```

## Adding Support for New LLM Providers

To add a new LLM provider:

1. Create a new file in `src/llm/` for your provider
2. Implement the `BaseLLMAdapter` interface
3. Add appropriate tests in `tests/llm/`
4. Update documentation to mention the new provider

## Release Process

Releases are managed by the maintainers. The general process is:

1. Update version number in `setup.py`
2. Update the `CHANGELOG.md`
3. Create a new GitHub release with release notes
4. Publish to PyPI

## Questions?

If you have any questions or need help, please open an issue on GitHub.

Thank you for contributing to MCP Adapter!