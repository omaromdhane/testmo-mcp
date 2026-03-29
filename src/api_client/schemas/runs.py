"""Run API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiResponse,
    ConfigExpand,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    IssueExpand,
    MilestoneExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    StateExpand,
    StatusExpand,
    UserExpand,
)


class RunLink(BaseModel):
    name: str = Field(..., description="Run link name")
    note: Optional[str] = Field(None, description="Run link note")
    url: str = Field(..., description="Run link URL")


class Run(BaseModel):
    """GET /api/v1/runs result item."""

    id: int = Field(..., description="Run ID")
    project_id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Run name")
    config_id: Optional[int] = Field(
        None, description="Configuration ID"
    )  # Conflict between openapi and testmo documentation
    milestone_id: Optional[int] = Field(
        None, description="Milestone ID"
    )  # Conflict between openapi and testmo documentation
    state_id: int = Field(..., description="Workflow state ID")
    forecast: Optional[int] = Field(None, description="Forecast duration")
    forecast_completed: Optional[int] = Field(
        None, description="Completed forecast duration"
    )
    elapsed: Optional[int] = Field(None, description="Elapsed duration")
    is_started: bool = Field(..., description="Whether run has started")
    is_closed: bool = Field(..., description="Whether run has closed")
    issues: list[int] = Field(
        default_factory=list, description="Issue IDs linked to run"
    )
    links: list[RunLink] = Field(default_factory=list, description="Run links")
    tags: list[str] = Field(default_factory=list, description="Run tags")
    untested_count: int = Field(..., description="Untested count")
    status1_count: int = Field(..., description="Status 1 count")
    status2_count: int = Field(..., description="Status 2 count")
    status3_count: int = Field(..., description="Status 3 count")
    status4_count: int = Field(..., description="Status 4 count")
    status5_count: int = Field(..., description="Status 5 count")
    status6_count: int = Field(..., description="Status 6 count")
    status7_count: int = Field(..., description="Status 7 count")
    status8_count: int = Field(..., description="Status 8 count")
    status9_count: int = Field(..., description="Status 9 count")
    status10_count: int = Field(..., description="Status 10 count")
    status11_count: int = Field(..., description="Status 11 count")
    status12_count: int = Field(..., description="Status 12 count")
    status13_count: int = Field(..., description="Status 13 count")
    status14_count: int = Field(..., description="Status 14 count")
    status15_count: int = Field(..., description="Status 15 count")
    status16_count: int = Field(..., description="Status 16 count")
    status17_count: int = Field(..., description="Status 17 count")
    status18_count: int = Field(..., description="Status 18 count")
    status19_count: int = Field(..., description="Status 19 count")
    status20_count: int = Field(..., description="Status 20 count")
    status21_count: int = Field(..., description="Status 21 count")
    status22_count: int = Field(..., description="Status 22 count")
    status23_count: int = Field(..., description="Status 23 count")
    status24_count: int = Field(..., description="Status 24 count")
    success_count: int = Field(..., description="Success count")
    failure_count: int = Field(..., description="Failure count")
    completed_count: int = Field(..., description="Completed count")
    total_count: int = Field(..., description="Total count")
    started_at: Optional[str] = Field(None, description="Start timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Created by user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    closed_at: Optional[str] = Field(None, description="Close timestamp")
    closed_by: Optional[int] = Field(None, description="Closed by user ID")


# Expands schema
class RunExpands(BaseModel):
    configs: Optional[List[ConfigExpand]] = None
    issues: Optional[List[IssueExpand]] = None
    milestones: Optional[List[MilestoneExpand]] = None
    states: Optional[List[StateExpand]] = None
    statuses: Optional[List[StatusExpand]] = None
    users: Optional[List[UserExpand]] = None


SUPPORTED_RUN_EXPANDS = {
    ExpandsEnum.configs,
    ExpandsEnum.issues,
    ExpandsEnum.milestones,
    ExpandsEnum.states,
    ExpandsEnum.statuses,
    ExpandsEnum.users,
}


# GET /api/v1/projects/{project_id}/runs request/response
class ListRunsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/projects/{project_id}/runs request."""

    SUPPORTED_EXPANDS = SUPPORTED_RUN_EXPANDS
    project_id: int = Field(..., description="Project ID")
    sort: Optional[Literal["runs:created_at", "runs:closed_at"]] = Field(
        None, description="Sort field for runs list"
    )
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
    closed_after: Optional[str] = Field(
        None, description="Filter runs closed after ISO8601 date-time"
    )
    closed_before: Optional[str] = Field(
        None, description="Filter runs closed before ISO8601 date-time"
    )
    config_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of configurations to filter by"
    )
    created_after: Optional[str] = Field(
        None, description="Filter runs created after ISO8601 date-time"
    )
    created_before: Optional[str] = Field(
        None, description="Filter runs created before ISO8601 date-time"
    )
    created_by: Optional[List[int]] = Field(
        None, description="Comma-separated list of users to filter by"
    )
    is_closed: Optional[bool] = Field(None, description="Filter active/closed runs")
    milestone_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of milestones to filter by"
    )
    state_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of states to filter by"
    )
    tags: Optional[List[str]] = Field(
        None, description="Comma-separated list of tags to filter by"
    )


class ListRunsApiResponse(PaginatedApiResponse[Run], ExpandedApiResponse[RunExpands]):
    """GET /api/v1/projects/{project_id}/runs response."""


# GET /api/v1/runs/{run_id} request/response
class GetRunApiRequest(ExpandedApiRequest):
    """GET /api/v1/runs/{run_id} request."""

    SUPPORTED_EXPANDS = SUPPORTED_RUN_EXPANDS
    run_id: int = Field(..., description="Run ID")


class GetRunApiResponse(ApiResponse[Run], ExpandedApiResponse[RunExpands]):
    """GET /api/v1/runs/{run_id} response."""
