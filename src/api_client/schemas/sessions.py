"""Sessions API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiResponse,
    ConfigExpand,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    FieldValueExpand,
    IssueExpand,
    MilestoneExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    StateExpand,
    StatusExpand,
    TemplateExpand,
    UserExpand,
)


# ============================================================================
# Session expands schema
# ============================================================================
class SessionExpands(BaseModel):
    configs: Optional[List[ConfigExpand]] = None
    field_values: Optional[List[FieldValueExpand]] = None
    issues: Optional[List[IssueExpand]] = None
    milestones: Optional[List[MilestoneExpand]] = None
    states: Optional[List[StateExpand]] = None
    statuses: Optional[List[StatusExpand]] = None
    templates: Optional[List[TemplateExpand]] = None
    users: Optional[List[UserExpand]] = None


SUPPORTED_SESSION_EXPANDS = {
    ExpandsEnum.configs,
    ExpandsEnum.field_values,
    ExpandsEnum.issues,
    ExpandsEnum.milestones,
    ExpandsEnum.states,
    ExpandsEnum.statuses,
    ExpandsEnum.templates,
    ExpandsEnum.users,
}


# ============================================================================
# Session schema
# ============================================================================
class Session(BaseModel):
    id: int = Field(..., description="Session ID")
    project_id: int = Field(..., description="Project ID")
    template_id: int = Field(..., description="Template ID")
    name: str = Field(..., description="Session name")
    config_id: Optional[int] = Field(
        None, description="Configuration ID"
    )  # Conflict between openapi and testmo documentation
    milestone_id: Optional[int] = Field(
        None, description="Milestone ID"
    )  # Conflict between openapi and testmo documentation
    state_id: int = Field(..., description="State ID")
    assignee_id: Optional[int] = Field(
        None, description="Assignee user ID"
    )  # Conflict between openapi and testmo documentation
    estimate: Optional[int] = Field(None, description="Estimate duration")
    forecast: Optional[int] = Field(None, description="Forecast duration")
    elapsed: Optional[int] = Field(None, description="Elapsed duration")
    is_started: bool = Field(..., description="Whether session has started")
    is_closed: bool = Field(..., description="Whether session is closed")
    issues: list[int] = Field(default_factory=list, description="Issue IDs")
    tags: list[str] = Field(default_factory=list, description="Session tags")
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


# ============================================================================
# GET /projects/{project_id}/sessions request/response
# ============================================================================
class ListSessionsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/projects/{project_id}/sessions request."""

    SUPPORTED_EXPANDS = SUPPORTED_SESSION_EXPANDS
    project_id: int = Field(..., description="Project ID")
    sort: Optional[Literal["sessions:created_at", "sessions:closed_at"]] = Field(
        None, description="Sort field for sessions list"
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        None, description="Sort order (ascending or descending) (default: desc)"
    )
    assignee_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of assignees to filter by"
    )
    closed_after: Optional[str] = Field(
        None, description="Filter sessions closed after ISO8601 date-time"
    )
    closed_before: Optional[str] = Field(
        None, description="Filter sessions closed before ISO8601 date-time"
    )
    config_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of configurations to filter by."
    )
    created_after: Optional[str] = Field(
        None, description="Filter sessions created after ISO8601 date-time"
    )
    created_before: Optional[str] = Field(
        None, description="Filter sessions created before ISO8601 date-time"
    )
    created_by: Optional[List[int]] = Field(
        None, description="Comma-separated list of users to filter by"
    )
    is_closed: Optional[bool] = Field(
        None, description="Limit result to active or closed sessions only"
    )
    milestone_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of milestones to filter by"
    )
    state_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of states to filter by"
    )
    tags: Optional[List[str]] = Field(
        None, description="Comma-separated list of tags to filter by"
    )
    template_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of templates to filter by"
    )


class ListSessionsApiResponse(
    PaginatedApiResponse[Session], ExpandedApiResponse[SessionExpands]
):
    """GET /api/v1/projects/{project_id}/sessions response."""


# ============================================================================
# GET /sessions/{session_id} request/response
# ============================================================================
class GetSessionApiRequest(ExpandedApiRequest):
    """GET /api/v1/sessions/{session_id} request."""

    SUPPORTED_EXPANDS = SUPPORTED_SESSION_EXPANDS
    session_id: int = Field(..., description="Session ID")


class GetSessionApiResponse(ApiResponse[Session], ExpandedApiResponse[SessionExpands]):
    """GET /api/v1/sessions/{session_id} response."""
