"""Entry point for ``mcp dev`` / MCP Inspector.

Usage:
    uv run mcp dev src/dev.py
"""

import logging
import sys
from pathlib import Path

from main import _find_default_env_file, _load_config, _register_tools

logger = logging.getLogger("testmo_mcp.dev")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger.info("Running tool registration for MCP Inspector (dev mode)")

env_file: Path | None = _find_default_env_file()
if env_file:
    logger.info(f"Loading configuration from .env file: {env_file}")
else:
    logger.info("Loading configuration from environment variables")

config = _load_config(env_file)
try:
    _register_tools(config)
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    logger.error("Please ensure TESTMO_URL and TESTMO_API_KEY are set")
    sys.exit(1)
except Exception as e:
    logger.error(f"Failed to register tools: {e}")
    sys.exit(1)
