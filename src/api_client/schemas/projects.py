"""Project schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiResponse,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    PaginatedApiRequest,
    PaginatedApiResponse,
    UserExpand,
)


class ProjectExpands(BaseModel):
    users: Optional[List[UserExpand]] = None


class Project(BaseModel):
    """Testmo project model."""

    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    is_completed: bool = Field(..., description="Whether project is completed")
    milestone_count: int = Field(..., description="Total number of milestones")
    milestone_active_count: int = Field(..., description="Number of active milestones")
    milestone_completed_count: int = Field(
        ..., description="Number of completed milestones"
    )
    run_count: int = Field(..., description="Total number of runs")
    run_active_count: int = Field(..., description="Number of active runs")
    run_closed_count: int = Field(..., description="Number of closed runs")
    session_count: int = Field(..., description="Total number of sessions")
    session_active_count: int = Field(..., description="Number of active sessions")
    session_closed_count: int = Field(..., description="Number of closed sessions")
    automation_source_count: int = Field(
        ..., description="Total number of automation sources"
    )
    automation_source_active_count: int = Field(
        ..., description="Number of active automation sources"
    )
    automation_source_retired_count: int = Field(
        ..., description="Number of completed automation sources"
    )
    automation_run_count: int = Field(
        ..., description="Total number of automation runs"
    )
    automation_run_active_count: int = Field(
        ..., description="Number of active automation runs"
    )
    automation_run_completed_count: int = Field(
        ..., description="Number of completed automation runs"
    )
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="User ID who created the project")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(
        None, description="User ID who last updated the project"
    )
    completed_at: Optional[str] = Field(None, description="Completion timestamp")


# GET /api/v1/projects request/response
class ListProjectsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """List projects request parameters."""

    SUPPORTED_EXPANDS = {ExpandsEnum.users}

    sort: Optional[Literal["projects:created_at", "projects:completed_at"]] = Field(
        None, description="Sort field (projects:created_at or projects:completed_at)"
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        None, description="Sort order (asc or desc)"
    )
    is_completed: Optional[bool] = Field(
        None, description="Filter by completion status"
    )


class ListProjectsApiResponse(
    PaginatedApiResponse[Project], ExpandedApiResponse[ProjectExpands]
):
    """Projects response with users expand."""


# GET /api/v1/projects/{project_id} request/response
class GetProjectApiResponse(ApiResponse[Project], ExpandedApiResponse[ProjectExpands]):
    """Single project response with expands."""
