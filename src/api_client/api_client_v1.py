import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from api_client.errors import RequestSendError, ResponseReadError, ResponseWithError
from api_client.schemas import (
    ApiClientResponse,
    GetAutomationRunApiRequest,
    GetAutomationRunApiResponse,
    GetAutomationSourceApiRequest,
    GetAutomationSourceApiResponse,
    GetCurrentUserApiResponse,
    GetGroupApiRequest,
    GetGroupApiResponse,
    GetMilestoneApiRequest,
    GetMilestoneApiResponse,
    GetProjectApiResponse,
    GetRoleApiRequest,
    GetRoleApiResponse,
    GetRunApiRequest,
    GetRunApiResponse,
    GetSessionApiRequest,
    GetSessionApiResponse,
    GetUserApiRequest,
    GetUserApiResponse,
    ListAttachmentsApiRequest,
    ListAttachmentsApiResponse,
    ListAutomationRunsApiRequest,
    ListAutomationRunsApiResponse,
    ListAutomationSourcesApiRequest,
    ListAutomationSourcesApiResponse,
    ListCasesApiRequest,
    ListCasesApiResponse,
    ListFoldersApiRequest,
    ListFoldersApiResponse,
    ListGroupsApiRequest,
    ListGroupsApiResponse,
    ListIssueConnectionsApiRequest,
    ListIssueConnectionsApiResponse,
    ListMilestonesApiRequest,
    ListMilestonesApiResponse,
    ListProjectsApiRequest,
    ListProjectsApiResponse,
    ListProjectUsersApiRequest,
    ListProjectUsersApiResponse,
    ListRolesApiRequest,
    ListRolesApiResponse,
    ListRunResultsApiRequest,
    ListRunResultsApiResponse,
    ListRunsApiRequest,
    ListRunsApiResponse,
    ListSessionsApiRequest,
    ListSessionsApiResponse,
    ListUsersApiRequest,
    ListUsersApiResponse,
)

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=BaseModel)

logger = logging.getLogger("testmo_mcp.api_client_v1")


