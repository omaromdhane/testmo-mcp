"""Cases schemas for GET /projects/{project_id}/cases."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_serializer, model_validator

from api_client.schemas.common import (
    AutomationLinkExpand,
    CommentExpand,
    ExpandedApiRequest,
    ExpandedApiResponse,
    ExpandsEnum,
    FolderExpand,
    HistoryExpand,
    PaginatedApiRequest,
    PaginatedApiResponse,
    TagExpand,
    TemplateExpand,
    UserExpand,
)


class Case(BaseModel):
    """Test case model from repository cases endpoint."""

    id: int = Field(..., description="Case ID")
    estimate: Optional[int] = Field(None, description="Estimated duration")
    folder_id: int = Field(..., description="Folder ID")
    forecast: Optional[int] = Field(None, description="Forecast duration")
    has_automation: bool = Field(..., description="Has automation links")
    has_automation_status: bool = Field(..., description="Has automation status")
    key: int = Field(..., description="Case key")
    name: str = Field(..., description="Case name")
    project_id: int = Field(..., description="Project ID")
    repo_id: int = Field(..., description="Repository ID")
    state_id: int = Field(..., description="State ID")
    status_id: Optional[int] = Field(None, description="Status ID")
    status_at: Optional[str] = Field(None, description="Status timestamp")
    template_id: int = Field(..., description="Template ID")
    created_at: str = Field(..., description="Creation timestamp")
    created_by: int = Field(..., description="Created by user IDs")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    updated_by: Optional[int] = Field(None, description="Last updated by user ID")
    automation_links: Optional[list[int]] = Field(None, description="Automation links")
    tags: Optional[list[int]] = Field(None, description="Tags")
    history: Optional[list[int]] = Field(None, description="History")
    comments: Optional[list[int]] = Field(None, description="Comments")
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic Testmo custom fields mapped from keys prefixed with custom_",
    )

    @model_validator(mode="before")
    @classmethod
    def extract_custom_fields(cls, data):
        if not isinstance(data, dict):
            return data

        custom = {}
        cleaned = {}

        for k, v in data.items():
            if k.startswith("custom_"):
                custom[k] = v
            else:
                cleaned[k] = v

        cleaned["custom_fields"] = custom
        return cleaned

    @model_serializer(mode="wrap")
    def serialize_model(self, serializer: Any) -> dict[str, Any]:
        data = serializer(self)
        # Remove empty expands
        if data.get("automation_links") is None:
            data.pop("automation_links", None)
        if data.get("tags") is None:
            data.pop("tags", None)
        if data.get("history") is None:
            data.pop("history", None)
        if data.get("comments") is None:
            data.pop("comments", None)
        return data


class RepositoryCaseResultExpands(BaseModel):
    templates: Optional[List[TemplateExpand]] = None
    folders: Optional[List[FolderExpand]] = None
    users: Optional[List[UserExpand]] = None
    automation_links: Optional[List[AutomationLinkExpand]] = None
    tags: Optional[List[TagExpand]] = None
    history: Optional[List[HistoryExpand]] = None
    comments: Optional[List[CommentExpand]] = None


# GET /api/v1/projects/{project_id}/cases request/response
class ListCasesApiRequest(PaginatedApiRequest, ExpandedApiRequest):
    """Request parameters for listing project cases."""

    SUPPORTED_EXPANDS = {
        ExpandsEnum.automation_links,
        ExpandsEnum.comments,
        ExpandsEnum.folders,
        ExpandsEnum.history,
        ExpandsEnum.users,
        ExpandsEnum.tags,
        ExpandsEnum.templates,
    }

    project_id: int = Field(..., description="Project ID")
    order: Optional[Literal["asc", "desc"]] = Field(
        None, description="Sort order (ascending or descending)"
    )
    sort: Optional[
        Literal[
            "repository_cases:created_at",
            "repository_cases:created_by",
            "repository_cases:display_order",
            "repository_cases:estimate",
            "repository_cases:folder_id",
            "repository_cases:forecast",
            "repository_cases:has_automation",
            "repository_cases:id",
            "repository_cases:name",
            "repository_cases:state_id",
            "repository_cases:status_at",
            "repository_cases:status_id",
            "repository_cases:template_id",
            "repository_cases:updated_at",
            "repository_cases:updated_by",
        ]
    ] = Field(None, description="Sort field for cases list")
    updated_by: Optional[List[int]] = Field(
        None, description="Comma-separated list of user IDs"
    )
    folder_id: Optional[List[int]] = Field(None, description="List of folder IDs")
    template_id: Optional[List[int]] = Field(None, description="List of template IDs")
    created_after: Optional[str] = Field(
        None, description="Limit to cases created after (ISO8601 UTC)"
    )
    created_before: Optional[str] = Field(
        None, description="Limit to cases created before (ISO8601 UTC)"
    )
    state_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of state IDs"
    )
    status_id: Optional[List[int]] = Field(
        None, description="Comma-separated list of status IDs"
    )
    has_automation: Optional[bool] = Field(
        None, description="Filter cases with/without automation links"
    )
    has_automation_status: Optional[bool] = Field(
        None, description="Filter cases with/without automation status"
    )


class ListCasesApiResponse(
    PaginatedApiResponse[Case], ExpandedApiResponse[RepositoryCaseResultExpands]
):
    """Paginated cases list response."""
