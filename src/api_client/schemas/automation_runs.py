"""Automation Run API request/response schemas."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiResponse,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    PaginatedApiRequest,
    PaginatedApiResponse,
)


# ============================================================================
# Automation Run Expands
# ============================================================================
class AutomationRunExpands(BaseModel):
    """Expands for automation run responses."""

    automation_sources: Optional[List[Dict[str, Any]]] = Field(
        None, description="Automation sources expand"
    )
    configs: Optional[List[Dict[str, Any]]] = Field(None, description="Configs expand")
    milestones: Optional[List[Dict[str, Any]]] = Field(
        None, description="Milestones expand"
    )
    statuses: Optional[List[Dict[str, Any]]] = Field(
        None, description="Statuses expand"
    )
    users: Optional[List[Dict[str, Any]]] = Field(None, description="Users expand")


SUPPORTED_AUTOMATION_RUN_EXPANDS = {
    ExpandsEnum.automation_sources,
    ExpandsEnum.configs,
    ExpandsEnum.milestones,
    ExpandsEnum.statuses,
    ExpandsEnum.users,
}


# ============================================================================
# Artifact, Field, Link schemas (reusable)
# ============================================================================
class Artifact(BaseModel):
    """Test artifact schema."""

    name: str = Field(..., description="Name or file name of the test artifact")
    note: Optional[str] = Field(
        None, description="Short note or summary (max 80 chars)"
    )
    url: str = Field(
        ..., description="Link to external resource to download the artifact"
    )
    mime_type: Optional[str] = Field(
        None, description="MIME type (e.g., image/png, text/plain)"
    )
    size: Optional[int] = Field(None, description="File size in bytes")


class AutomationField(BaseModel):
    """Custom field schema for automation runs."""

    type: Literal[1, 2, 3, 4, 5] = Field(
        ...,
        description="Field type: 1=string, 2=plain text, 3=HTML, 4=terminal/console, 5=URL",
    )
    name: str = Field(..., description="Name of the field")
    value: str = Field(..., description="Value of the field")
    meta: Optional[Dict[str, str]] = Field(
        None, description="Meta fields for extra information"
    )


class AutomationLink(BaseModel):
    """Link schema for automation runs."""

    name: str = Field(..., description="Name or file name of the link")
    note: Optional[str] = Field(
        None, description="Short note or summary (max 80 chars)"
    )
    url: str = Field(..., description="Link to external resource or website")


class AutomationRunThread(BaseModel):
    """Automation run thread schema."""

    id: int = Field(..., description="Automation run thread ID")
    index: int = Field(..., description="Thread index")
    name: str = Field(..., description="Thread name")
    status: Literal[2, 3, 4] = Field(
        ..., description="Status: 2=success, 3=failure, 4=running"
    )
    elapsed: Optional[int] = Field(None, description="Elapsed duration")
    is_completed: bool = Field(..., description="Whether thread is completed")
    artifacts: List[Artifact] = Field(..., description="Artifacts")
    fields: List[AutomationField] = Field(..., description="Fields")
    untested_count: int = Field(..., description="Count of untested items")
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
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    completed_by: Optional[int] = Field(None, description="Completer user ID")


# ============================================================================
# Automation Run
# ============================================================================
class AutomationRun(BaseModel):
    """Automation run schema."""

    id: int = Field(..., description="Automation run ID")
    project_id: int = Field(..., description="Project ID")
    source_id: int = Field(..., description="Source ID")
    name: str = Field(..., description="Automation run name")
    status: Literal[2, 3, 4] = Field(
        ..., description="Status: 2=success, 3=failure, 4=running"
    )
    config_id: Optional[int] = Field(
        None, description="Configuration ID"
    )  # Conflict between openapi and testmo documentation
    milestone_id: Optional[int] = Field(
        None, description="Milestone ID"
    )  # Conflict between openapi and testmo documentation
    elapsed: Optional[int] = Field(None, description="Elapsed duration")
    is_completed: bool = Field(..., description="Whether run is completed")
    artifacts: List[Artifact] = Field(..., description="Artifacts")
    fields: List[AutomationField] = Field(..., description="Fields")
    links: List[AutomationLink] = Field(..., description="Links")
    tags: List[str] = Field(..., description="Tags")
    threads: List[AutomationRunThread] = Field(..., description="Threads")
    untested_count: int = Field(..., description="Count of untested items")
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
    thread_count: int = Field(..., description="Thread count")
    thread_active_count: int = Field(..., description="Active thread count")
    thread_completed_count: int = Field(..., description="Completed thread count")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Update timestamp")
    updated_by: Optional[int] = Field(None, description="Updater user ID")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    completed_by: Optional[int] = Field(None, description="Completer user ID")


# ============================================================================
# List Automation Runs
# ============================================================================
class ListAutomationRunsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/projects/{project_id}/automation/runs request."""

    SUPPORTED_EXPANDS = SUPPORTED_AUTOMATION_RUN_EXPANDS
    project_id: int = Field(..., description="Project ID")
    sort: Optional[Literal["automation_runs:created_at"]] = Field(
        None, description="Sort field"
    )
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
    config_id: Optional[List[int]] = Field(
        None, description="Comma-separated config IDs"
    )
    created_after: Optional[str] = Field(
        None, description="Created after (ISO8601, UTC)"
    )
    created_before: Optional[str] = Field(
        None, description="Created before (ISO8601, UTC)"
    )
    created_by: Optional[List[int]] = Field(
        None, description="Comma-separated user IDs"
    )
    milestone_id: Optional[List[int]] = Field(
        None, description="Comma-separated milestone IDs"
    )
    source_id: Optional[List[int]] = Field(
        None, description="Comma-separated source IDs"
    )
    status: Optional[List[int]] = Field(
        None, description="Comma-separated statuses (2=success, 3=failure, 4=running)"
    )
    tags: Optional[List[str]] = Field(None, description="Comma-separated tags")


class ListAutomationRunsApiResponse(
    PaginatedApiResponse[AutomationRun], ExpandedApiResponse[AutomationRunExpands]
):
    """GET /api/v1/projects/{project_id}/automation/runs response."""


# ============================================================================
# Get Automation Run
# ============================================================================
class GetAutomationRunApiRequest(ExpandedApiRequest):
    """GET /api/v1/automation/runs/{automation_run_id} request."""

    SUPPORTED_EXPANDS = SUPPORTED_AUTOMATION_RUN_EXPANDS
    automation_run_id: int = Field(..., description="Automation run ID")


class GetAutomationRunApiResponse(
    ApiResponse[AutomationRun], ExpandedApiResponse[AutomationRunExpands]
):
    """GET /api/v1/automation/runs/{automation_run_id} response."""
