import pytest
import asyncio
import tempfile
import shutil
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.agent_orchestration_engine import AgentOrchestrationEngine
from workflows.workflow_router import WorkflowRouter
from mcp_agent.agents.agent import Agent

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_mcp_agent():
    """Create mock MCP agent."""
    agent = Mock(spec=Agent)
    agent.call_tool = AsyncMock()
    agent.invoke_tool = AsyncMock()
    return agent

@pytest.fixture
def mock_logger():
    """Create mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "oauth": {
            "twitter": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token"
            },
            "linkedin": {
                "client_id": "test_linkedin_id",
                "client_secret": "test_linkedin_secret"
            }
        },
        "social_apis": {
            "twitter": {
                "api_key": "test_key",
                "api_secret": "test_secret"
            }
        }
    }

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_deepcode_input():
    """Sample input for DeepCode workflow."""
    return {
        "user_request": "Implement the BERT algorithm from this research paper",
        "paper_content": "BERT: Pre-training of Deep Bidirectional Transformers...",
        "workflow_mode": "deepcode",
        "file_types": [".pdf"]
    }

@pytest.fixture
def sample_zenalto_input():
    """Sample input for ZenAlto workflow."""
    return {
        "user_request": "Create a professional Twitter thread about AI developments",
        "platforms": ["twitter"],
        "tone": "professional",
        "workflow_mode": "zenalto"
    }

@pytest.fixture
def sample_hybrid_input():
    """Sample input for hybrid workflow."""
    return {
        "user_request": "Create LinkedIn posts explaining this research paper's findings",
        "paper_content": "Novel AI architecture achieving SOTA results...",
        "platforms": ["linkedin"],
        "workflow_mode": "hybrid"
    }

@pytest.fixture
async def orchestration_engine(mock_mcp_agent, mock_logger, test_config):
    """Create test orchestration engine."""
    engine = AgentOrchestrationEngine()
    if hasattr(engine, 'mcp_agent'):
        engine.mcp_agent = mock_mcp_agent
    if hasattr(engine, 'logger'):
        engine.logger = mock_logger
    if hasattr(engine, 'config'):
        engine.config = test_config
    return engine

@pytest.fixture
def workflow_router():
    """Create test workflow router."""
    return WorkflowRouter()

class MockSocialClient:
    """Mock social media client for testing."""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.connected = True
        
    async def post_content(self, text: str, media=None, **kwargs):
        return {
            "success": True,
            "post_id": f"mock_{self.platform}_123",
            "url": f"https://{self.platform}.com/post/123"
        }
    
    async def get_analytics(self, post_ids, metrics=None):
        return {
            "metrics": {
                post_id: {
                    "impressions": 1000,
                    "engagement": 50,
                    "likes": 25
                } for post_id in post_ids
            }
        }
    
    async def get_user_info(self):
        return {
            "id": f"mock_{self.platform}_user",
            "username": f"test_{self.platform}_user",
            "followers_count": 1000
        }

@pytest.fixture
def mock_social_clients():
    """Create mock social media clients."""
    return {
        "twitter": MockSocialClient("twitter"),
        "linkedin": MockSocialClient("linkedin"),
        "instagram": MockSocialClient("instagram")
    }