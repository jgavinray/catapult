from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src.catapult.jira_client import (
    JiraClient,
    JiraConfig,
    JiraTicket,
)


@pytest.fixture()
def jira_config():
    """Test Jira configuration"""
    return JiraConfig(
        base_url="https://test.atlassian.net",
        username="test@example.com",
        api_token="test-token",
    )


@pytest.fixture()
def jira_client(jira_config):
    """Test Jira client"""
    return JiraClient(jira_config)


@pytest.fixture()
def sample_ticket_data():
    """Sample Jira ticket data"""
    return {
        "key": "TEST-123",
        "id": "12345",
        "fields": {
            "summary": "Test ticket summary",
            "description": "Test ticket description",
            "status": {"name": "In Progress"},
            "issuetype": {"name": "Story"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"},
            "created": "2023-01-01T10:00:00.000Z",
            "updated": "2023-01-02T10:00:00.000Z",
            "labels": ["urgent", "backend"],
            "components": [{"name": "API"}, {"name": "Database"}],
            "project": {"key": "TEST"},
        },
    }


@pytest.fixture()
def sample_search_response():
    """Sample Jira search response"""
    return {
        "issues": [
            {
                "key": "TEST-123",
                "id": "12345",
                "fields": {
                    "summary": "Test ticket 1",
                    "description": "Description 1",
                    "status": {"name": "In Progress"},
                    "issuetype": {"name": "Story"},
                    "priority": {"name": "High"},
                    "assignee": {"displayName": "John Doe"},
                    "reporter": {"displayName": "Jane Smith"},
                    "created": "2023-01-01T10:00:00.000Z",
                    "updated": "2023-01-02T10:00:00.000Z",
                    "labels": ["urgent"],
                    "components": [{"name": "API"}],
                    "project": {"key": "TEST"},
                },
            },
            {
                "key": "TEST-124",
                "id": "12346",
                "fields": {
                    "summary": "Test ticket 2",
                    "description": "Description 2",
                    "status": {"name": "Done"},
                    "issuetype": {"name": "Bug"},
                    "priority": {"name": "Medium"},
                    "assignee": None,
                    "reporter": {"displayName": "Bob Johnson"},
                    "created": "2023-01-03T10:00:00.000Z",
                    "updated": "2023-01-04T10:00:00.000Z",
                    "labels": ["backend"],
                    "components": [{"name": "Database"}],
                    "project": {"key": "TEST"},
                },
            },
        ]
    }


class TestJiraConfig:
    """Test JiraConfig model"""

    def test_jira_config_creation(self):
        """Test JiraConfig creation with required fields"""
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )
        assert config.base_url == "https://test.atlassian.net"
        assert config.username == "test@example.com"
        assert config.api_token == "test-token"
        assert config.timeout == 30  # default value

    def test_jira_config_with_custom_timeout(self):
        """Test JiraConfig with custom timeout"""
        config = JiraConfig(
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
            timeout=60,
        )
        assert config.timeout == 60


class TestJiraTicket:
    """Test JiraTicket model"""

    def test_jira_ticket_creation(self):
        """Test JiraTicket creation"""
        ticket = JiraTicket(
            key="TEST-123",
            id="12345",
            summary="Test summary",
            status="In Progress",
            issue_type="Story",
            priority="High",
            reporter="Jane Smith",
            created=datetime.now(),
            updated=datetime.now(),
            project_key="TEST",
        )
        assert ticket.key == "TEST-123"
        assert ticket.id == "12345"
        assert ticket.summary == "Test summary"
        assert ticket.status == "In Progress"
        assert ticket.issue_type == "Story"
        assert ticket.priority == "High"
        assert ticket.reporter == "Jane Smith"
        assert ticket.project_key == "TEST"


