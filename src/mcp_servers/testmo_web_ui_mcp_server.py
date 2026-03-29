import logging
from typing import Annotated, ClassVar, List, Literal, Optional

from pydantic import Field

from api_client import TestmoApiClientV1
from api_client.schemas import (
    ExpandsEnum,
    ListAutomationRunsApiRequest,
    ListAutomationSourcesApiRequest,
    ListCasesApiRequest,
    ListFoldersApiRequest,
    ListMilestonesApiRequest,
    ListRunResultsApiRequest,
    ListRunsApiRequest,
    ListSessionsApiRequest,
)
from api_client.schemas.folders import RepositoryFolder
from mcp_servers.base_mcp_server import BaseMCPServer

logger = logging.getLogger("testmo_mcp.testmo_web_ui_mcp_server")


class TestmoWebUiMCPServer(BaseMCPServer):
    """
    Provides a filesystem-like view of Testmo data similar to the web UI.
    This server makes it easy for LLMs to navigate the Testmo data structure similar to the web UI mimicking a human user.
    """

    TOOL_NAMES: ClassVar[list[str]] = [
        "search_cases",
        "browse_folders",
        "get_cases_details",
        "list_manual_runs",
        "get_manual_run_results",
        "list_milestones",
        "list_sessions",
        "list_automation_runs",
        "list_automation_sources",
    ]

    def __init__(self, api_client: TestmoApiClientV1):
        super().__init__(api_client)

    # ============================================================================
    # Cases & Folders
    # ============================================================================
    async def search_cases(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of cases per page (15, 25, 50, 100)", default=100
            ),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        sort: Annotated[
            Optional[
                Literal[
                    "created_at",
                    "created_by",
                    "estimate",
                    "forecast",
                    "has_automation",
                    "id",
                    "name",
                    "state_id",
                    "status_at",
                    "status_id",
                    "folder_id",
                    "template_id",
                    "updated_at",
                    "updated_by",
                ]
            ],
            Field(description="Sort by field", default=None),
        ],
        updated_by: Annotated[
            Optional[List[int]], Field(description="Filter by user IDs", default=None)
        ],
        folder_id: Annotated[
            Optional[List[int]], Field(description="Filter by folder IDs", default=None)
        ],
        template_id: Annotated[
            Optional[List[int]],
            Field(description="Filter by template IDs", default=None),
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter by cases created after (ISO8601 UTC)", default=None
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter by cases created before (ISO8601 UTC)", default=None
            ),
        ],
        state_id: Annotated[
            Optional[List[int]], Field(description="Filter by state IDs", default=None)
        ],
        status_id: Annotated[
            Optional[List[int]], Field(description="Filter by status IDs", default=None)
        ],
        has_automation: Annotated[
            Optional[bool],
            Field(
                description="Filter cases with/without automation links", default=None
            ),
        ],
        has_automation_status: Annotated[
            Optional[bool],
            Field(
                description="Filter cases with/without automation status", default=None
            ),
        ],
    ) -> dict:
        """
        Search for cases in a project with advanced filtering options.
        """
        logger.info(f"TOOL CALLED: search_cases(project_id={project_id}, page={page})")
        try:
            cases_resp = await self.api_client.list_cases(
                ListCasesApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    order=order,
                    sort=f"repository_cases:{sort}" if sort else None,
                    updated_by=updated_by,
                    folder_id=folder_id,
                    template_id=template_id,
                    created_after=created_after,
                    created_before=created_before,
                    state_id=state_id,
                    status_id=status_id,
                    has_automation=has_automation,
                    has_automation_status=has_automation_status,
                )
            )
            result = {
                "cases": [
                    f"[id: {case.id}] {case.name}" for case in cases_resp.data.result
                ],
                "cases_count": cases_resp.data.total,
                "current_page": cases_resp.data.page,
                "cases_per_page": cases_resp.data.per_page,
                "has_next_page": cases_resp.data.has_next_page(),
                "has_prev_page": cases_resp.data.has_prev_page(),
            }
            return result
        except Exception as exc:
            logger.error(f"Unexpected error in search_cases: {exc}", exc_info=True)
            raise exc

    # Linear search for cases details
    async def get_cases_details(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        case_ids: Annotated[
            List[int],
            Field(description="The list of case IDs as integers (limited to 100)"),
        ],
    ) -> dict:
        """
        Get detailed information about multiple test cases.
        """
        try:
            if len(case_ids) > 100:
                raise ValueError(
                    "Too many cases to display, please limit the number of cases to 100"
                )

            logger.info(
                f"TOOL CALLED: get_cases_details(project_id={project_id}, case_ids={case_ids})"
            )

            # Convert case_ids to a set for faster lookup
            requested_case_ids = set(case_ids)
            found_cases_details = []
            found_case_ids = set()

            # Fetch all cases and filter by the requested IDs
            # Note: Testmo API doesn't support filtering by case IDs, so we need to fetch all pages
            current_page = 1
            while True:
                case_resp = await self.api_client.list_cases(
                    ListCasesApiRequest(
                        project_id=project_id,
                        page=current_page,
                        per_page=100,
                        expands=[
                            ExpandsEnum.folders,
                            ExpandsEnum.automation_links,
                            ExpandsEnum.comments,
                            ExpandsEnum.history,
                            ExpandsEnum.users,
                            ExpandsEnum.tags,
                            ExpandsEnum.templates,
                        ],
                    )
                )

                # Filter cases that match the requested IDs
                matching_cases = [
                    case
                    for case in case_resp.data.result
                    if case.id in requested_case_ids
                ]

                for case in matching_cases:
                    found_case_ids.add(case.id)
                    case_details = {
                        "id": case.id,
                        "estimate": case.estimate,
                        "folder": [
                            folder.model_dump()
                            for folder in case_resp.data.expands.folders
                            if folder.id == case.folder_id
                        ],
                        "forecast": case.forecast,
                        "has_automation": case.has_automation,
                        "has_automation_status": case.has_automation_status,
                        "key": case.key,
                        "name": case.name,
                        "state_id": case.state_id,
                        "status_id": case.status_id,
                        "status_at": case.status_at,
                        "template": [
                            template.model_dump()
                            for template in case_resp.data.expands.templates
                            if template.id == case.template_id
                        ],
                        "created_at": case.created_at,
                        "created_by": [
                            user.model_dump()
                            for user in case_resp.data.expands.users
                            if user.id == case.created_by
                        ],
                        "last_updated_at": case.updated_at,
                        "last_updated_by": [
                            user.model_dump()
                            for user in case_resp.data.expands.users
                            if user.id == case.updated_by
                        ],
                        "automation_links": [
                            automation_link.model_dump()
                            for automation_link in case_resp.data.expands.automation_links
                            if automation_link.automation_case_id
                            in case.automation_links
                        ],
                        "tags": [
                            tag.model_dump()
                            for tag in case_resp.data.expands.tags
                            if tag.id in case.tags
                        ],
                        "history": [
                            history.model_dump()
                            for history in case_resp.data.expands.history
                            if history.id in case.history
                        ],
                        "comments": [
                            comment.model_dump()
                            for comment in case_resp.data.expands.comments
                            if comment.id in case.comments
                        ],
                        "custom_fields": case.custom_fields,
                    }
                    found_cases_details.append(case_details)

                # Stop if we found all requested cases or reached the last page
                if (
                    found_case_ids == requested_case_ids
                    or not case_resp.data.has_next_page()
                ):
                    break

                current_page += 1

            missing_case_ids = requested_case_ids - found_case_ids
            result = {"cases": found_cases_details}
            # Add missing case IDs info if any
            if missing_case_ids:
                result["missing_cases"] = {
                    "message": "No cases with these IDs were found in the project",
                    "ids": list(missing_case_ids),
                }

            return result
        except Exception as exc:
            logger.error(f"Unexpected error in get_cases_details: {exc}", exc_info=True)
            raise exc

    # TODO: Binary search for cases details (more efficient than linear search)
    async def get_cases_details_binary(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        case_ids: Annotated[
            List[int],
            Field(description="The list of case IDs as integers (limited to 100)"),
        ],
    ) -> dict:
        """
        Get detailed information about multiple test cases.
        """
        raise NotImplementedError("This method is not implemented yet")

    def _format_folders_to_tree(self, folders: List[RepositoryFolder]) -> List[str]:
        if not folders:
            return []

        pipe_sep = "│   "
        space_sep = "    "
        branch_sep = "├── "
        last_sep = "└── "

        result = []
        draw_pipe = []  # whether each ancestor level should draw │

        for i, folder in enumerate(folders):
            depth = folder.depth

            # shrink stack if we moved up
            draw_pipe = draw_pipe[:depth]

            # detect if there is another sibling at same depth
            has_sibling = False
            for j in range(i + 1, len(folders)):
                if folders[j].depth < depth:
                    break
                if folders[j].depth == depth:
                    has_sibling = True
                    break

            # build prefix
            prefix = ""
            for pipe in draw_pipe:
                prefix += pipe_sep if pipe else space_sep

            prefix += branch_sep if has_sibling else last_sep

            result.append(prefix + f"[id: {folder.id}] {folder.name}")

            # store whether this level continues
            draw_pipe.append(has_sibling)
        return result

    async def browse_folders(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of folders per page (15, 25, 50, 100)", default=100
            ),
        ],
    ) -> dict:
        """
        Browse the folders in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: browse_folders(project_id={project_id}, page={page}, per_page={per_page})"
            )
            folders_resp = await self.api_client.list_folders(
                ListFoldersApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    sort="repository_folders:display_order",
                    order="asc",
                )
            )
            folders = folders_resp.data.result
            folders_tree = self._format_folders_to_tree(folders)
            result = {
                "folders_tree": "\n".join(folders_tree),
                "folders_count": folders_resp.data.total,
                "current_page": folders_resp.data.page,
                "folders_per_page": folders_resp.data.per_page,
                "has_next_page": folders_resp.data.has_next_page(),
                "has_prev_page": folders_resp.data.has_prev_page(),
            }
            return result
        except Exception as exc:
            logger.error(f"Unexpected error in browse_folders: {exc}", exc_info=True)
            raise exc

    # ============================================================================
    # Runs
    # ============================================================================
    async def list_manual_runs(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(description="Number of runs per page (15, 25, 50, 100)", default=100),
        ],
        sort: Annotated[
            Optional[Literal["created_at", "closed_at"]],
            Field(description="Sort field", default=None),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        closed_after: Annotated[
            Optional[str],
            Field(
                description="Filter runs closed after ISO8601 date-time", default=None
            ),
        ],
        closed_before: Annotated[
            Optional[str],
            Field(
                description="Filter runs closed before ISO8601 date-time", default=None
            ),
        ],
        is_closed: Annotated[
            Optional[bool],
            Field(
                description="Limit result to active or closed runs only.", default=None
            ),
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter runs created after ISO8601 date-time", default=None
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter runs created before ISO8601 date-time", default=None
            ),
        ],
        created_by: Annotated[
            Optional[str],
            Field(description="Filter runs by creator user IDs", default=None),
        ],
        milestone_id: Annotated[
            Optional[str],
            Field(description="Filter runs by milestone IDs", default=None),
        ],
        config_id: Annotated[
            Optional[str], Field(description="Filter runs by config IDs", default=None)
        ],
        state_id: Annotated[
            Optional[str], Field(description="Filter runs by state IDs", default=None)
        ],
        tags: Annotated[
            Optional[str], Field(description="Filter runs by tags", default=None)
        ],
    ) -> dict:
        """
        List the manual runs in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: list_manual_runs(project_id={project_id}, page={page}, per_page={per_page})"
            )
            runs_resp = await self.api_client.list_runs(
                ListRunsApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    expands=[
                        ExpandsEnum.configs,
                        ExpandsEnum.issues,
                        ExpandsEnum.milestones,
                        ExpandsEnum.states,
                        ExpandsEnum.statuses,
                        ExpandsEnum.users,
                    ],
                    sort=f"runs:{sort}" if sort else None,
                    order=order,
                    closed_after=closed_after,
                    closed_before=closed_before,
                    is_closed=is_closed,
                    created_after=created_after,
                    created_before=created_before,
                    created_by=created_by,
                    milestone_id=milestone_id,
                    config_id=config_id,
                    state_id=state_id,
                    tags=tags,
                )
            )
            runs_details = {}
            expands = runs_resp.data.expands
            for run in runs_resp.data.result:
                run_details = {
                    "name": run.name,
                    "config": [
                        config.model_dump()
                        for config in expands.configs
                        if config.id == run.config_id
                    ]
                    if expands.configs
                    else None,
                    "milestone": [
                        milestone.model_dump()
                        for milestone in expands.milestones
                        if milestone.id == run.milestone_id
                    ]
                    if expands.milestones
                    else None,
                    "state": [
                        state.model_dump()
                        for state in expands.states
                        if state.id == run.state_id
                    ]
                    if expands.states
                    else None,
                    "forecast": run.forecast,
                    "forecast_completed": run.forecast_completed,
                    "elapsed": run.elapsed,
                    "is_started": run.is_started,
                    "is_closed": run.is_closed,
                    "issues": [
                        issue.model_dump()
                        for issue in expands.issues
                        if issue.id in run.issues
                    ],
                    "links": run.links,
                    "untested_count": run.untested_count,
                    "success_count": run.success_count,
                    "failure_count": run.failure_count,
                    "completed_count": run.completed_count,
                    "total_count": run.total_count,
                    "tags": run.tags,
                    "started_at": run.started_at,
                    "created_at": run.created_at,
                    "created_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == run.created_by
                    ],
                    "last_updated_at": run.updated_at,
                    "last_updated_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == run.updated_by
                    ],
                    "closed_at": run.closed_at,
                    "closed_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == run.closed_by
                    ],
                }
                runs_details[f"[id: {run.id}]"] = run_details
            return {
                "runs": runs_details,
                "runs_count": runs_resp.data.total,
                "current_page": runs_resp.data.page,
                "runs_per_page": runs_resp.data.per_page,
                "has_next_page": runs_resp.data.has_next_page(),
                "has_prev_page": runs_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(f"Unexpected error in list_manual_runs: {exc}", exc_info=True)
            raise exc

    async def get_manual_run_results(
        self,
        run_id: Annotated[int, Field(description="The run ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of results per page (15, 25, 50, 100)", default=100
            ),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        sort: Annotated[
            Optional[Literal["created_at"]],
            Field(description="Sort field", default=None),
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter results created after ISO8601 date-time",
                default=None,
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter results created before ISO8601 date-time",
                default=None,
            ),
        ],
        created_by: Annotated[
            Optional[List[int]],
            Field(description="Filter results by creator user IDs", default=None),
        ],
        assignee_id: Annotated[
            Optional[List[int]],
            Field(description="Filter results by assignee user IDs", default=None),
        ],
        status_id: Annotated[
            Optional[List[int]],
            Field(description="Filter results by status IDs", default=None),
        ],
    ) -> dict:
        """
        Get results of test cases for a manual run.
        """
        try:
            logger.info(
                f"TOOL CALLED: get_manual_run_results(run_id={run_id}, page={page}, per_page={per_page})"
            )
            results_resp = await self.api_client.list_run_results(
                ListRunResultsApiRequest(
                    run_id=run_id,
                    page=page,
                    per_page=per_page,
                    order=order,
                    sort=f"run_results:{sort}" if sort else None,
                    created_after=created_after,
                    created_before=created_before,
                    created_by=created_by,
                    assignee_id=assignee_id,
                    status_id=status_id,
                    get_latest_result=True,
                    expands=[
                        ExpandsEnum.users,
                        ExpandsEnum.statuses,
                        ExpandsEnum.issues,
                    ],
                )
            )
            results = {}
            expands = results_resp.data.expands
            for result in results_resp.data.result:
                test_result = {
                    "case_id": result.case_id,
                    "status": [
                        status.model_dump()
                        for status in expands.statuses
                        if status.id == result.status_id
                    ],
                    "note": result.note,
                    "elapsed": result.elapsed,
                    "assignee": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == result.assignee_id
                    ],
                    "issues": [
                        issue.model_dump()
                        for issue in expands.issues
                        if issue.id in result.issues
                    ],
                    "created_at": result.created_at,
                    "created_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == result.created_by
                    ],
                    "last_updated_at": result.updated_at,
                    "last_updated_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == result.updated_by
                    ],
                }
                results[f"[id: {result.id}]"] = test_result
            return {
                "results": results,
                "results_count": results_resp.data.total,
                "current_page": results_resp.data.page,
                "results_per_page": results_resp.data.per_page,
                "has_next_page": results_resp.data.has_next_page(),
                "has_prev_page": results_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(
                f"Unexpected error in get_manual_run_results: {exc}", exc_info=True
            )
            raise exc

    # ============================================================================
    # Milestones
    # ============================================================================
    async def list_milestones(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of milestones per page (15, 25, 50, 100)",
                default=100,
            ),
        ],
        is_completed: Annotated[
            Optional[bool],
            Field(description="Filter active/completed milestones", default=None),
        ],
        sort: Annotated[
            Optional[Literal["created_at", "completed_at"]],
            Field(description="Sort field", default=None),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        automation_tags: Annotated[
            Optional[List[str]],
            Field(description="Filter milestones by automation tags", default=None),
        ],
        completed_after: Annotated[
            Optional[str],
            Field(
                description="Filter milestones completed after ISO8601 date-time",
                default=None,
            ),
        ],
        completed_before: Annotated[
            Optional[str],
            Field(
                description="Filter milestones completed before ISO8601 date-time",
                default=None,
            ),
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter milestones created after ISO8601 date-time",
                default=None,
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter milestones created before ISO8601 date-time",
                default=None,
            ),
        ],
        created_by: Annotated[
            Optional[List[int]],
            Field(description="Filter milestones by creator user IDs", default=None),
        ],
        parent_id: Annotated[
            Optional[List[int]],
            Field(
                description="Filter milestones by parent milestone IDs", default=None
            ),
        ],
        root_id: Annotated[
            Optional[List[int]],
            Field(description="Filter milestones by root milestone IDs", default=None),
        ],
        type_id: Annotated[
            Optional[List[int]],
            Field(description="Filter milestones by milestone type IDs", default=None),
        ],
    ) -> dict:
        """
        List the milestones in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: list_milestones(project_id={project_id}, page={page}, per_page={per_page})"
            )
            milestones_resp = await self.api_client.list_milestones(
                ListMilestonesApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    is_completed=is_completed,
                    sort=f"milestones:{sort}" if sort else None,
                    order=order,
                    automation_tags=automation_tags,
                    completed_after=completed_after,
                    completed_before=completed_before,
                    created_after=created_after,
                    created_before=created_before,
                    created_by=created_by,
                    parent_id=parent_id,
                    root_id=root_id,
                    type_id=type_id,
                    expands=[
                        ExpandsEnum.issues,
                        ExpandsEnum.milestone_types,
                        ExpandsEnum.users,
                    ],
                )
            )

            milestones_details = {}
            expands = milestones_resp.data.expands
            for milestone in milestones_resp.data.result:
                milestone_details = {
                    "root_milestone_id": milestone.root_id,
                    "parent_milestone_id": milestone.parent_id,
                    "type": [
                        milestone_type.model_dump()
                        for milestone_type in expands.milestone_types
                        if milestone_type.id == milestone.type_id
                    ],
                    "name": milestone.name,
                    "note": milestone.note,
                    "is_started": milestone.is_started,
                    "is_completed": milestone.is_completed,
                    "start_date": milestone.start_date,
                    "due_date": milestone.due_date,
                    "automation_tags": milestone.automation_tags,
                    "issues": [
                        issue.model_dump()
                        for issue in expands.issues
                        if issue.id in milestone.issues
                    ],
                    "links": [link.model_dump() for link in milestone.links],
                    "started_at": milestone.started_at,
                    "created_at": milestone.created_at,
                    "completed_at": milestone.completed_at,
                    "created_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == milestone.created_by
                    ],
                    "updated_at": milestone.updated_at,
                    "updated_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == milestone.updated_by
                    ],
                }
                milestones_details[f"[id: {milestone.id}]"] = milestone_details
            return {
                "milestones": milestones_details,
                "milestones_count": milestones_resp.data.total,
                "current_page": milestones_resp.data.page,
                "milestones_per_page": milestones_resp.data.per_page,
                "has_next_page": milestones_resp.data.has_next_page(),
                "has_prev_page": milestones_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(f"Unexpected error in list_milestones: {exc}", exc_info=True)
            raise exc

    # ============================================================================
    # Sessions
    # ============================================================================
    async def list_sessions(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of sessions per page (15, 25, 50, 100)", default=100
            ),
        ],
        sort: Annotated[
            Optional[Literal["created_at", "closed_at"]],
            Field(description="Sort field", default=None),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        assignee_id: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by assignee user IDs", default=None),
        ],
        closed_after: Annotated[
            Optional[str],
            Field(
                description="Filter sessions closed after ISO8601 date-time",
                default=None,
            ),
        ],
        closed_before: Annotated[
            Optional[str],
            Field(
                description="Filter sessions closed before ISO8601 date-time",
                default=None,
            ),
        ],
        config_id: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by configuration IDs", default=None),
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter sessions created after ISO8601 date-time",
                default=None,
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter sessions created before ISO8601 date-time",
                default=None,
            ),
        ],
        created_by: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by creator user IDs", default=None),
        ],
        is_closed: Annotated[
            Optional[bool],
            Field(description="Filter active/closed sessions", default=None),
        ],
        milestone_id: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by milestone IDs", default=None),
        ],
        state_id: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by state IDs", default=None),
        ],
        tags: Annotated[
            Optional[List[str]],
            Field(description="Filter sessions by tags", default=None),
        ],
        template_id: Annotated[
            Optional[List[int]],
            Field(description="Filter sessions by template IDs", default=None),
        ],
    ) -> dict:
        """
        List the sessions in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: list_sessions(project_id={project_id}, page={page}, per_page={per_page})"
            )
            sessions_resp = await self.api_client.list_sessions(
                ListSessionsApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    sort=f"sessions:{sort}" if sort else None,
                    order=order,
                    assignee_id=assignee_id,
                    closed_after=closed_after,
                    closed_before=closed_before,
                    config_id=config_id,
                    created_after=created_after,
                    created_before=created_before,
                    created_by=created_by,
                    is_closed=is_closed,
                    milestone_id=milestone_id,
                    state_id=state_id,
                    tags=tags,
                    template_id=template_id,
                    expands=[
                        ExpandsEnum.configs,
                        ExpandsEnum.field_values,
                        ExpandsEnum.issues,
                        ExpandsEnum.milestones,
                        ExpandsEnum.states,
                        ExpandsEnum.statuses,
                        ExpandsEnum.templates,
                        ExpandsEnum.users,
                    ],
                )
            )

            sessions_details = {}
            expands = sessions_resp.data.expands
            for session in sessions_resp.data.result:
                session_details = {
                    "template": [
                        template.model_dump()
                        for template in expands.templates
                        if template.id == session.template_id
                    ],
                    "name": session.name,
                    "config": [
                        config.model_dump()
                        for config in expands.configs
                        if config.id == session.config_id
                    ],
                    "milestone": [
                        milestone.model_dump()
                        for milestone in expands.milestones
                        if milestone.id == session.milestone_id
                    ],
                    "state": [
                        state.model_dump()
                        for state in expands.states
                        if state.id == session.state_id
                    ],
                    "assignee": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == session.assignee_id
                    ],
                    "estimate": session.estimate,
                    "forecast": session.forecast,
                    "elapsed": session.elapsed,
                    "is_started": session.is_started,
                    "is_closed": session.is_closed,
                    "issues": [
                        issue.model_dump()
                        for issue in expands.issues
                        if issue.id in session.issues
                    ],
                    "tags": session.tags,
                    "untested_count": session.untested_count,
                    "success_count": session.success_count,
                    "failure_count": session.failure_count,
                    "completed_count": session.completed_count,
                    "total_count": session.total_count,
                    "started_at": session.started_at,
                    "created_at": session.created_at,
                    "created_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == session.created_by
                    ],
                    "updated_at": session.updated_at,
                    "updated_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == session.updated_by
                    ],
                    "closed_at": session.closed_at,
                    "closed_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == session.closed_by
                    ],
                }
                sessions_details[f"[id: {session.id}]"] = session_details
            return {
                "sessions": sessions_details,
                "sessions_count": sessions_resp.data.total,
                "current_page": sessions_resp.data.page,
                "sessions_per_page": sessions_resp.data.per_page,
                "has_next_page": sessions_resp.data.has_next_page(),
                "has_prev_page": sessions_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(f"Unexpected error in list_sessions: {exc}", exc_info=True)
            raise exc

    # ============================================================================
    # Automation Runs
    # ============================================================================
    async def list_automation_runs(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of automation runs per page (15, 25, 50, 100)",
                default=100,
            ),
        ],
        is_completed: Annotated[
            Optional[bool],
            Field(description="Filter active/completed automation runs", default=None),
        ],
        sort: Annotated[
            Optional[Literal["created_at", "completed_at"]],
            Field(description="Sort field", default=None),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        config_id: Annotated[
            Optional[List[int]], Field(description="Filter by config IDs", default=None)
        ],
        created_after: Annotated[
            Optional[str],
            Field(
                description="Filter by automation runs created after ISO8601 date-time",
                default=None,
            ),
        ],
        created_before: Annotated[
            Optional[str],
            Field(
                description="Filter by automation runs created before ISO8601 date-time",
                default=None,
            ),
        ],
        created_by: Annotated[
            Optional[List[int]],
            Field(description="Filter by creator user IDs", default=None),
        ],
        milestone_id: Annotated[
            Optional[List[int]],
            Field(description="Filter by milestone IDs", default=None),
        ],
        source_id: Annotated[
            Optional[List[int]],
            Field(description="Filter by automation source IDs", default=None),
        ],
        status: Annotated[
            Optional[List[int]], Field(description="Filter by statuses", default=None)
        ],
        tags: Annotated[
            Optional[List[str]], Field(description="Filter by tags", default=None)
        ],
    ) -> dict:
        """
        List the automation runs in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: list_automation_runs(project_id={project_id}, page={page})"
            )

            automation_runs_resp = await self.api_client.list_automation_runs(
                ListAutomationRunsApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    is_completed=is_completed,
                    sort=f"automation_runs:{sort}" if sort else None,
                    order=order,
                    config_id=config_id,
                    created_after=created_after,
                    created_before=created_before,
                    created_by=created_by,
                    milestone_id=milestone_id,
                    source_id=source_id,
                    status=status,
                    tags=tags,
                    expands=[
                        ExpandsEnum.automation_sources,
                        ExpandsEnum.configs,
                        ExpandsEnum.milestones,
                        ExpandsEnum.users,
                    ],
                )
            )

            runs_details = {}
            for run in automation_runs_resp.data.result:
                run_details = {
                    "name": run.name,
                    "is_completed": run.is_completed,
                    "created_at": run.created_at,
                    "completed_at": run.completed_at,
                    "total_tests_count": run.total_count,
                    "success_count": run.success_count,
                    "failure_count": run.failure_count,
                    "completed_count": run.completed_count,
                }
                runs_details[f"[id: {run.id}]"] = run_details

            return {
                "automation_runs": runs_details,
                "automation_runs_count": automation_runs_resp.data.total,
                "current_page": automation_runs_resp.data.page,
                "automation_runs_per_page": automation_runs_resp.data.per_page,
                "has_next_page": automation_runs_resp.data.has_next_page(),
                "has_prev_page": automation_runs_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(f"Error in list_automation_runs: {str(exc)}", exc_info=True)
            raise exc

    # ============================================================================
    # Automation Sources
    # ============================================================================
    async def list_automation_sources(
        self,
        project_id: Annotated[int, Field(description="The project ID as integer")],
        page: Annotated[int, Field(description="Page number", default=1)],
        per_page: Annotated[
            Literal[15, 25, 50, 100],
            Field(
                description="Number of automation sources per page (15, 25, 50, 100)",
                default=100,
            ),
        ],
        sort: Annotated[
            Optional[Literal["created_at", "ran_at", "retired_at"]],
            Field(description="Sort field", default=None),
        ],
        order: Annotated[
            Optional[Literal["asc", "desc"]],
            Field(description="Sort order", default=None),
        ],
        is_retired: Annotated[
            Optional[bool],
            Field(description="Filter active/retired automation sources", default=None),
        ],
    ) -> dict:
        """
        List the automation sources in a project.
        """
        try:
            logger.info(
                f"TOOL CALLED: list_automation_sources(project_id={project_id}, page={page})"
            )
            sources_resp = await self.api_client.list_automation_sources(
                ListAutomationSourcesApiRequest(
                    project_id=project_id,
                    page=page,
                    per_page=per_page,
                    sort=f"automation_sources:{sort}" if sort else None,
                    order=order,
                    is_retired=is_retired,
                    expands=[
                        ExpandsEnum.users,
                    ],
                )
            )

            # Format automation sources with key details
            sources_details = {}
            expands = sources_resp.data.expands
            for source in sources_resp.data.result:
                source_details = {
                    "name": source.name,
                    "status": source.status,
                    "is_retired": source.is_retired,
                    "run_count": source.run_count,
                    "test_count_average": source.test_count_average,
                    "elapsed_average": source.elapsed_average,
                    "ran_at": source.ran_at,
                    "created_at": source.created_at,
                    "created_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == source.created_by
                    ],
                    "last_updated_at": source.updated_at,
                    "last_updated_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == source.updated_by
                    ],
                    "retired_at": source.retired_at,
                    "retired_by": [
                        user.model_dump()
                        for user in expands.users
                        if user.id == source.retired_by
                    ],
                }
                sources_details[f"[id: {source.id}]"] = source_details

            return {
                "automation_sources": sources_details,
                "automation_sources_count": sources_resp.data.total,
                "current_page": sources_resp.data.page,
                "automation_sources_per_page": sources_resp.data.per_page,
                "has_next_page": sources_resp.data.has_next_page(),
                "has_prev_page": sources_resp.data.has_prev_page(),
            }
        except Exception as exc:
            logger.error(
                f"Unexpected error in list_automation_sources: {exc}", exc_info=True
            )
            raise exc
