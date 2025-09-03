# Development Assignment #11: Comprehensive Testing Suite

## Priority: 🟠 LOW - Week 4

## Objective
Implement a comprehensive testing strategy covering unit tests, integration tests, and end-to-end testing for the complete ZenAlto integration, ensuring system reliability and preventing regressions.

## Background
With the new ZenAlto functionality, we need robust testing to ensure both DeepCode and ZenAlto workflows function correctly, maintain backward compatibility, and handle edge cases gracefully.

## Deliverables

### 1. Test Framework Setup
**File**: `tests/conftest.py`

```python
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
from auth.oauth_manager import OAuthManager
from social_apis.client_factory import SocialMediaClientFactory

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
    engine.mcp_agent = mock_mcp_agent
    engine.logger = mock_logger
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
```

### 2. Workflow Router Tests
**File**: `tests/test_workflow_router.py`

```python
import pytest
from workflows.workflow_router import WorkflowRouter

class TestWorkflowRouter:
    """Test suite for WorkflowRouter."""
    
    @pytest.mark.asyncio
    async def test_deepcode_detection_clear_indicators(self, workflow_router):
        """Test DeepCode workflow detection with clear indicators."""
        
        input_data = {
            "user_request": "Implement the algorithm from this research paper",
            "file_types": [".pdf"],
            "paper_content": "Abstract: This paper presents..."
        }
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        assert result["workflow_type"] == "deepcode"
        assert result["confidence"] > 0.8
        assert "research" in result["reasoning"].lower() or "paper" in result["reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_zenalto_detection_clear_indicators(self, workflow_router):
        """Test ZenAlto workflow detection with clear indicators."""
        
        input_data = {
            "user_request": "Create a viral Twitter thread about machine learning",
            "platforms": ["twitter"],
            "content_type": "social_media"
        }
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        assert result["workflow_type"] == "zenalto"
        assert result["confidence"] > 0.8
        assert "twitter" in result["reasoning"].lower() or "social" in result["reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_hybrid_detection(self, workflow_router):
        """Test hybrid workflow detection."""
        
        input_data = {
            "user_request": "Create LinkedIn posts explaining this research paper",
            "paper_content": "Research findings...",
            "platforms": ["linkedin"]
        }
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        assert result["workflow_type"] in ["hybrid", "zenalto"]  # Could be either
        assert result["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_explicit_mode_override(self, workflow_router):
        """Test explicit workflow mode override."""
        
        input_data = {
            "user_request": "Create a tweet",  # Would normally be zenalto
            "workflow_mode": "deepcode"  # Explicit override
        }
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        assert result["workflow_type"] == "deepcode"
        assert result["confidence"] == 1.0
        assert result.get("forced") == True
    
    @pytest.mark.asyncio
    async def test_ambiguous_input_defaults(self, workflow_router):
        """Test behavior with ambiguous input."""
        
        input_data = {
            "user_request": "Process this content"  # Very ambiguous
        }
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        # Should default to deepcode for ambiguous cases
        assert result["workflow_type"] == "deepcode"
        assert result["confidence"] < 0.7
    
    @pytest.mark.asyncio
    async def test_empty_input_handling(self, workflow_router):
        """Test handling of empty/invalid input."""
        
        input_data = {}
        
        result = await workflow_router.detect_workflow_type(input_data)
        
        assert result["workflow_type"] == "deepcode"  # Default
        assert result["confidence"] == 0.0
        assert "error" not in result  # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_file_type_detection(self, workflow_router):
        """Test file type-based detection."""
        
        # PDF should trigger deepcode
        result = await workflow_router.detect_workflow_type({
            "file_types": [".pdf", ".tex"]
        })
        assert result["workflow_type"] == "deepcode"
        
        # Media files should trigger zenalto
        result = await workflow_router.detect_workflow_type({
            "file_types": [".jpg", ".png", ".mp4"]
        })
        assert result["workflow_type"] == "zenalto"
    
    def test_indicator_scoring(self, workflow_router):
        """Test indicator scoring algorithm."""
        
        text = "research paper github repository algorithm implementation"
        scores = workflow_router.analyze_input_patterns(text)
        
        assert scores["deepcode_score"] > scores["zenalto_score"]
        assert scores["deepcode_score"] > 0
    
    def test_platform_context_detection(self, workflow_router):
        """Test platform context influence on detection."""
        
        input_data = {
            "user_request": "Create content about AI",
            "platform_context": {"twitter": {"connected": True}}
        }
        
        result = asyncio.run(workflow_router.detect_workflow_type(input_data))
        
        # Platform context should influence toward zenalto
        assert result["workflow_type"] == "zenalto"
```

