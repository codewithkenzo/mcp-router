"""
Setup script for the MCP Router package.
"""

from setuptools import setup, find_packages

setup(
    name="mcp-router",
    version="1.0.0",
    description="A router for MCP queries with plugin system, adapter framework, and caching",
    author="Zeeeepa",
    author_email="info@zeeeepa.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=1.9.0",
        "sqlalchemy>=1.4.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.14.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
        ],
        "mcp": [
            "mcp>=0.1.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