class TestJiraClient:
    """Test JiraClient class"""

    def test_client_initialization(self, jira_client):
        """Test client initialization"""
        assert jira_client.config.base_url == "https://test.atlassian.net"
        assert jira_client.session is not None
        assert "Authorization" in jira_client.session.headers
        assert jira_client.session.headers["Content-Type"] == "application/json"

    @patch("requests.Session.get")
    def test_test_connection_success(self, mock_get, jira_client):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = jira_client.test_connection()
        assert result is True
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_test_connection_failure(self, mock_get, jira_client):
        """Test failed connection test"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = jira_client.test_connection()
        assert result is False

    @patch("requests.Session.get")
    def test_test_connection_exception(self, mock_get, jira_client):
        """Test connection test with exception"""
        mock_get.side_effect = requests.RequestException("Connection error")

        result = jira_client.test_connection()
        assert result is False

    @patch("requests.Session.get")
    def test_get_ticket_success(self, mock_get, jira_client, sample_ticket_data):
        """Test successful ticket retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ticket_data
        mock_get.return_value = mock_response

        ticket = jira_client.get_ticket("TEST-123")

        assert ticket is not None
        assert ticket.key == "TEST-123"
        assert ticket.summary == "Test ticket summary"
        assert ticket.status == "In Progress"
        assert ticket.issue_type == "Story"
        assert ticket.priority == "High"
        assert ticket.assignee == "John Doe"
        assert ticket.reporter == "Jane Smith"
        assert ticket.labels == ["urgent", "backend"]
        assert ticket.components == ["API", "Database"]
        assert ticket.project_key == "TEST"

    @patch("requests.Session.get")
    def test_get_ticket_not_found(self, mock_get, jira_client):
        """Test ticket retrieval when ticket not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        ticket = jira_client.get_ticket("NONEXISTENT-123")
        assert ticket is None

    @patch("requests.Session.get")
    def test_get_ticket_exception(self, mock_get, jira_client):
        """Test ticket retrieval with exception"""
        mock_get.side_effect = requests.RequestException("Network error")

        ticket = jira_client.get_ticket("TEST-123")
        assert ticket is None

    @patch("requests.Session.get")
    def test_search_tickets_success(
        self, mock_get, jira_client, sample_search_response
    ):
        """Test successful ticket search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_get.return_value = mock_response

        tickets = jira_client.search_tickets("project = TEST")

        assert len(tickets) == 2
        assert tickets[0].key == "TEST-123"
        assert tickets[1].key == "TEST-124"
        assert tickets[0].assignee == "John Doe"
        assert tickets[1].assignee is None

    @patch("requests.Session.get")
    def test_search_tickets_failure(self, mock_get, jira_client):
        """Test failed ticket search"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        tickets = jira_client.search_tickets("invalid jql")
        assert len(tickets) == 0

    @patch("requests.Session.get")
    def test_get_tickets_by_project(
        self, mock_get, jira_client, sample_search_response
    ):
        """Test getting tickets by project"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_get.return_value = mock_response

        tickets = jira_client.get_tickets_by_project("TEST")

        assert len(tickets) == 2
        mock_get.assert_called_once()
        # Verify the JQL query was constructed correctly
        call_args = mock_get.call_args
        assert "project = TEST" in call_args[1]["params"]["jql"]

    @patch("requests.Session.get")
    def test_get_tickets_by_assignee(
        self, mock_get, jira_client, sample_search_response
    ):
        """Test getting tickets by assignee"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_get.return_value = mock_response

        tickets = jira_client.get_tickets_by_assignee("John Doe")

        assert len(tickets) == 2
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'assignee = "John Doe"' in call_args[1]["params"]["jql"]

    @patch("requests.Session.get")
    def test_get_tickets_by_status(self, mock_get, jira_client, sample_search_response):
        """Test getting tickets by status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_get.return_value = mock_response

        tickets = jira_client.get_tickets_by_status("In Progress")

        assert len(tickets) == 2
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'status = "In Progress"' in call_args[1]["params"]["jql"]

    @patch("requests.Session.get")
    def test_get_recent_tickets(self, mock_get, jira_client, sample_search_response):
        """Test getting recent tickets"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_get.return_value = mock_response

        tickets = jira_client.get_recent_tickets(7)

        assert len(tickets) == 2
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "created >= -7d OR updated >= -7d" in call_args[1]["params"]["jql"]

    @patch("requests.Session.get")
    def test_get_ticket_types(self, mock_get, jira_client):
        """Test getting issue types"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Story", "id": "1"},
            {"name": "Bug", "id": "2"},
            {"name": "Task", "id": "3"},
        ]
        mock_get.return_value = mock_response

        types = jira_client.get_ticket_types()

        assert len(types) == 3
        assert "Story" in types
        assert "Bug" in types
        assert "Task" in types

    @patch("requests.Session.get")
    def test_get_projects(self, mock_get, jira_client):
        """Test getting projects"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"key": "TEST", "name": "Test Project"},
            {"key": "DEMO", "name": "Demo Project"},
        ]
        mock_get.return_value = mock_response

        projects = jira_client.get_projects()

        assert len(projects) == 2
        assert projects[0]["key"] == "TEST"
        assert projects[0]["name"] == "Test Project"
        assert projects[1]["key"] == "DEMO"
        assert projects[1]["name"] == "Demo Project"


class TestJiraTicketAnalysis:
    """Test ticket analysis functionality"""

    def test_analyze_empty_tickets(self, jira_client):
        """Test analysis of empty ticket list"""
        analysis = jira_client.analyze_tickets([])

        assert analysis.total_tickets == 0
        assert len(analysis.tickets_by_type) == 0
        assert len(analysis.tickets_by_status) == 0
        assert len(analysis.tickets_by_priority) == 0
        assert len(analysis.tickets_by_assignee) == 0
        assert len(analysis.tickets_by_project) == 0
        assert len(analysis.unique_labels) == 0
        assert len(analysis.unique_components) == 0

    def test_analyze_tickets(self, jira_client):
        """Test analysis of tickets"""
        tickets = [
            JiraTicket(
                key="TEST-123",
                id="12345",
                summary="Test 1",
                status="In Progress",
                issue_type="Story",
                priority="High",
                assignee="John Doe",
                reporter="Jane Smith",
                created=datetime.now(),
                updated=datetime.now(),
                labels=["urgent", "backend"],
                components=["API", "Database"],
                project_key="TEST",
            ),
            JiraTicket(
                key="TEST-124",
                id="12346",
                summary="Test 2",
                status="Done",
                issue_type="Bug",
                priority="Medium",
                assignee=None,
                reporter="Bob Johnson",
                created=datetime.now(),
                updated=datetime.now(),
                labels=["backend"],
                components=["Database"],
                project_key="TEST",
            ),
            JiraTicket(
                key="DEMO-100",
                id="12347",
                summary="Demo ticket",
                status="In Progress",
                issue_type="Story",
                priority="Low",
                assignee="John Doe",
                reporter="Alice Brown",
                created=datetime.now(),
                updated=datetime.now(),
                labels=["frontend"],
                components=["UI"],
                project_key="DEMO",
            ),
        ]

        analysis = jira_client.analyze_tickets(tickets)

        assert analysis.total_tickets == 3

        # Check counts by type
        assert analysis.tickets_by_type["Story"] == 2
        assert analysis.tickets_by_type["Bug"] == 1

        # Check counts by status
        assert analysis.tickets_by_status["In Progress"] == 2
        assert analysis.tickets_by_status["Done"] == 1

        # Check counts by priority
        assert analysis.tickets_by_priority["High"] == 1
        assert analysis.tickets_by_priority["Medium"] == 1
        assert analysis.tickets_by_priority["Low"] == 1

        # Check counts by assignee
        assert analysis.tickets_by_assignee["John Doe"] == 2
        assert analysis.tickets_by_assignee["Unassigned"] == 1

        # Check counts by project
        assert analysis.tickets_by_project["TEST"] == 2
        assert analysis.tickets_by_project["DEMO"] == 1

        # Check unique labels (should be sorted)
        assert analysis.unique_labels == ["backend", "frontend", "urgent"]

        # Check unique components (should be sorted)
        assert analysis.unique_components == ["API", "Database", "UI"]


class TestJiraTicketParsing:
    """Test ticket parsing functionality"""

    def test_parse_ticket_with_all_fields(self, jira_client, sample_ticket_data):
        """Test parsing ticket with all fields present"""
        ticket = jira_client._parse_ticket(sample_ticket_data)

        assert ticket.key == "TEST-123"
        assert ticket.id == "12345"
        assert ticket.summary == "Test ticket summary"
        assert ticket.description == "Test ticket description"
        assert ticket.status == "In Progress"
        assert ticket.issue_type == "Story"
        assert ticket.priority == "High"
        assert ticket.assignee == "John Doe"
        assert ticket.reporter == "Jane Smith"
        assert ticket.labels == ["urgent", "backend"]
        assert ticket.components == ["API", "Database"]
        assert ticket.project_key == "TEST"
        assert ticket.raw_data == sample_ticket_data

    def test_parse_ticket_with_missing_fields(self, jira_client):
        """Test parsing ticket with missing optional fields"""
        minimal_data = {
            "key": "TEST-123",
            "id": "12345",
            "fields": {
                "summary": "Test summary",
                "status": {"name": "Open"},
                "issuetype": {"name": "Task"},
                "priority": {"name": "Medium"},
                "reporter": {"displayName": "Reporter"},
                "created": "2023-01-01T10:00:00.000Z",
                "updated": "2023-01-01T10:00:00.000Z",
                "project": {"key": "TEST"},
            },
        }

        ticket = jira_client._parse_ticket(minimal_data)

        assert ticket.key == "TEST-123"
        assert ticket.summary == "Test summary"
        assert ticket.assignee is None
        assert ticket.description == ""
        assert ticket.labels == []
        assert ticket.components == []
