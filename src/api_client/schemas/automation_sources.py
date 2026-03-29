"""Automation sources API request/response schemas."""

from typing import Literal, Optional

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


class AutomationSource(BaseModel):
    """GET /api/v1/projects/{project_id}/automation/sources result item."""

    id: int = Field(..., description="Automation source ID")
    project_id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Automation source name")
    status: Literal[1, 2, 3] = Field(..., description="Automation source status")
    is_retired: bool = Field(..., description="Whether source is retired")
    run_count: int = Field(..., description="Run count")
    test_count_average: Optional[int] = Field(None, description="Average test count")
    elapsed_average: Optional[int] = Field(None, description="Average elapsed time")
    ran_at: Optional[str] = Field(None, description="Most recent run timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")
    retired_at: Optional[str] = Field(None, description="Retirement timestamp")
    retired_by: Optional[int] = Field(None, description="Retired by user ID")


class AutomationSourceExpands(BaseModel):
    """Expands payload for automation sources endpoints."""

    users: Optional[list[UserExpand]] = None


# GET /api/v1/projects/{project_id}/automation/sources request/response
class ListAutomationSourcesApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/projects/{project_id}/automation/sources request."""

    SUPPORTED_EXPANDS = {ExpandsEnum.users}

    project_id: int = Field(..., description="Project ID")
    sort: Optional[
        Literal[
            "automation_sources:created_at",
            "automation_sources:ran_at",
            "automation_sources:retired_at",
        ]
    ] = Field(None, description="Sort field for automation sources list")
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")
    is_retired: Optional[bool] = Field(
        None, description="Filter active or retired automation sources"
    )


class ListAutomationSourcesApiResponse(
    PaginatedApiResponse[AutomationSource],
    ExpandedApiResponse[AutomationSourceExpands],
):
    """GET /api/v1/projects/{project_id}/automation/sources response."""


# GET /api/v1/automation/sources/{automation_source_id} request/response
class GetAutomationSourceApiRequest(ExpandedApiRequest):
    """GET /api/v1/automation/sources/{automation_source_id} request."""

    SUPPORTED_EXPANDS = {ExpandsEnum.users}
    automation_source_id: int = Field(..., description="Automation source ID")


class GetAutomationSourceApiResponse(
    ApiResponse[AutomationSource], ExpandedApiResponse[AutomationSourceExpands]
):
    """GET /api/v1/automation/sources/{automation_source_id} response."""
