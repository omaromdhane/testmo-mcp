"""Role API request/response schemas."""

from typing import List, Optional

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


class Role(BaseModel):
    """GET /api/v1/roles result item."""

    id: int = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    permissions: int = Field(..., description="Bitmask permissions")
    is_default: bool = Field(..., description="Whether this role is default")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Creator user ID")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updater user ID")


# expands schema
class RoleExpands(BaseModel):
    users: Optional[List[UserExpand]] = None


SUPPORTED_ROLE_EXPANDS = {ExpandsEnum.users}


# GET /api/v1/roles request/response (Admin API)
class ListRolesApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/roles request."""

    SUPPORTED_EXPANDS = SUPPORTED_ROLE_EXPANDS


class ListRolesApiResponse(
    PaginatedApiResponse[Role], ExpandedApiResponse[RoleExpands]
):
    """GET /api/v1/roles response."""


# GET /api/v1/roles/{role_id} request/response (Admin API)
class GetRoleApiRequest(ExpandedApiRequest):
    """GET /api/v1/roles/{role_id} request."""

    SUPPORTED_EXPANDS = SUPPORTED_ROLE_EXPANDS
    role_id: int = Field(..., description="Role ID")


class GetRoleApiResponse(ApiResponse[Role], ExpandedApiResponse[RoleExpands]):
    """GET /api/v1/roles/{role_id} response."""
