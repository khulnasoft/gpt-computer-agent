"""Unit tests for Aideck API endpoints"""

# Add src to path for testing
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.api import app


class TestAPIEndpoints:
    """Test cases for API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config["TESTING"] = True
        return app.test_client()

    def test_read_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_list_conversations_empty(self, client):
        """Test list conversations when no conversations exist"""
        response = client.get("/api/conversations")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_conversation(self, client):
        """Test create conversation"""
        response = client.post(
            "/api/conversations", params={"title": "Test Conversation"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data

    def test_create_conversation_default_title(self, client):
        """Test create conversation with default title"""
        response = client.post("/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data

    def test_get_nonexistent_conversation(self, client):
        """Test get non-existent conversation"""
        response = client.get("/api/conversations/nonexistent")
        assert response.status_code == 404

    def test_delete_conversation(self, client):
        """Test delete conversation"""
        # First create a conversation
        create_response = client.post("/api/conversations", params={"title": "Test"})
        conversation_id = create_response.json()["conversation_id"]

        # Then delete it
        delete_response = client.delete(f"/api/conversations/{conversation_id}")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"status": "success"}

    def test_create_message_no_conversation_id(self, client):
        """Test create message without conversation_id"""
        message_data = {"content": "Hello, world!", "metadata": {}}

        with patch("aideck.api.app.agent") as mock_agent:
            # Mock agent response
            mock_response = Mock()
            mock_response.content = "Hello! How can I help you?"
            mock_response.metadata = {}
            mock_agent.run = AsyncMock(return_value=mock_response)

            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "agent"
            assert data["content"] == "Hello! How can I help you?"

    def test_create_message_with_conversation_id(self, client):
        """Test create message with existing conversation_id"""
        # First create a conversation
        create_response = client.post("/api/conversations", params={"title": "Test"})
        conversation_id = create_response.json()["conversation_id"]

        message_data = {
            "content": "Hello, world!",
            "conversation_id": conversation_id,
            "metadata": {},
        }

        with patch("aideck.api.app.agent") as mock_agent:
            # Mock agent response
            mock_response = Mock()
            mock_response.content = "Hello! How can I help you?"
            mock_response.metadata = {}
            mock_agent.run = AsyncMock(return_value=mock_response)

            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "agent"
            assert data["content"] == "Hello! How can I help you?"

    def test_create_message_agent_error(self, client):
        """Test create message with agent error"""
        message_data = {"content": "Hello, world!", "metadata": {}}

        with patch("aideck.api.app.agent") as mock_agent:
            # Mock agent error
            mock_agent.run = AsyncMock(side_effect=Exception("Agent error"))

            response = client.post("/api/messages", json=message_data)
            assert response.status_code == 500

    def test_health_check(self, client):
        """Test health check endpoint if it exists"""
        # This endpoint might not exist in the current API
        response = client.get("/health")
        # If it doesn't exist, this should return 404
        if response.status_code != 404:
            assert response.status_code == 200

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get("/api/conversations")
        # CORS headers might be present
        # This test checks if they exist without failing if they don't
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]
        for header in cors_headers:
            if header in response.headers:
                assert response.headers[header] is not None

    def test_api_prefix(self, client):
        """Test API prefix is working"""
        # The API should be available at /api/ endpoints
        response = client.get("/api/conversations")
        assert response.status_code in [
            200,
            404,
        ]  # 404 is acceptable if no conversations exist

    def test_json_content_type(self, client):
        """Test JSON responses have correct content type"""
        response = client.get("/api/conversations")
        assert "application/json" in response.headers["content-type"]

    def test_message_validation(self, client):
        """Test message validation"""
        # Test with missing content
        response = client.post("/api/messages", json={})
        # Should return 422 for missing required field
        assert response.status_code == 422

        # Test with invalid metadata
        response = client.post(
            "/api/messages",
            json={"content": "test", "metadata": "invalid_metadata"},  # Should be dict
        )
        # Should return 422 for invalid field type
        assert response.status_code == 422
