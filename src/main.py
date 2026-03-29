import argparse
import logging
import sys
from os import path
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from api_client import TestmoApiClientV1
from mcp_servers.testmo_web_ui_mcp_server import TestmoWebUiMCPServer
from mcp_servers.tool_manager import ToolManager
from testmo_config import McpServerConfig
from version import version

logger = logging.getLogger("testmo_mcp.main")


def _setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("testmo_mcp.main")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Testmo MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use .env file from default location (current directory or parent)
  python main.py

  # Use specific .env file
  python main.py --env-file /path/to/.env

  # Use environment variables only (no .env file)
  python main.py --no-env-file

  # Enable debug logging
  python main.py --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--env-file",
        type=Path,
        default=None,
        help="Path to .env file (default: searches for .env in current and parent directories)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"Testmo MCP Server version: {version}",
    )

    return parser.parse_args()


def _find_default_env_file() -> Path | None:
    """Search for a .env file in the current directory and its parents."""
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        env_file = candidate / ".env"
        if env_file.exists():
            return env_file
    return None


def _load_config(env_file: Path | None = None) -> McpServerConfig:
    """Load the configuration from the environment variables or the .env file."""
    resolved_env = env_file or _find_default_env_file()
    config = (
        McpServerConfig(_env_file=resolved_env) if resolved_env else McpServerConfig()
    )
    return config


def _register_tools(config: McpServerConfig) -> int:
    """
    Initialise API client, and register all tools on the global ``mcp`` FastMCP instance.  Returns the number of tools registered.
    """
    api_client = TestmoApiClientV1(config.testmo_url, config.testmo_api_key)
    mcp_server = TestmoWebUiMCPServer(api_client)

    tool_manager = ToolManager(config, [mcp_server])
    tool_manager.initialize()
    tools = tool_manager.convert_to_tools()

    for tool in tools.values():
        mcp.add_tool(
            tool.fn,
            name=tool.name,
            title=tool.title,
            description=tool.description,
            annotations=tool.annotations,
            icons=tool.icons,
            meta=tool.meta,
        )
    logger.info(
        f"Successfully registered {[tool.name for tool in tools.values()]} tools"
    )


mcp = FastMCP("testmo-mcp")


def main():
    """Main entry point for the MCP server."""
    args = _parse_args()
    global logger
    logger = _setup_logging(args.log_level)

    logger.info("Starting Testmo MCP Server...")

    # Resolve the env file path
    env_file: Path | None = None
    if args.env_file:
        logger.info(f"Loading configuration from: {args.env_file}")
        if not path.exists(args.env_file):
            logger.error(f"Specified .env file not found: {args.env_file}")
            sys.exit(1)
        env_file = args.env_file
    else:
        logger.info("Loading configuration from environment variables")

    config = _load_config(env_file)
    try:
        n_tools = _register_tools(config)
        logger.info(f"Successfully registered {n_tools} tools")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure TESTMO_URL and TESTMO_API_KEY are set")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to register tools: {e}")
        sys.exit(1)

    try:
        logger.info("Starting MCP server with stdio transport...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
