"""Common API request/response and expand schemas."""

from enum import Enum
from typing import Any, ClassVar, Generic, List, Optional, Set, TypeVar

from pydantic import BaseModel, Field, field_validator, model_serializer

T = TypeVar("T")
E = TypeVar("E", bound=BaseModel)

# ============================================================================
# Base request/response
# ============================================================================


class ApiRequest(BaseModel):
    """Base API request schema."""


class ApiResponse(BaseModel, Generic[T]):
    """Base API response schema."""

    result: T = Field(..., description="API response data")


# ============================================================================
# Pagination request/response
# ============================================================================


class PaginatedApiRequest(BaseModel):
    """Pagination request parameters."""

    page: Optional[int] = Field(1, ge=1, description="Page number to retrieve")
    per_page: Optional[int] = Field(
        100, ge=15, le=100, description="Items per page (15, 25, 50, or 100)"
    )

    def validate_per_page(self) -> None:
        """Validate per_page is one of the supported values."""
        supported = [15, 25, 50, 100]
        if self.per_page not in supported:
            # Round to nearest supported value
            self.per_page = min(supported, key=lambda x: abs(x - self.per_page))


class PaginatedApiResponse(ApiResponse[List[T]], Generic[T]):
    """Paginated response from Testmo API."""

    page: Optional[int] = Field(
        None, description="Current page number (null for empty result)"
    )
    prev_page: Optional[int] = Field(
        None, description="Previous page number (null if no previous page)"
    )
    next_page: Optional[int] = Field(
        None, description="Next page number (null if no next page)"
    )
    last_page: Optional[int] = Field(
        None, description="Last page number (null for empty result)"
    )
    per_page: int = Field(100, description="Maximum items per page")
    total: int = Field(0, description="Total number of items across all pages")

    def has_next_page(self) -> bool:
        """Check if there is a next page."""
        return self.next_page is not None

    def has_prev_page(self) -> bool:
        """Check if there is a previous page."""
        return self.prev_page is not None

    def is_last_page(self) -> bool:
        """Check if this is the last page."""
        return self.next_page is None or self.page == self.last_page

    def is_first_page(self) -> bool:
        """Check if this is the first page."""
        return self.prev_page is None or self.page == 1


# ============================================================================
# Expand request/response
# ============================================================================
class ExpandsEnum(str, Enum):
    automation_sources = "automation_sources"
    automation_links = "automation_links"
    comments = "comments"
    configs = "configs"
    field_values = "field_values"
    folders = "folders"
    groups = "groups"
    history = "history"
    issues = "issues"
    milestone_stats = "milestone_stats"
    milestone_types = "milestone_types"
    milestones = "milestones"
    roles = "roles"
    states = "states"
    statuses = "statuses"
    tags = "tags"
    templates = "templates"
    users = "users"


class ExpandedApiRequest(BaseModel):
    """Standard expands request parameter."""

    expands: Optional[List[ExpandsEnum]] = Field(
        None, description="List of expands to apply to the response"
    )
    SUPPORTED_EXPANDS: ClassVar[Set[ExpandsEnum]] = set()

    @field_validator("expands")
    @classmethod
    def validate_expands(
        cls, values: Optional[List[ExpandsEnum]]
    ) -> Optional[List[ExpandsEnum]]:
        if values is None:
            return None
        if not cls.SUPPORTED_EXPANDS:
            raise ValueError("SUPPORTED_EXPANDS is not set for this API")
        invalid = [value for value in values if value not in cls.SUPPORTED_EXPANDS]
        if invalid:
            raise ValueError(
                f"Unsupported expands for this API: {', '.join(v.value for v in invalid)}"
            )
        return values

    def to_query_string(self) -> str:
        return ",".join(value.value for value in self.expands)