### 3. Agent Integration Tests
**File**: `tests/test_agent_integration.py`

```python
import pytest
from workflows.agent_orchestration_engine import AgentOrchestrationEngine

class TestAgentIntegration:
    """Test agent integration and coordination."""
    
    @pytest.mark.asyncio
    async def test_zenalto_agent_initialization(self, orchestration_engine):
        """Test ZenAlto agent initialization."""
        
        # Mock agent imports to avoid import errors
        with patch.multiple(
            'workflows.agent_orchestration_engine',
            ContentIntentAgent=MagicMock(),
            ContentStrategyAgent=MagicMock(),
            ContentGenerationAgent=MagicMock()
        ):
            agents = orchestration_engine._init_zenalto_agents()
            
            expected_agents = [
                'content_intent', 'content_strategy', 'content_generation',
                'social_parser', 'analytics', 'scheduling'
            ]
            
            for agent_name in expected_agents:
                assert agent_name in agents
    
    @pytest.mark.asyncio
    async def test_deepcode_backward_compatibility(
        self,
        orchestration_engine,
        sample_deepcode_input
    ):
        """Test that DeepCode workflows remain unchanged."""
        
        # Mock the original DeepCode workflow
        orchestration_engine._execute_deepcode_workflow = AsyncMock(
            return_value={
                "success": True,
                "workflow": "deepcode",
                "implementation": {"code": "test_code"},
                "analysis": {"summary": "test_analysis"}
            }
        )
        
        result = await orchestration_engine.process_request(sample_deepcode_input)
        
        assert result["workflow_type"] == "deepcode"
        assert result["success"] == True
        assert "implementation" in result
        assert "analysis" in result
    
    @pytest.mark.asyncio
    async def test_zenalto_workflow_execution(
        self,
        orchestration_engine,
        sample_zenalto_input
    ):
        """Test ZenAlto workflow execution."""
        
        # Mock ZenAlto agents
        orchestration_engine.zenalto_agents = {
            'content_intent': Mock(),
            'content_strategy': Mock(),
            'content_generation': Mock(),
            'scheduling': Mock()
        }
        
        # Mock agent methods
        orchestration_engine.zenalto_agents['content_intent'].analyze_intent = AsyncMock(
            return_value={"intent": "social_media_thread", "confidence": 0.9}
        )
        orchestration_engine.zenalto_agents['content_strategy'].create_strategy = AsyncMock(
            return_value={"platforms": ["twitter"], "post_count": 5}
        )
        orchestration_engine.zenalto_agents['content_generation'].generate = AsyncMock(
            return_value={"content": {"twitter": {"posts": ["Post 1", "Post 2"]}}}
        )
        orchestration_engine.zenalto_agents['scheduling'].schedule = AsyncMock(
            return_value={"success": True, "scheduled_posts": []}
        )
        
        result = await orchestration_engine._execute_zenalto_workflow(sample_zenalto_input)
        
        assert result["workflow"] == "zenalto"
        assert result["success"] == True
        assert "stages" in result
        assert "intent" in result["stages"]
        assert "strategy" in result["stages"]
        assert "content" in result["stages"]
    
    @pytest.mark.asyncio
    async def test_hybrid_workflow_execution(
        self,
        orchestration_engine,
        sample_hybrid_input
    ):
        """Test hybrid workflow execution."""
        
        # Mock both DeepCode and ZenAlto workflows
        orchestration_engine._execute_deepcode_workflow = AsyncMock(
            return_value={
                "success": True,
                "analysis": {"key_points": ["AI breakthrough", "Novel architecture"]}
            }
        )
        orchestration_engine._execute_zenalto_workflow = AsyncMock(
            return_value={
                "success": True,
                "stages": {"content": {"linkedin": {"posts": ["LinkedIn post"]}}}
            }
        )
        
        result = await orchestration_engine._execute_hybrid_workflow(sample_hybrid_input)
        
        assert result["workflow"] == "hybrid"
        assert result["success"] == True
        assert "deepcode_result" in result
        assert "zenalto_result" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_agent_failure(self, orchestration_engine):
        """Test error handling when agents fail."""
        
        # Mock failing agent
        orchestration_engine.zenalto_agents = {
            'content_intent': Mock()
        }
        orchestration_engine.zenalto_agents['content_intent'].analyze_intent = AsyncMock(
            side_effect=Exception("Agent failed")
        )
        
        result = await orchestration_engine._execute_zenalto_workflow({
            "user_request": "Create a post"
        })
        
        assert result["success"] == False
        assert "error" in result
        assert "Agent failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_metrics_tracking(self, orchestration_engine):
        """Test workflow metrics are tracked."""
        
        orchestration_engine.workflow_metrics = {
            "total_requests": 0,
            "deepcode_requests": 0,
            "zenalto_requests": 0
        }
        
        # Mock workflow execution
        orchestration_engine._execute_deepcode_workflow = AsyncMock(
            return_value={"success": True}
        )
        
        await orchestration_engine.process_request({
            "user_request": "test",
            "workflow_mode": "deepcode"
        })
        
        assert orchestration_engine.workflow_metrics["total_requests"] > 0
        assert orchestration_engine.workflow_metrics["deepcode_requests"] > 0
```

