"""
Core Infrastructure Module
==========================

Shared infrastructure components used across all phases:
- Configuration management (Pydantic Settings)
- Database connections (Neo4j, ChromaDB)
- LLM clients (Gemini, Claude)
- Common data models
- Logging utilities
"""

from entrainer_selection.core.config import Settings, get_settings
from entrainer_selection.core.logging import setup_logging, get_logger

__all__ = [
    "Settings",
    "get_settings",
    "setup_logging",
    "get_logger",
]

