#!/usr/bin/env python3
"""
Setup script for the MCP Router package.
"""

from setuptools import setup, find_packages

setup(
    name="mcp-router",
    version="0.1.0",
    description="A robust system for managing and routing requests to hundreds of MCP servers",
    author="Zeeeepa",
    author_email="info@zeeeepa.com",
    url="https://github.com/Zeeeepa/Sequencer",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.1.0",
        "requests>=2.25.0",
        "aiohttp>=3.7.4",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
            "black>=20.8b1",
            "isort>=5.7.0",
            "mypy>=0.800",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
