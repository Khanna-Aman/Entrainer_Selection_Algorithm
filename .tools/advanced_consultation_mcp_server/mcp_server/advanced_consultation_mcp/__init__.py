"""Advanced Consultation MCP Server.

A three-stage consultation workflow using Gemini 3 Pro for deep analysis,
structured prompting, and recommendation extraction.

Tools:
  - capture_initial_request: Stage 0 - Capture user's request
  - start_advanced_consultation: Stage 1 - Generate structured prompt
  - fetch_consultation_response: Stage 2 - Get Gemini 3 Pro response
  - extract_consultation_recommendations: Stage 3 - Extract recommendations
  - run_full_consultation: Run all stages automatically
  - list_consultations: List available consultations

Usage:
  # As a module
  python -m advanced_consultation_mcp.server

  # With MCP client
  Configure in claude_desktop_config.json or VSCode settings
"""

from .server import main, main_sync, server

__all__ = ["main", "main_sync", "server"]
__version__ = "1.1.0"