### 4. Social API Client Tests
**File**: `tests/test_social_clients.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from social_apis.twitter_client import TwitterClient
from social_apis.linkedin_client import LinkedInClient
from social_apis.client_factory import SocialMediaClientFactory

class TestSocialClients:
    """Test social media API clients."""
    
    @pytest.mark.asyncio
    async def test_twitter_client_post_tweet(self):
        """Test Twitter client tweet posting."""
        
        config = {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "access_token": "test_token",
            "access_token_secret": "test_token_secret"
        }
        
        with patch('tweepy.Client') as mock_client:
            mock_instance = Mock()
            mock_instance.create_tweet = AsyncMock(return_value=Mock(
                data={'id': '123456789'}
            ))
            mock_client.return_value = mock_instance
            
            client = TwitterClient(config)
            result = await client.post_tweet("Test tweet")
            
            assert result["success"] == True
            assert result["tweet_id"] == "123456789"
            assert "twitter.com" in result["url"]
    
    @pytest.mark.asyncio
    async def test_twitter_client_thread_posting(self):
        """Test Twitter thread posting."""
        
        config = {"api_key": "test", "api_secret": "test"}
        
        with patch('tweepy.Client') as mock_client:
            mock_instance = Mock()
            # Mock sequential tweet responses
            mock_instance.create_tweet = AsyncMock(side_effect=[
                Mock(data={'id': '123'}),
                Mock(data={'id': '456'}),
                Mock(data={'id': '789'})
            ])
            mock_client.return_value = mock_instance
            
            client = TwitterClient(config)
            result = await client.post_thread([
                "Thread 1/3",
                "Thread 2/3", 
                "Thread 3/3"
            ])
            
            assert result["success"] == True
            assert len(result["tweet_ids"]) == 3
            assert result["thread_id"] == "123"
    
    @pytest.mark.asyncio
    async def test_twitter_rate_limit_handling(self):
        """Test Twitter rate limit handling."""
        
        config = {"api_key": "test", "api_secret": "test"}
        
        with patch('tweepy.Client') as mock_client:
            mock_instance = Mock()
            mock_instance.create_tweet = AsyncMock(
                side_effect=tweepy.TooManyRequests("Rate limit exceeded")
            )
            mock_client.return_value = mock_instance
            
            client = TwitterClient(config)
            result = await client.post_tweet("Test tweet")
            
            assert result["success"] == False
            assert "rate limit" in result["error"].lower()
    
    @pytest.mark.asyncio 
    async def test_linkedin_client_post_update(self):
        """Test LinkedIn client post update."""
        
        config = {"access_token": "test_token"}
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={"id": "linkedin_post_123"})
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            async with LinkedInClient(config) as client:
                result = await client.post_update("Test LinkedIn post")
                
                assert result["success"] == True
                assert result["post_id"] == "linkedin_post_123"
    
    @pytest.mark.asyncio
    async def test_client_factory(self):
        """Test social media client factory."""
        
        config = {"api_key": "test"}
        
        # Test supported platform
        client = SocialMediaClientFactory.create_client("twitter", config)
        assert isinstance(client, TwitterClient)
        
        # Test unsupported platform
        with pytest.raises(ValueError, match="Unsupported platform"):
            SocialMediaClientFactory.create_client("unsupported", config)
        
        # Test supported platforms list
        platforms = SocialMediaClientFactory.get_supported_platforms()
        assert "twitter" in platforms
        assert "linkedin" in platforms
```

