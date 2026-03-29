"""User API request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ApiRequest,
    ApiResponse,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    GroupExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    RoleExpand,
    UserExpand,
)


class CurrentUser(BaseModel):
    """GET /api/v1/user response."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    timezone: Optional[str] = Field(None, description="Preferred timezone")
    date_format: Optional[str] = Field(None, description="Preferred date format")
    time_format: Optional[str] = Field(None, description="Preferred time format")


class User(BaseModel):
    """GET /api/v1/users result item."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    type: int = Field(..., description="User type")
    timezone: Optional[str] = Field(None, description="Preferred timezone")
    date_format: Optional[str] = Field(None, description="Preferred date format")
    time_format: Optional[str] = Field(None, description="Preferred time format")
    notifications: int = Field(..., description="Notifications mode ")
    tfa_enabled: bool = Field(..., description="Two-factor authentication enabled")
    is_active: bool = Field(..., description="Whether the user is active")
    is_forgotten: bool = Field(
        ..., description="Whether the user is forgotten/anonymized"
    )
    is_api: bool = Field(..., description="Whether this is an API user")
    role_id: int = Field(..., description="Assigned role ID")
    groups: Optional[list[int]] = Field(None, description="Group IDs")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")


class ProjectUser(BaseModel):
    """GET /api/v1/projects/{project_id}/users result item."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")


class UserExpands(BaseModel):
    groups: Optional[list[GroupExpand]] = None
    roles: Optional[list[RoleExpand]] = None
    users: Optional[list[UserExpand]] = None


suppoted_user_expands = {
    ExpandsEnum.groups,
    ExpandsEnum.roles,
    ExpandsEnum.users,
}


# GET /api/v1/projects/{project_id}/users request/response (User API)
class ListProjectUsersApiRequest(PaginatedApiRequest):
    """GET /api/v1/projects/{project_id}/users request."""

    project_id: int = Field(..., description="Project ID")


class ListProjectUsersApiResponse(PaginatedApiResponse[ProjectUser]):
    """GET /api/v1/projects/{project_id}/users response."""


# GET /api/v1/user request/response (User API)
class GetCurrentUserApiRequest(ApiRequest):
    """GET /api/v1/user request."""


class GetCurrentUserApiResponse(ApiResponse[CurrentUser]):
    """GET /api/v1/user response."""


# GET /api/v1/users request/response (Admin API)
class ListUsersApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/users request."""

    SUPPORTED_EXPANDS = suppoted_user_expands


class ListUsersApiResponse(
    PaginatedApiResponse[User], ExpandedApiResponse[UserExpands]
):
    """GET /api/v1/users response."""


# GET /api/v1/users/{user_id} request (Admin API)
class GetUserApiRequest(ExpandedApiRequest):
    """GET /api/v1/users/{user_id} request."""

    SUPPORTED_EXPANDS = suppoted_user_expands
    user_id: int = Field(..., description="User ID")


class GetUserApiResponse(ApiResponse[User], ExpandedApiResponse[UserExpands]):
    """GET /api/v1/users/{user_id} response."""