class TestmoApiClientV1:
    """
    Low-level Testmo API client that returns raw status + payload.

    Note: This client manages an httpx.AsyncClient. For proper resource cleanup,
    call aclose() when done or use as an async context manager.
    """

    def __init__(self, testmo_url: str, testmo_api_key: str):
        self.testmo_url = testmo_url
        self.testmo_api_key = testmo_api_key
        self.auth_http_client = httpx.AsyncClient(
            base_url=self.testmo_url,
            headers={
                "Authorization": f"Bearer {self.testmo_api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def _request(
        self,
        method: str,
        path: str,
        query_params: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        expected_status_code: int = 200,
    ) -> ApiClientResponse[Any]:
        """
        Send an HTTP request and return raw response payload.

        Raises:
            RequestSendError: if request transport fails.
            ResponseReadError: if response payload cannot be decoded.
        """
        try:
            logger.info(
                f"Request: method={method} path={path} query_params={query_params} json_payload={json_payload}"
            )
            response = await self.auth_http_client.request(
                method=method,
                url=path,
                params=query_params,
                json=json_payload,
            )
            logger.info(
                f"Response: status_code={response.status_code} text={response.text}"
            )
        except httpx.RequestError as exc:
            raise RequestSendError(str(exc), getattr(exc, "request", None)) from exc

        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise ResponseReadError(
                f"Unable to decode JSON response for {method} {path}",
                response.request,
                response,
            ) from exc

        if response.status_code != expected_status_code:
            raise ResponseWithError(
                f"Expected status code {expected_status_code} but got {response.status_code}",
                response.request,
                response,
            )

        return ApiClientResponse(status_code=response.status_code, data=payload)

    async def _request_typed(
        self,
        method: str,
        path: str,
        model_type: type[ModelT],
        query_params: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        expected_status_code: int = 200,
    ) -> ApiClientResponse[ModelT]:
        """
        Send request and parse successful responses json payload into a typed model.

        Raises:
            RequestSendError: if request transport fails.
            ResponseReadError: if typed model validation fails.
            ResponseValidationError: if the response payload does not match the expected schema.
            ErrorResponse: if the response is not a 200 OK.
            ResponseValidationError: if the response payload does not match the expected schema.
        """
        raw_response = await self._request(
            method=method,
            path=path,
            query_params=query_params,
            json_payload=json_payload,
            expected_status_code=expected_status_code,
        )

        try:
            typed_payload = model_type.model_validate(raw_response.data)
        except ValidationError as exc:
            raise ResponseReadError(
                f"Response json payload did not match expected schema for {method} {path}"
            ) from exc

        return ApiClientResponse(
            status_code=raw_response.status_code, data=typed_payload
        )

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> ApiClientResponse:
        return await self._request("GET", path, query_params=params)

    async def _post(
        self, path: str, json: dict[str, Any] | None = None
    ) -> ApiClientResponse:
        return await self._request("POST", path, json_payload=json)

    def _flatten_query_params(
        self, params: dict[str, str | list[str]]
    ) -> dict[str, str]:
        """Flatten query params into a single level of key-value pairs. If the value is a list, join the values with a comma. if the value is a string, use the value as is. Empty lists are excluded."""
        from enum import Enum

        flattened_params = {}
        for key, value in params.items():
            if isinstance(value, list):
                if len(value) > 0:  # Only include non-empty lists
                    # Extract .value from Enum objects, otherwise convert to string
                    flattened_params[key] = ",".join(
                        v.value if isinstance(v, Enum) else str(v) for v in value
                    )
            else:
                flattened_params[key] = value
        return flattened_params

    def client(self) -> httpx.AsyncClient | None:
        return self.auth_http_client

    # ============================================================================
    # Projects
    # ============================================================================
    async def list_projects(
        self,
        params: ListProjectsApiRequest,
    ) -> ApiClientResponse[ListProjectsApiResponse]:
        params = params.model_dump(exclude_none=True, mode="python")
        return await self._request_typed(
            method="GET",
            path="/api/v1/projects",
            model_type=ListProjectsApiResponse,
            query_params=self._flatten_query_params(params),
        )

    async def get_project(
        self, project_id: int
    ) -> ApiClientResponse[GetProjectApiResponse]:
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}",
            model_type=GetProjectApiResponse,
        )

    # ============================================================================
    # Cases
    # ============================================================================
    async def list_cases(
        self, params: ListCasesApiRequest
    ) -> ApiClientResponse[ListCasesApiResponse]:
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="json"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/cases",
            model_type=ListCasesApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Automation Runs (these are meant for automated tests to submit run results to Testmo, apart from read operations)
    # ============================================================================
    async def list_automation_runs(
        self, params: ListAutomationRunsApiRequest
    ) -> ApiClientResponse[ListAutomationRunsApiResponse]:
        """List automation runs for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/automation/runs",
            model_type=ListAutomationRunsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_automation_run(
        self, params: GetAutomationRunApiRequest
    ) -> ApiClientResponse[GetAutomationRunApiResponse]:
        """Get a single automation run."""
        automation_run_id = params.automation_run_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"automation_run_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/automation/runs/{automation_run_id}",
            model_type=GetAutomationRunApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Attachments
    # ============================================================================
    async def list_attachments(
        self, params: ListAttachmentsApiRequest
    ) -> ApiClientResponse[ListAttachmentsApiResponse]:
        """List attachments for a test case."""
        case_id = params.case_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"case_id"}, mode="python"
        )

        return await self._request_typed(
            method="GET",
            path=f"/api/v1/cases/{case_id}/attachments",
            model_type=ListAttachmentsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Sessions
    # ============================================================================
    async def list_sessions(
        self, params: ListSessionsApiRequest
    ) -> ApiClientResponse[ListSessionsApiResponse]:
        """List sessions for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/sessions",
            model_type=ListSessionsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_session(
        self, params: GetSessionApiRequest
    ) -> ApiClientResponse[GetSessionApiResponse]:
        """Get a single session."""
        session_id = params.session_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"session_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/sessions/{session_id}",
            model_type=GetSessionApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Runs
    # ============================================================================
    async def list_runs(
        self, params: ListRunsApiRequest
    ) -> ApiClientResponse[ListRunsApiResponse]:
        """List runs for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/runs",
            model_type=ListRunsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_run(
        self, params: GetRunApiRequest
    ) -> ApiClientResponse[GetRunApiResponse]:
        """Get a single run."""
        run_id = params.run_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"run_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/runs/{run_id}",
            model_type=GetRunApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Results
    # ============================================================================
    async def list_run_results(
        self, params: ListRunResultsApiRequest
    ) -> ApiClientResponse[ListRunResultsApiResponse]:
        """List results for a run."""
        run_id = params.run_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"run_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/runs/{run_id}/results",
            model_type=ListRunResultsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Milestones
    # ============================================================================
    async def list_milestones(
        self, params: ListMilestonesApiRequest
    ) -> ApiClientResponse[ListMilestonesApiResponse]:
        """List milestones for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/milestones",
            model_type=ListMilestonesApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_milestone(
        self, params: GetMilestoneApiRequest
    ) -> ApiClientResponse[GetMilestoneApiResponse]:
        """Get a single milestone."""
        milestone_id = params.milestone_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"milestone_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/milestones/{milestone_id}",
            model_type=GetMilestoneApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Folders
    # ============================================================================
    async def list_folders(
        self, params: ListFoldersApiRequest
    ) -> ApiClientResponse[ListFoldersApiResponse]:
        """List folders for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/folders",
            model_type=ListFoldersApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Automation Sources
    # ============================================================================
    async def list_automation_sources(
        self, params: ListAutomationSourcesApiRequest
    ) -> ApiClientResponse[ListAutomationSourcesApiResponse]:
        """List automation sources for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/automation/sources",
            model_type=ListAutomationSourcesApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_automation_source(
        self, params: GetAutomationSourceApiRequest
    ) -> ApiClientResponse[GetAutomationSourceApiResponse]:
        """Get a single automation source."""
        automation_source_id = params.automation_source_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"automation_source_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/automation/sources/{automation_source_id}",
            model_type=GetAutomationSourceApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Users
    # ============================================================================
    async def list_users(
        self, params: ListUsersApiRequest
    ) -> ApiClientResponse[ListUsersApiResponse]:
        """List all users (admin API)."""
        query_params = params.model_dump(exclude_none=True, mode="python")
        return await self._request_typed(
            method="GET",
            path="/api/v1/users",
            model_type=ListUsersApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_user(
        self, params: GetUserApiRequest
    ) -> ApiClientResponse[GetUserApiResponse]:
        """Get a single user (admin API)."""
        user_id = params.user_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"user_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/users/{user_id}",
            model_type=GetUserApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def list_project_users(
        self, params: ListProjectUsersApiRequest
    ) -> ApiClientResponse[ListProjectUsersApiResponse]:
        """List users for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/users",
            model_type=ListProjectUsersApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_current_user(self) -> ApiClientResponse[GetCurrentUserApiResponse]:
        """Get the current user."""
        return await self._request_typed(
            method="GET",
            path="/api/v1/user",
            model_type=GetCurrentUserApiResponse,
        )

    # ============================================================================
    # Roles
    # ============================================================================
    async def list_roles(
        self, params: ListRolesApiRequest
    ) -> ApiClientResponse[ListRolesApiResponse]:
        """List all roles (admin API)."""
        query_params = params.model_dump(exclude_none=True, mode="python")
        return await self._request_typed(
            method="GET",
            path="/api/v1/roles",
            model_type=ListRolesApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_role(
        self, params: GetRoleApiRequest
    ) -> ApiClientResponse[GetRoleApiResponse]:
        """Get a single role (admin API)."""
        role_id = params.role_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"role_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/roles/{role_id}",
            model_type=GetRoleApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Groups
    # ============================================================================
    async def list_groups(
        self, params: ListGroupsApiRequest
    ) -> ApiClientResponse[ListGroupsApiResponse]:
        """List all groups (admin API)."""
        query_params = params.model_dump(exclude_none=True, mode="python")
        return await self._request_typed(
            method="GET",
            path="/api/v1/groups",
            model_type=ListGroupsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    async def get_group(
        self, params: GetGroupApiRequest
    ) -> ApiClientResponse[GetGroupApiResponse]:
        """Get a single group (admin API)."""
        group_id = params.group_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"group_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/groups/{group_id}",
            model_type=GetGroupApiResponse,
            query_params=self._flatten_query_params(query_params),
        )

    # ============================================================================
    # Issues
    # ============================================================================
    async def list_issue_connections(
        self, params: ListIssueConnectionsApiRequest
    ) -> ApiClientResponse[ListIssueConnectionsApiResponse]:
        """List issue connections for a project."""
        project_id = params.project_id
        query_params = params.model_dump(
            exclude_none=True, exclude={"project_id"}, mode="python"
        )
        return await self._request_typed(
            method="GET",
            path=f"/api/v1/projects/{project_id}/issues/connections",
            model_type=ListIssueConnectionsApiResponse,
            query_params=self._flatten_query_params(query_params),
        )
