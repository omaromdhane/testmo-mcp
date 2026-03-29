"""Issues API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import PaginatedApiRequest, PaginatedApiResponse


class IssueConnection(BaseModel):
    """GET /api/v1/issues/connections result item."""

    integration_id: int = Field(..., description="Issue tracker integration ID")
    integration_type: int = Field(..., description="Integration type")
    integration_name: str = Field(..., description="Integration name")
    connection_id: int = Field(..., description="Connection ID")
    connection_name: str = Field(..., description="Connection name")
    connection_project_id: int = Field(..., description="Mapped project ID in tracker")
    connection_project_name: str = Field(
        ..., description="Mapped project name in tracker"
    )
    is_active: bool = Field(..., description="Whether connection is active")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class ListIssueConnectionsApiRequest(PaginatedApiRequest):
    """GET /api/v1/issues/connections request."""

    sort: Optional[
        Literal[
            "connections:integration_name",
            "connections:integration_id",
            "connections:connection_id",
            "connections:connection_name",
            "connections:connection_project_id",
            "connections:connection_project_name",
            "connections:integration_type",
            "connections:is_active",
            "connections:created_at",
            "connections:updated_at",
        ]
    ] = Field(
        "connections:integration_name", description="Sort field for connections list"
    )
    order: Optional[Literal["asc", "desc"]] = Field("asc", description="Sort order")
    integration_id: Optional[List[int]] = Field(
        None, description="List of integration IDs"
    )
    integration_name: Optional[str] = Field(
        None, description="Integration name partial match"
    )
    connection_id: Optional[List[int]] = Field(
        None, description="List of connection IDs"
    )
    connection_name: Optional[str] = Field(
        None, description="Connection name partial match"
    )
    connection_project_id: Optional[List[int]] = Field(
        None, description="List of mapped project IDs"
    )
    connection_project_name: Optional[str] = Field(
        None, description="Mapped project name partial match"
    )
    integration_type: Optional[List[int]] = Field(
        None, description="List of integration types"
    )
    is_active: Optional[bool] = Field(
        None, description="Filter active/inactive connections"
    )


class ListIssueConnectionsApiResponse(PaginatedApiResponse[IssueConnection]):
    """GET /api/v1/issues/connections response."""