class ExpandedApiResponse(BaseModel, Generic[E]):
    """Response envelope containing typed expands payload."""

    expands: Optional[E] = Field(None, description="Expanded related resources")

    @field_validator("expands", mode="before")
    @classmethod
    def validate_expands(cls, v: Any) -> Any:
        if isinstance(v, list) and len(v) == 0:
            return None
        return v

    @model_serializer(mode="wrap")
    def serialize_model(self, serializer: Any) -> dict[str, Any]:
        data = serializer(self)

        if self.expands is None:
            data.pop("expands", None)
        else:
            serialized_expands = self.expands.model_dump()
            new_expands = {k: v for k, v in serialized_expands.items() if v is not None}
            if new_expands:
                data["expands"] = new_expands
            else:
                data.pop("expands", None)

        return data


# ============================================================================
# Expand object schemas (from Testmo OpenAPI)
# ============================================================================


class UserExpand(BaseModel):
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")


class ConfigExpand(BaseModel):
    id: int = Field(..., description="Config ID")
    name: str = Field(..., description="Config name")


class FieldValueExpand(BaseModel):
    id: int = Field(..., description="Field value ID")
    name: str = Field(..., description="Field value name")
    icon: Optional[str] = Field(None, description="Field value icon")
    color: Optional[str] = Field(None, description="Field value color")


class GroupExpand(BaseModel):
    id: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")


class IssueExpand(BaseModel):
    id: int = Field(..., description="Issue ID")
    type: int = Field(..., description="Issue type")
    display_id: str = Field(..., description="Issue display ID")
    external_project_id: Optional[int] = Field(None, description="External project ID")
    external_project_key: Optional[str] = Field(
        None, description="External project key"
    )


class MilestoneExpand(BaseModel):
    id: int = Field(..., description="Milestone ID")
    name: str = Field(..., description="Milestone name")


class MilestoneStatsExpand(BaseModel):
    id: int = Field(..., description="Milestone stats ID")
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


class MilestoneTypeExpand(BaseModel):
    id: int = Field(..., description="Milestone type ID")
    name: str = Field(..., description="Milestone type name")
    is_default: bool = Field(
        ..., description="Whether this is the default milestone type"
    )


class RoleExpand(BaseModel):
    id: int = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")


class StateExpand(BaseModel):
    id: int = Field(..., description="State ID")
    name: str = Field(..., description="State name")
    is_default: bool = Field(..., description="Whether this is the default state")


class StatusExpand(BaseModel):
    id: int = Field(..., description="Status ID")
    name: str = Field(..., description="Status name")
    system_name: str = Field(..., description="Status system name")
    color: str = Field(..., description="Status color")
    is_final: bool = Field(..., description="Whether this is a final status")
    is_untested: bool = Field(..., description="Whether this is an untested status")
    is_passed: bool = Field(..., description="Whether this is a passed status")
    is_failed: bool = Field(..., description="Whether this is a failed status")
    aliases: List[str] = Field(..., description="Status aliases")


class TemplateExpand(BaseModel):
    id: int = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    is_default: bool = Field(..., description="Whether this is the default template")


class FolderExpand(BaseModel):
    id: int = Field(..., description="Folder ID")
    name: str = Field(..., description="Folder name")


class AutomationSourceExpand(BaseModel):
    id: int = Field(..., description="Automation source ID")
    name: str = Field(..., description="Automation source name")


class AutomationLinkExpand(BaseModel):
    automation_source_id: int = Field(..., description="Automation source ID")
    automation_case_id: int = Field(..., description="Automation case ID")
    name: str = Field(..., description="Automation link name")


class TagExpand(BaseModel):
    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")


class RepositoryCaseChange(BaseModel):
    id: int = Field(..., description="Repository case change ID")
    type: int = Field(..., description="Repository case change type")
    field: str = Field(..., description="Repository case change field")


class HistoryExpand(BaseModel):
    id: int = Field(..., description="History ID")
    created_at: str = Field(..., description="History created at")
    changes: List[RepositoryCaseChange] = Field(..., description="History changes")


class CommentExpand(BaseModel):
    id: int = Field(..., description="Comment ID")
    created_at: str = Field(..., description="Comment created at")
    created_by: int = Field(..., description="Comment created by")