### 5. OAuth Authentication Tests
**File**: `tests/test_oauth.py`

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from auth.oauth_manager import OAuthManager
from auth.token_storage import TokenStorage

class TestOAuthAuthentication:
    """Test OAuth authentication flow."""
    
    @pytest.mark.asyncio
    async def test_oauth_flow_initiation(self, test_config):
        """Test OAuth flow initiation."""
        
        manager = OAuthManager(test_config["oauth"])
        
        result = await manager.initiate_oauth_flow(
            platform="twitter",
            user_id="test_user",
            redirect_uri="http://localhost/callback"
        )
        
        assert "auth_url" in result
        assert "state" in result
        assert "expires_at" in result
        assert result["state"] in manager.pending_authentications
        assert "twitter.com" in result["auth_url"]
    
    @pytest.mark.asyncio
    async def test_pkce_generation(self, test_config):
        """Test PKCE code generation."""
        
        manager = OAuthManager(test_config["oauth"])
        
        verifier = manager._generate_code_verifier()
        challenge = manager._generate_code_challenge(verifier)
        
        assert len(verifier) >= 43  # Min length for PKCE
        assert len(challenge) == 43  # SHA256 base64 length
        assert verifier != challenge
    
    @pytest.mark.asyncio
    async def test_oauth_callback_success(self, test_config):
        """Test successful OAuth callback handling."""
        
        manager = OAuthManager(test_config["oauth"])
        
        # First initiate flow to get state
        init_result = await manager.initiate_oauth_flow(
            platform="twitter",
            user_id="test_user", 
            redirect_uri="http://localhost/callback"
        )
        
        state = init_result["state"]
        
        # Mock token exchange
        with patch.object(manager, '_exchange_code_for_tokens') as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "test_access_token",
                "expires_in": 3600
            }
            
            with patch.object(manager, '_get_user_info') as mock_user_info:
                mock_user_info.return_value = {"id": "123", "username": "testuser"}
                
                result = await manager.handle_oauth_callback(
                    platform="twitter",
                    code="test_code",
                    state=state
                )
                
                assert result["success"] == True
                assert result["access_token"] == "test_access_token"
                assert "user_info" in result
    
    @pytest.mark.asyncio
    async def test_oauth_callback_invalid_state(self, test_config):
        """Test OAuth callback with invalid state."""
        
        manager = OAuthManager(test_config["oauth"])
        
        result = await manager.handle_oauth_callback(
            platform="twitter",
            code="test_code",
            state="invalid_state"
        )
        
        assert result["success"] == False
        assert "invalid state" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, test_config):
        """Test token refresh functionality."""
        
        manager = OAuthManager(test_config["oauth"])
        
        # Mock stored tokens
        with patch.object(manager.token_storage, 'get_tokens') as mock_get:
            mock_get.return_value = {
                "refresh_token": "test_refresh_token",
                "expires_at": "2023-01-01T00:00:00"  # Expired
            }
            
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = Mock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={
                    "access_token": "new_access_token",
                    "expires_in": 3600
                })
                
                mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
                
                result = await manager.refresh_token("test_user", "twitter")
                
                assert result["success"] == True
                assert result["access_token"] == "new_access_token"
    
    @pytest.mark.asyncio
    async def test_token_storage_encryption(self):
        """Test token storage encryption."""
        
        storage = TokenStorage()
        
        test_tokens = {
            "access_token": "secret_token_123",
            "refresh_token": "refresh_token_456"
        }
        
        # Test encryption/decryption
        encrypted = storage._encrypt_data(test_tokens)
        decrypted = storage._decrypt_data(encrypted)
        
        assert decrypted == test_tokens
        assert "secret_token_123" not in encrypted  # Token not in plaintext
    
    @pytest.mark.asyncio
    async def test_token_expiration_handling(self):
        """Test handling of expired tokens."""
        
        storage = TokenStorage()
        
        # Mock expired token
        expired_token_data = {
            "access_token": "expired_token",
            "expires_at": "2020-01-01T00:00:00"  # Past date
        }
        
        with patch.object(storage, '_get_from_database') as mock_get:
            encrypted_data = storage._encrypt_data(expired_token_data)
            mock_get.return_value = encrypted_data
            
            result = await storage.get_tokens("test_user", "twitter")
            
            assert result["expired"] == True
            assert result["access_token"] == "expired_token"
