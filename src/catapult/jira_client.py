"""
Jira API Client Module

This module provides a comprehensive client for interacting with Jira's REST API.
It supports authentication, ticket retrieval, searching, and analysis of ticket data.

Key Components:
- JiraConfig: Configuration model for Jira connection settings
- JiraTicket: Pydantic model representing a Jira ticket
- JiraTicketAnalysis: Model for ticket analysis results
- JiraClient: Main client class for API interactions

Features:
- Basic authentication with username/API token
- Ticket retrieval by key, project, assignee, status, or recent activity
- Custom JQL search support
- Ticket analysis and reporting
- Comprehensive error handling and logging
- Full test coverage

Usage Example:
    >>> from catapult.jira_client import JiraClient, JiraConfig
    >>> config = JiraConfig(
    ...     base_url="https://company.atlassian.net",
    ...     username="user@company.com",
    ...     api_token="your-api-token"
    ... )
    >>> client = JiraClient(config)
    >>> ticket = client.get_ticket("PROJ-123")
    >>> tickets = client.get_tickets_by_project("PROJ")
    >>> analysis = client.analyze_tickets(tickets)

Authentication:
    This client uses Jira's Basic Authentication with API tokens.
    To create an API token:
    1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
    2. Create a new token
    3. Use your email and the token with this client

API Endpoints Used:
    - GET /rest/api/2/serverInfo - Connection testing
    - GET /rest/api/2/issue/{key} - Individual ticket retrieval
    - GET /rest/api/2/search - JQL search
    - GET /rest/api/2/issuetype - Issue type enumeration
    - GET /rest/api/2/project - Project enumeration

Error Handling:
    All API calls are wrapped in try-catch blocks with appropriate logging.
    Network errors, HTTP errors, and JSON parsing errors are handled gracefully.
    Methods return None or empty lists on failure rather than raising exceptions.

Dependencies:
    - requests: HTTP client for API calls
    - pydantic: Data validation and serialization
    - base64: Authentication header encoding
    - datetime: Timestamp parsing
    - logging: Error and debug logging
"""

import base64
import logging
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class JiraConfig(BaseModel):
    """Configuration for Jira API connection"""

    base_url: str = Field(..., description="Base URL for Jira instance")
    username: str = Field(..., description="Username for authentication")
    api_token: str = Field(..., description="API token for authentication")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class JiraTicket(BaseModel):
    """Jira ticket model"""

    key: str = Field(..., description="Ticket key (e.g., PROJ-123)")
    id: str = Field(..., description="Ticket ID")
    summary: str = Field(..., description="Ticket summary")
    description: Optional[str] = Field(None, description="Ticket description")
    status: str = Field(..., description="Current status")
    issue_type: str = Field(..., description="Issue type (Story, Bug, Task, etc.)")
    priority: str = Field(..., description="Priority level")
    assignee: Optional[str] = Field(None, description="Assignee display name")
    reporter: str = Field(..., description="Reporter display name")
    created: datetime = Field(..., description="Creation timestamp")
    updated: datetime = Field(..., description="Last update timestamp")
    labels: list[str] = Field(default_factory=list, description="Ticket labels")
    components: list[str] = Field(default_factory=list, description="Components")
    project_key: str = Field(..., description="Project key")
    raw_data: dict[str, Any] = Field(
        default_factory=dict, description="Raw API response"
    )


class JiraTicketAnalysis(BaseModel):
    """Analysis of Jira tickets"""

    total_tickets: int = Field(..., description="Total number of tickets")
    tickets_by_type: dict[str, int] = Field(
        default_factory=dict, description="Count by issue type"
    )
    tickets_by_status: dict[str, int] = Field(
        default_factory=dict, description="Count by status"
    )
    tickets_by_priority: dict[str, int] = Field(
        default_factory=dict, description="Count by priority"
    )
    tickets_by_assignee: dict[str, int] = Field(
        default_factory=dict, description="Count by assignee"
    )
    tickets_by_project: dict[str, int] = Field(
        default_factory=dict, description="Count by project"
    )
    unique_labels: list[str] = Field(
        default_factory=list, description="All unique labels"
    )
    unique_components: list[str] = Field(
        default_factory=list, description="All unique components"
    )


