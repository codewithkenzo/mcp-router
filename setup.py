#!/usr/bin/env python3
"""
Setup script for mcp-router.
"""

import os
import re
from setuptools import setup, find_packages

# Extract version from package __init__.py
def get_version():
    init_path = os.path.join("mcp_router", "__init__.py")
    if not os.path.isfile(init_path):
        return "0.1.0"  # Default version
    with open(init_path, "r") as f:
        version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', f.read())
    if version_match:
        return version_match.group(1)
    return "0.1.0"  # Default version if not found

# Read long description from README
def get_long_description():
    readme_path = "mcp_router/README.md"
    if os.path.isfile(readme_path):
        with open(readme_path, "r") as f:
            return f.read()
    return "MCP Router for Dolphin-MCP with OpenRouter integration"

setup(
    name="mcp-router",
    version=get_version(),
    description="MCP Router for Dolphin-MCP with OpenRouter integration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Kenzo",
    author_email="kenzo@example.com",
    url="https://github.com/user/mcp-router",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.6.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
        "toml>=0.10.2",
        "psutil>=5.9.0",
        "flask>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pylint>=2.13.0",
            "black>=22.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-router=mcp_router.cli.cli:main",
            "mcp-router-web=mcp_router.frontend.app:main",
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
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 