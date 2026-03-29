import re

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class McpServerConfig(BaseSettings):
    """MCP server configuration."""

    testmo_url: str = Field(..., description="Testmo instance URL")
    testmo_api_key: str = Field(..., description="Testmo API key")
    project_id: int | None = Field(
        None, description="Testmo project ID to lock the MCP server to"
    )

    @field_validator("testmo_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize URL."""
        if not v.startswith(("https://")):
            raise ValueError("URL must start with https://")
        # must be in the format of https://<domain>.testmo.net
        if not re.match(r"https://[a-zA-Z0-9.-]+\.testmo\.net", v):
            raise ValueError("URL must be in the format of https://<domain>.testmo.net")
        return v.rstrip("/")

    @field_validator("testmo_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate and normalize API key."""
        return v.strip()

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, v: int | None) -> int | None:
        """Validate and normalize project ID."""
        if v is not None and v <= 0:
            raise ValueError("Project ID must be a positive integer")
        return v
