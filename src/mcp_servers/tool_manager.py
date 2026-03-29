import inspect
import logging
from functools import wraps
from typing import Callable

from mcp.server.fastmcp.tools import Tool
from pydantic import BaseModel

from mcp_servers.base_mcp_server import BaseMCPServer
from testmo_config import McpServerConfig

logger = logging.getLogger("testmo_mcp.tool_manager")


class ToolDefinition(BaseModel):
    """Intermediate representation of a tool before conversion to MCP Tool."""

    name: str
    description: str
    fn: Callable

    class Config:
        arbitrary_types_allowed = True


class ToolManager:
    """
    Tool manager for the MCP server.
    Handles both global mode (requires project_id) and locked mode (project_id pre-filled).
    """

    def __init__(self, config: McpServerConfig, mcp_servers: list[BaseMCPServer]):
        self.tool_definitions = {}
        self.config = config
        self.mcp_servers = mcp_servers
        self.mode = "locked_project" if self.config.project_id is not None else "global"

    def _create_locked_wrapper(self, fn, project_id: int):
        """Create a wrapper function that pre-fills project_id while preserving function metadata."""

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            return await fn(*args, project_id=project_id, **kwargs)

        # Copy the signature but remove project_id parameter
        sig = inspect.signature(fn)
        new_params = [
            param
            for name, param in sig.parameters.items()
            if name not in ("self", "project_id")
        ]
        wrapper.__signature__ = sig.replace(parameters=new_params)

        return wrapper

    def initialize(self):
        """Initialize and return all tool definitions from registered MCP servers."""
        self.tool_definitions = {}

        for mcp_server in self.mcp_servers:
            for tool_name in mcp_server.get_tool_names():
                tool_fn = getattr(mcp_server, tool_name)
                tool_description = tool_fn.__doc__ or ""

                if self.mode == "locked_project":
                    # Check if this tool has a project_id parameter
                    sig = inspect.signature(tool_fn)
                    if "project_id" in sig.parameters:
                        # Create a wrapper function with project_id pre-filled
                        tool_fn = self._create_locked_wrapper(
                            tool_fn, self.config.project_id
                        )
                        logger.debug(
                            f"Created locked-mode tool definition: {tool_name} (project_id={self.config.project_id})"
                        )
                    else:
                        logger.debug(
                            f"Created tool definition: {tool_name} (no project_id parameter)"
                        )
                else:
                    logger.debug(f"Created global-mode tool definition: {tool_name}")

                self.tool_definitions[tool_name] = ToolDefinition(
                    name=tool_name,
                    description=tool_description,
                    fn=tool_fn,
                )

        logger.debug(
            f"Initialized {len(self.tool_definitions)} tool definitions in {self.mode} mode"
        )

    def get_tool_definition(self, name: str) -> ToolDefinition | None:
        """Get a specific tool definition by name."""
        return self.tool_definitions.get(name)

    def get_tool_definitions(self) -> dict[str, ToolDefinition]:
        """Get all tool definitions as a dictionary."""
        return self.tool_definitions

    def convert_to_tools(self) -> dict[str, Tool]:
        """Convert all ToolDefinitions to MCP Tool objects."""
        tools = {}
        for name, tool_def in self.tool_definitions.items():
            tool = Tool.from_function(
                tool_def.fn,
                name=tool_def.name,
                description=tool_def.description,
            )
            tools[name] = tool
            logger.debug(f"Converted tool definition to Tool: {name}")

        return tools
