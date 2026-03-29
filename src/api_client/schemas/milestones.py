"""Milestones API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiResponse,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    IssueExpand,
    MilestoneExpand,
    MilestoneStatsExpand,
    MilestoneTypeExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    StatusExpand,
    UserExpand,
)


class MilestoneLink(BaseModel):
    name: str = Field(..., description="Milestone link name")
    note: Optional[str] = Field(None, description="Milestone link note")
    url: str = Field(..., description="Milestone link URL")


class Milestone(BaseModel):
    """GET /api/v1/projects/{project_id}/milestones result item."""

    id: int = Field(..., description="Milestone ID")
    project_id: int = Field(..., description="Project ID")
    root_id: Optional[int] = Field(None, description="Root milestone ID")
    parent_id: Optional[int] = Field(None, description="Parent milestone ID")
    type_id: int = Field(..., description="Milestone type ID")
    name: str = Field(..., description="Milestone name")
    note: Optional[str] = Field(None, description="Milestone note")
    is_started: bool = Field(..., description="Whether milestone has started")
    is_completed: bool = Field(..., description="Whether milestone is completed")
    start_date: Optional[str] = Field(None, description="Milestone start date")
    due_date: Optional[str] = Field(None, description="Milestone due date")
    automation_tags: list[str] = Field(
        default_factory=list, description="Automation tags"
    )
    issues: list[int] = Field(default_factory=list, description="Issue IDs")
    links: list[MilestoneLink] = Field(
        default_factory=list, description="Milestone links"
    )
    started_at: Optional[str] = Field(None, description="Started timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    completed_at: Optional[str] = Field(None, description="Completed timestamp")


class MilestoneExpands(BaseModel):
    issues: Optional[List[IssueExpand]] = None
    milestone_stats: Optional[List[MilestoneStatsExpand]] = None
    milestone_types: Optional[List[MilestoneTypeExpand]] = None
    milestones: Optional[List[MilestoneExpand]] = None
    statuses: Optional[List[StatusExpand]] = None
    users: Optional[List[UserExpand]] = None


MILESTONE_EXPANDS = {
    ExpandsEnum.issues,
    ExpandsEnum.milestone_stats,
    ExpandsEnum.milestone_types,
    ExpandsEnum.milestones,
    ExpandsEnum.statuses,
    ExpandsEnum.users,
}


# GET /api/v1/projects/{project_id}/milestones request/response
class ListMilestonesApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/projects/{project_id}/milestones request."""

    SUPPORTED_EXPANDS = MILESTONE_EXPANDS
    project_id: int = Field(..., description="Project ID")
    sort: Optional[Literal["milestones:created_at", "milestones:completed_at"]] = Field(
        None, description="Sort field for milestones list"
    )
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
    automation_tags: Optional[List[str]] = Field(
        None, description="List of automation tags"
    )
    completed_after: Optional[str] = Field(
        None, description="Filter milestones completed after ISO8601 date-time"
    )
    completed_before: Optional[str] = Field(
        None, description="Filter milestones completed before ISO8601 date-time"
    )
    created_after: Optional[str] = Field(
        None, description="Filter milestones created after ISO8601 date-time"
    )
    created_before: Optional[str] = Field(
        None, description="Filter milestones created before ISO8601 date-time"
    )
    created_by: Optional[List[int]] = Field(
        None, description="List of creator user IDs"
    )
    is_completed: Optional[bool] = Field(
        None, description="Filter active/completed milestones"
    )
    parent_id: Optional[List[int]] = Field(
        None, description="List of parent milestone IDs"
    )
    root_id: Optional[List[int]] = Field(None, description="List of root milestone IDs")
    type_id: Optional[List[int]] = Field(None, description="List of milestone type IDs")


class ListMilestonesApiResponse(
    PaginatedApiResponse[Milestone], ExpandedApiResponse[MilestoneExpands]
):
    """GET /api/v1/projects/{project_id}/milestones response."""


# GET /api/v1/milestones/{milestone_id} request/response
class GetMilestoneApiRequest(ExpandedApiRequest):
    """GET /api/v1/milestones/{milestone_id} request."""

    SUPPORTED_EXPANDS = MILESTONE_EXPANDS
    milestone_id: int = Field(..., description="Milestone ID")


class GetMilestoneApiResponse(
    ApiResponse[Milestone], ExpandedApiResponse[MilestoneExpands]
):
    """GET /api/v1/milestones/{milestone_id} response."""
