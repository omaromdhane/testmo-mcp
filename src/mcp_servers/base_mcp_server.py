"""Testmo MCP tools with separate global and locked contexts."""

import logging
from typing import ClassVar

from api_client import TestmoApiClientV1

logger = logging.getLogger("testmo_mcp.base_mcp_server")


class BaseMCPServer:
    """Shared context behavior for tool classes."""

    TOOL_NAMES: ClassVar[list[str]] = []

    def __init__(self, api_client: TestmoApiClientV1):
        self.api_client = api_client

    @classmethod
    def get_tool_names(cls) -> list[str]:
        """Return accessible tool names for this MCP context."""
        return cls.TOOL_NAMES
