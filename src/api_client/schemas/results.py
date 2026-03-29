"""Run results API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    IssueExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    StatusExpand,
    UserExpand,
)


class RunResultExpands(BaseModel):
    issues: Optional[List[IssueExpand]] = None
    users: Optional[List[UserExpand]] = None
    statuses: Optional[List[StatusExpand]] = None


class RunResult(BaseModel):
    """GET /api/v1/runs/{run_id}/results result item."""

    id: int = Field(..., description="Result ID")
    project_id: int = Field(..., description="Project ID")
    run_id: int = Field(..., description="Run ID")
    test_id: int = Field(..., description="Test ID")
    case_id: int = Field(..., description="Case ID")
    status_id: int = Field(..., description="Status ID")
    is_latest: bool = Field(..., description="Whether this is the latest result")
    note: Optional[str] = Field(None, description="Result note")
    elapsed: Optional[int] = Field(None, description="Elapsed duration")
    assignee_id: Optional[int] = Field(None, description="Assignee user ID")
    issues: list[int] = Field(
        default_factory=list, description="Issue IDs linked to result"
    )
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    deleted_at: Optional[str] = Field(None, description="Deletion timestamp")
    deleted_by: Optional[int] = Field(None, description="Deleter user ID")


# GET /api/v1/runs/{run_id}/results request/response
class ListRunResultsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/runs/{run_id}/results request."""

    SUPPORTED_EXPANDS = {
        ExpandsEnum.issues,
        ExpandsEnum.users,
        ExpandsEnum.statuses,
    }

    run_id: int = Field(..., description="Run ID")
    sort: Optional[Literal["run_results:created_at"]] = Field(
        None, description="Sort field for results list"
    )
    order: Optional[Literal["asc", "desc"]] = Field("desc", description="Sort order")
    created_after: Optional[str] = Field(
        None, description="Filter results created after ISO8601 date-time"
    )
    created_before: Optional[str] = Field(
        None, description="Filter results created before ISO8601 date-time"
    )
    created_by: Optional[List[int]] = Field(
        None, description="List of users to filter by"
    )
    assignee_id: Optional[List[int]] = Field(
        None,
        description="Comma-separated list of assignees to filter by. Use assignee_id=0 for unassigned test case results",
    )
    # The system supports up to 25 total statuses. Use the ID keys & name values as defined in your instance,
    # typically: 1 for Untested, 2 for Passed, 3 for Failed, 4 for Retest, 5 for Blocked, 6 for Skipped.
    # Unless modified by your administrator, custom statuses will have IDs 7-25.
    status_id: Optional[List[int]] = Field(
        None, description="List of statuses to filter by"
    )
    get_latest_result: Optional[bool] = Field(
        None,
        description="Indicates whether to fetch only the latest result (true, 1) or all results (false, 0)",
    )


class ListRunResultsApiResponse(
    PaginatedApiResponse[RunResult], ExpandedApiResponse[RunResultExpands]
):
    """GET /api/v1/runs/{run_id}/results response."""
