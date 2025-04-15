from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-adapter",
    version="0.1.0",
    author="MCP Team",
    author_email="mcp@example.com",
    description="Python adapters for connecting LLMs with the Model Context Protocol (MCP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mcp-adapter",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/mcp-adapter/issues",
        "Documentation": "https://github.com/yourusername/mcp-adapter#readme",
        "Source Code": "https://github.com/yourusername/mcp-adapter",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "mcp>=0.1.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.23.0",
        "pydantic>=2.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "openai": ["openai>=1.12.0"],
        "gemini": ["google-generativeai>=0.3.0"],
        "all": [
            "openai>=1.12.0",
            "google-generativeai>=0.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "coverage>=7.0.0",
        ],
    },
)