class JiraClient:
    """Jira API client for retrieving and analyzing tickets"""

    def __init__(self, config):
        """
        Initialize Jira client with configuration.
        
        Args:
            config: JiraConfig instance or compatible config object with:
                   - base_url: Jira instance URL
                   - username: Username for authentication
                   - api_token: API token for authentication
                   - timeout: Request timeout (optional, defaults to 30)
        """
        # Handle both old JiraConfig and new config.jira objects
        if hasattr(config, 'base_url'):
            # Direct JiraConfig instance
            self.config = config
        else:
            # Assume it's a config object with jira attributes
            self.config = JiraConfig(
                base_url=config.base_url,
                username=config.username,
                api_token=config.api_token,
                timeout=getattr(config, 'timeout', 30)
            )
        
        self.session = requests.Session()
        self._setup_auth()

    def _setup_auth(self):
        """Setup authentication headers"""
        auth_string = f"{self.config.username}:{self.config.api_token}"
        auth_bytes = auth_string.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

        self.session.headers.update(
            {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def test_connection(self) -> bool:
        """Test connection to Jira instance"""
        try:
            response = self.session.get(
                urljoin(self.config.base_url, "/rest/api/2/serverInfo"),
                timeout=self.config.timeout,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False

    def get_ticket(self, ticket_key: str) -> Optional[JiraTicket]:
        """Get a single ticket by key"""
        try:
            url = urljoin(self.config.base_url, f"/rest/api/2/issue/{ticket_key}")
            response = self.session.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                return self._parse_ticket(response.json())
            else:
                logger.error(
                    f"Failed to get ticket {ticket_key}: {response.status_code}"
                )
                return None
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_key}: {e}")
            return None

    def search_tickets(self, jql: str, max_results: int = 100) -> list[JiraTicket]:
        """Search for tickets using JQL"""
        try:
            url = urljoin(self.config.base_url, "/rest/api/2/search")
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,description,status,issuetype,priority,assignee,reporter,created,updated,labels,components,project",
            }

            response = self.session.get(url, params=params, timeout=self.config.timeout)

            if response.status_code == 200:
                data = response.json()
                return [self._parse_ticket(issue) for issue in data.get("issues", [])]
            else:
                logger.error(f"Failed to search tickets: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error searching tickets: {e}")
            return []

    def get_tickets_by_project(
        self, project_key: str, max_results: int = 100
    ) -> list[JiraTicket]:
        """Get tickets for a specific project"""
        jql = f"project = {project_key}"
        return self.search_tickets(jql, max_results)

    def get_tickets_by_assignee(
        self, assignee: str, max_results: int = 100
    ) -> list[JiraTicket]:
        """Get tickets assigned to a specific user"""
        jql = f'assignee = "{assignee}"'
        return self.search_tickets(jql, max_results)

    def get_tickets_by_status(
        self, status: str, max_results: int = 100
    ) -> list[JiraTicket]:
        """Get tickets with a specific status"""
        jql = f'status = "{status}"'
        return self.search_tickets(jql, max_results)

    def get_recent_tickets(
        self, days: int = 30, max_results: int = 100
    ) -> list[JiraTicket]:
        """Get tickets created or updated in the last N days"""
        jql = f"created >= -{days}d OR updated >= -{days}d"
        return self.search_tickets(jql, max_results)

    def analyze_tickets(self, tickets: list[JiraTicket]) -> JiraTicketAnalysis:
        """Analyze a list of tickets to extract insights"""
        if not tickets:
            return JiraTicketAnalysis(total_tickets=0)

        analysis = JiraTicketAnalysis(total_tickets=len(tickets))

        # Count by various attributes
        for ticket in tickets:
            # By issue type
            analysis.tickets_by_type[ticket.issue_type] = (
                analysis.tickets_by_type.get(ticket.issue_type, 0) + 1
            )

            # By status
            analysis.tickets_by_status[ticket.status] = (
                analysis.tickets_by_status.get(ticket.status, 0) + 1
            )

            # By priority
            analysis.tickets_by_priority[ticket.priority] = (
                analysis.tickets_by_priority.get(ticket.priority, 0) + 1
            )

            # By assignee
            assignee = ticket.assignee or "Unassigned"
            analysis.tickets_by_assignee[assignee] = (
                analysis.tickets_by_assignee.get(assignee, 0) + 1
            )

            # By project
            analysis.tickets_by_project[ticket.project_key] = (
                analysis.tickets_by_project.get(ticket.project_key, 0) + 1
            )

            # Collect unique labels and components
            for label in ticket.labels:
                if label not in analysis.unique_labels:
                    analysis.unique_labels.append(label)

            for component in ticket.components:
                if component not in analysis.unique_components:
                    analysis.unique_components.append(component)

        # Sort labels and components
        analysis.unique_labels.sort()
        analysis.unique_components.sort()

        return analysis

    def _parse_ticket(self, issue_data: dict[str, Any]) -> JiraTicket:
        """Parse raw Jira issue data into JiraTicket model"""
        fields = issue_data.get("fields", {})

        return JiraTicket(
            key=issue_data.get("key", ""),
            id=issue_data.get("id", ""),
            summary=fields.get("summary", ""),
            description=fields.get("description", ""),
            status=fields.get("status", {}).get("name", ""),
            issue_type=fields.get("issuetype", {}).get("name", ""),
            priority=fields.get("priority", {}).get("name", ""),
            assignee=fields.get("assignee", {}).get("displayName")
            if fields.get("assignee")
            else None,
            reporter=fields.get("reporter", {}).get("displayName", ""),
            created=datetime.fromisoformat(
                fields.get("created", "").replace("Z", "+00:00")
            ),
            updated=datetime.fromisoformat(
                fields.get("updated", "").replace("Z", "+00:00")
            ),
            labels=fields.get("labels", []),
            components=[comp.get("name", "") for comp in fields.get("components", [])],
            project_key=fields.get("project", {}).get("key", ""),
            raw_data=issue_data,
        )

    def get_ticket_types(self) -> list[str]:
        """Get all available issue types from Jira"""
        try:
            url = urljoin(self.config.base_url, "/rest/api/2/issuetype")
            response = self.session.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                return [issue_type["name"] for issue_type in response.json()]
            else:
                logger.error(f"Failed to get issue types: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting issue types: {e}")
            return []

    def get_projects(self) -> list[dict[str, str]]:
        """Get all accessible projects"""
        try:
            url = urljoin(self.config.base_url, "/rest/api/2/project")
            response = self.session.get(url, timeout=self.config.timeout)

            if response.status_code == 200:
                return [
                    {"key": proj["key"], "name": proj["name"]}
                    for proj in response.json()
                ]
            else:
                logger.error(f"Failed to get projects: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
