"""Attachments API request/response schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from api_client.schemas.common import (
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    PaginatedApiRequest,
    PaginatedApiResponse,
    UserExpand,
)


# ============================================================================
# Attachment Expands
# ============================================================================
class AttachmentExpands(BaseModel):
    users: Optional[List[UserExpand]] = None


# ============================================================================
# Objects schemas
# ============================================================================
class Attachment(BaseModel):
    """Attachment model."""

    id: int = Field(..., description="Attachment ID")
    name: str = Field(..., description="Attachment file name")
    note: Optional[str] = Field(
        None, description="Attachment note"
    )  # conflict: nullable in website docs, required in openapi docs
    mime_type: str = Field(..., description="MIME type of the attachment")
    size: int = Field(..., description="File size in bytes")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Created by user ID")
    path: str = Field(..., description="Download path URL")
    path_thumbnail: Optional[str] = Field(None, description="Thumbnail path URL")
    path_preview: Optional[str] = Field(None, description="Preview path URL")


# ============================================================================
# GET /cases/{case_id}/attachments request/response
# ============================================================================
class ListAttachmentsApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """GET /api/v1/cases/{case_id}/attachments request."""

    SUPPORTED_EXPANDS = {ExpandsEnum.users}
    case_id: int = Field(..., description="Case ID")
    created_by: Optional[List[int]] = Field(
        None, description="List of user IDs to filter by"
    )
    order: Optional[Literal["asc", "desc"]] = Field(None, description="Sort order")


class ListAttachmentsApiResponse(
    PaginatedApiResponse[Attachment], ExpandedApiResponse[AttachmentExpands]
):
    """GET /api/v1/cases/{case_id}/attachments response."""
