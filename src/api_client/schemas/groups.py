"""Groups API request/response schemas."""

from typing import ClassVar, List, Optional, Set

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


class Group(BaseModel):
    """GET /api/v1/groups result item."""

    id: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    members: list[int] = Field(default_factory=list, description="Member user IDs")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")


class GroupExpands(BaseModel):
    users: Optional[List[UserExpand]] = None


GROUP_EXPANDS = {
    ExpandsEnum.users,
}


# GET /api/v1/groups request/response (Admin API)
class ListGroupsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/groups request."""

    SUPPORTED_EXPANDS: ClassVar[Set[ExpandsEnum]] = GROUP_EXPANDS


class ListGroupsApiResponse(
    PaginatedApiResponse[Group], ExpandedApiResponse[GroupExpands]
):
    """GET /api/v1/groups response."""


# GET /api/v1/groups/{group_id} request/response (Admin API)
class GetGroupApiRequest(ExpandedApiRequest):
    """GET /api/v1/groups/{group_id} request."""

    SUPPORTED_EXPANDS: ClassVar[Set[ExpandsEnum]] = GROUP_EXPANDS
    group_id: int = Field(..., description="Group ID")


class GetGroupApiResponse(ApiResponse[Group], ExpandedApiResponse[GroupExpands]):
    """GET /api/v1/groups/{group_id} response."""
