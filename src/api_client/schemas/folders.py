"""Folders API request/response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    PaginatedApiRequest,
    PaginatedApiResponse,
)


class RepositoryFolder(BaseModel):
    """GET /api/v1/projects/{project_id}/folders result item."""

    id: int = Field(..., description="Folder ID")
    project_id: int = Field(..., description="Project ID")
    repo_id: int = Field(..., description="Repository ID")
    name: str = Field(..., description="Folder name")
    parent_id: Optional[int] = Field(None, description="Parent folder ID")
    depth: int = Field(..., description="Folder depth")
    docs: Optional[str] = Field(None, description="Folder notes/description")
    display_order: int = Field(..., description="Display order")


# GET /api/v1/projects/{project_id}/folders request/response
class ListFoldersApiRequest(PaginatedApiRequest):
    """GET /api/v1/projects/{project_id}/folders request."""

    project_id: int = Field(..., description="Project ID")
    sort: Optional[
        Literal[
            "repository_folders:display_order",
            "repository_folders:name",
            "repository_folders:id",
            "repository_folders:depth",
        ]
    ] = Field(None, description="Sort field for folders list")
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
    parent_id: Optional[int] = Field(
        None, description="Return only folders with this parent ID"
    )
    name: Optional[str] = Field(None, description="Folder name partial match")


class ListFoldersApiResponse(PaginatedApiResponse[RepositoryFolder]):
    """GET /api/v1/projects/{project_id}/folders response."""
