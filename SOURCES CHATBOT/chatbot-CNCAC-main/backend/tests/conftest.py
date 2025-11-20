"""
Pytest configuration and fixtures.
IMPORTANT: tiktoken must be mocked BEFORE any imports to avoid encoding issues.
"""

import sys
from unittest.mock import MagicMock, Mock

# Mock tiktoken BEFORE any other imports to prevent encoding errors in tests
# Create a mock encoding object with encode method
mock_encoding = MagicMock()
mock_encoding.encode = Mock(return_value=[1, 2, 3])  # Return a list of token IDs

# Create tiktoken mock with proper methods
tiktoken_mock = MagicMock()
tiktoken_mock.get_encoding = Mock(return_value=mock_encoding)
tiktoken_mock.encoding_for_model = Mock(return_value=mock_encoding)

# Install tiktoken mocks in sys.modules before any imports
sys.modules['tiktoken'] = tiktoken_mock
sys.modules['tiktoken.load'] = MagicMock()
sys.modules['tiktoken_ext'] = MagicMock()
sys.modules['tiktoken_ext.openai_public'] = MagicMock()

# Now safe to import other modules
import pytest
import asyncio
from typing import Generator
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

load_dotenv("../.env.test")

# Remove deprecated event_loop fixture - pytest-asyncio handles this automatically

@pytest.fixture
def test_client():
    from src.main import app
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_supabase():
    with patch('src.core.database.get_supabase') as mock:
        mock_client = Mock()
        mock_client.auth.sign_up.return_value.user = Mock(id="test-user-id")
        mock_client.auth.sign_in_with_password.return_value.user = Mock(id="test-user-id")
        mock_client.auth.sign_in_with_password.return_value.session = Mock(access_token="test-token")
        mock_client.table.return_value.select.return_value.execute.return_value.data = []
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_neo4j():
    with patch('src.services.neo4j_service.Neo4jService') as mock:
        service = Mock()
        service.vector_search = AsyncMock(return_value=[])
        service.get_entity_context = AsyncMock(return_value=[])
        service.hybrid_search = AsyncMock(return_value=[])
        service.store_chunk = AsyncMock(return_value=None)
        service.create_entities_and_relations = AsyncMock(return_value=None)
        mock.return_value = service
        yield service

@pytest.fixture
def mock_minio():
    with patch('src.services.minio_service.MinioService') as mock:
        service = Mock()
        service.upload_document = AsyncMock(return_value="test-file-url")
        service.get_document = AsyncMock(return_value=b"test content")
        service.delete_document = AsyncMock(return_value=True)
        mock.return_value = service
        yield service

@pytest.fixture
def mock_openai():
    with patch('openai.AsyncOpenAI') as mock:
        client = Mock()
        client.embeddings.create = AsyncMock(return_value=Mock(data=[Mock(embedding=[0.1]*1536)]))
        client.chat.completions.create = AsyncMock(return_value=Mock(
            choices=[Mock(message=Mock(content="Test response"))]
        ))
        mock.return_value = client
        yield client

@pytest.fixture
def sample_document():
    return {
        "id": "test-doc-id",
        "filename": "test.pdf",
        "content": "Test document content",
        "chunks": ["chunk1", "chunk2"],
        "metadata": {"pages": 2}
    }

@pytest.fixture
def sample_chat_request():
    return {
        "message": "Test question",
        "conversation_id": "test-conv-id",
        "user_id": "test-user-id"
    }

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}