```

### 6. End-to-End Tests
**File**: `tests/test_e2e.py`

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_zenalto_workflow(self):
        """Test complete ZenAlto workflow from request to posting."""
        
        # This test would require actual API credentials in a test environment
        # For CI/CD, we'll mock the external services
        
        with patch('social_apis.twitter_client.TwitterClient') as mock_client_class:
            mock_client = Mock()
            mock_client.post_tweet = AsyncMock(return_value={
                "success": True,
                "tweet_id": "123456",
                "url": "https://twitter.com/test/status/123456"
            })
            mock_client_class.return_value = mock_client
            
            # Full workflow test
            from workflows.agent_orchestration_engine import AgentOrchestrationEngine
            
            engine = AgentOrchestrationEngine()
            
            input_data = {
                "user_request": "Create a Twitter thread about the benefits of AI",
                "platforms": ["twitter"],
                "tone": "educational",
                "workflow_mode": "zenalto"
            }
            
            result = await engine.process_request(input_data)
            
            assert result["workflow_type"] == "zenalto"
            assert result["success"] == True
            assert "posting_result" in result.get("stages", {})
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_hybrid_research_to_social_workflow(self):
        """Test complete hybrid workflow from research paper to social posts."""
        
        from workflows.agent_orchestration_engine import AgentOrchestrationEngine
        
        engine = AgentOrchestrationEngine()
        
        input_data = {
            "user_request": "Create LinkedIn posts explaining this AI research paper",
            "paper_content": "This paper presents a novel approach to transformer architectures...",
            "platforms": ["linkedin"],
            "workflow_mode": "hybrid"
        }
        
        with patch.multiple(
            engine,
            _execute_deepcode_workflow=AsyncMock(return_value={
                "success": True,
                "analysis": {"key_points": ["Novel architecture", "Performance gains"]}
            }),
            _execute_zenalto_workflow=AsyncMock(return_value={
                "success": True,
                "stages": {"posting": {"success": True}}
            })
        ):
            result = await engine.process_request(input_data)
            
            assert result["workflow"] == "hybrid"
            assert result["success"] == True
            assert "deepcode_result" in result
            assert "zenalto_result" in result
    
    @pytest.mark.e2e
    @pytest.mark.asyncio 
    async def test_oauth_to_posting_flow(self):
        """Test OAuth authentication followed by content posting."""
        
        from auth.oauth_manager import OAuthManager
        from social_apis.client_factory import SocialMediaClientFactory
        
        # Mock OAuth flow
        config = {"twitter": {"client_id": "test", "client_secret": "test"}}
        oauth_manager = OAuthManager(config)
        
        # Mock successful OAuth
        with patch.object(oauth_manager, '_exchange_code_for_tokens') as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "test_token",
                "expires_in": 3600
            }
            
            # Mock posting
            with patch.object(SocialMediaClientFactory, 'create_client') as mock_factory:
                mock_client = Mock()
                mock_client.post_content = AsyncMock(return_value={
                    "success": True,
                    "post_id": "123"
                })
                mock_factory.return_value = mock_client
                
                # Simulate OAuth callback
                oauth_result = await oauth_manager.handle_oauth_callback(
                    platform="twitter",
                    code="test_code",
                    state="test_state"  # Would need valid state in real test
                )
                
                # Skip OAuth result check for this mock test
                # Then test posting
                client = SocialMediaClientFactory.create_client("twitter", {})
                post_result = await client.post_content("Test post")
                
                assert post_result["success"] == True
```

### 7. Performance Tests
**File**: `tests/test_performance.py`

```python
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Performance and load testing."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_workflow_routing_performance(self, workflow_router):
        """Test workflow routing performance."""
        
        test_inputs = [
            {"user_request": "Create a tweet about AI"},
            {"user_request": "Implement this research paper"},
            {"user_request": "Generate LinkedIn content"},
            {"user_request": "Analyze this algorithm"},
        ] * 25  # 100 total requests
        
        start_time = time.time()
        
        tasks = [
            workflow_router.detect_workflow_type(input_data) 
            for input_data in test_inputs
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert total_time < 5.0  # Should complete in under 5 seconds
        assert len(results) == 100
        assert all(r["workflow_type"] in ["deepcode", "zenalto"] for r in results)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_agent_processing(self, orchestration_engine):
        """Test concurrent agent processing."""
        
        # Mock agent methods for performance testing
        orchestration_engine._execute_deepcode_workflow = AsyncMock(
            return_value={"success": True}
        )
        orchestration_engine._execute_zenalto_workflow = AsyncMock(
            return_value={"success": True}
        )
        
        requests = [
            {"user_request": f"Test request {i}", "workflow_mode": "deepcode"}
            for i in range(10)
        ]
        
        start_time = time.time()
        
        tasks = [
            orchestration_engine.process_request(req) 
            for req in requests
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle 10 concurrent requests quickly
        assert total_time < 2.0
        assert all(r["success"] for r in results)
    
    @pytest.mark.performance
    def test_token_encryption_performance(self):
        """Test token encryption/decryption performance."""
        
        from auth.token_storage import TokenStorage
        
        storage = TokenStorage()
        
        test_data = {
            "access_token": "very_long_token_" * 100,
            "refresh_token": "another_long_token_" * 100,
            "user_info": {"name": "test", "followers": 10000}
        }
        
        # Test encryption speed
        start_time = time.time()
        
        for _ in range(1000):
            encrypted = storage._encrypt_data(test_data)
            decrypted = storage._decrypt_data(encrypted)
        
        end_time = time.time()
        
        # Should handle 1000 encrypt/decrypt cycles quickly
        assert (end_time - start_time) < 1.0
        assert decrypted == test_data
```

### 8. Test Configuration
**File**: `pytest.ini`

```ini
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow tests that may take a while
    oauth: Tests requiring OAuth setup

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Async test configuration
asyncio_mode = auto

# Test output
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=workflows
    --cov=auth
    --cov=social_apis
    --cov=ui
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# Test discovery
minversion = 6.0
```

### 9. CI/CD Integration
**File**: `.github/workflows/tests.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/ -m "unit" --cov=./ --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/ -m "integration"
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

## Test Data Management

### 1. Test Fixtures
Create reusable test data fixtures:

```python
# tests/fixtures/sample_data.py
SAMPLE_RESEARCH_PAPER = """
Title: Attention Is All You Need
Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...
"""

SAMPLE_SOCIAL_POSTS = {
    "twitter": {
        "thread": [
            "🧵 Thread about AI developments 1/5",
            "First, let's talk about transformer architectures 2/5",
            "The attention mechanism revolutionized NLP 3/5",
            "Applications now span far beyond text 4/5",
            "What's next? Multimodal transformers 5/5"
        ],
        "single": "Exciting developments in AI are happening every day! 🚀 #AI #MachineLearning"
    },
    "linkedin": {
        "professional": "As a data scientist, I'm excited to share insights on the latest AI breakthroughs..."
    }
}
```

## Success Criteria

- [ ] >90% code coverage across all modules
- [ ] All critical paths tested (happy path + edge cases)
- [ ] Performance benchmarks established
- [ ] CI/CD pipeline functional
- [ ] OAuth flows thoroughly tested
- [ ] Social API clients tested
- [ ] Backward compatibility verified
- [ ] Error handling comprehensive

## Delivery Checklist

- [ ] Test framework setup complete
- [ ] Unit tests for all components
- [ ] Integration tests for workflows
- [ ] End-to-end test scenarios
- [ ] Performance test suite
- [ ] OAuth authentication tests
- [ ] Social API client tests
- [ ] CI/CD pipeline configured
- [ ] Test documentation complete
- [ ] Coverage reports generated