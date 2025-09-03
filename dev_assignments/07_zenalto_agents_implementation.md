# Development Assignment #7: ZenAlto Agents Implementation

## Priority: 🔥 HIGH - Week 2

## Objective
Implement the 5 missing ZenAlto agents required for complete social media workflow functionality. Each agent should follow the existing agent pattern and integrate with the MCP framework.

## Background
Only `ContentIntentAgent` is currently implemented. We need 5 additional specialized agents to complete the social media management pipeline.

## Deliverables

Create the following agent files in `workflows/agents/`:

### 1. Content Strategy Agent
**File**: `workflows/agents/content_strategy_agent.py`

```python
class ContentStrategyAgent:
    """
    Develops comprehensive content strategies based on intent analysis.
    
    Responsibilities:
    - Campaign planning and structuring
    - Platform-specific strategy development
    - Content calendar optimization
    - Audience targeting recommendations
    - Hashtag and keyword strategies
    """
    
    def __init__(self, mcp_agent: Agent, logger, config: Optional[Dict] = None):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.config = config or {}
        self.strategy_templates = self._load_strategy_templates()
    
    async def create_strategy(
        self,
        intent_analysis: Dict[str, Any],
        target_platforms: List[str],
        scheduling_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create comprehensive content strategy.
        
        Returns:
        {
            "strategy_type": "campaign|single|series",
            "platforms": {
                "twitter": {"post_count": 5, "thread": true, "optimal_times": [...]},
                "linkedin": {"post_count": 1, "article": false, "optimal_times": [...]}
            },
            "content_themes": ["education", "engagement", "promotion"],
            "hashtag_strategy": {
                "primary": ["#AI", "#MachineLearning"],
                "secondary": ["#Tech", "#Innovation"],
                "trending": ["#AITrends2024"]
            },
            "audience_segments": ["developers", "business leaders"],
            "success_metrics": {
                "target_engagement": 5.2,
                "target_reach": 10000
            },
            "timeline": {
                "start": "2024-01-15T09:00:00Z",
                "end": "2024-01-22T17:00:00Z",
                "posts": [...]
            }
        }
        """
    
    async def optimize_for_platform(
        self,
        base_strategy: Dict,
        platform: str
    ) -> Dict[str, Any]:
        """Optimize strategy for specific platform requirements."""
    
    async def analyze_competitor_strategies(
        self,
        topic: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Analyze competitor content strategies for insights."""
    
    async def generate_content_calendar(
        self,
        strategy: Dict,
        duration_days: int
    ) -> List[Dict[str, Any]]:
        """Generate detailed content calendar from strategy."""
```

### 2. Content Generation Agent
**File**: `workflows/agents/content_generation_agent.py`

```python
class ContentGenerationAgent:
    """
    Generates optimized social media content based on strategy.
    
    Responsibilities:
    - Platform-specific content creation
    - Tone and style adaptation
    - Media recommendations
    - A/B testing variants
    - Content optimization
    """
    
    def __init__(self, mcp_agent: Agent, logger, config: Optional[Dict] = None):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.config = config or {}
        self.platform_limits = self._load_platform_limits()
    
    async def generate(
        self,
        strategy: Dict[str, Any],
        tone: str = "professional",
        optimization_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate content for all platforms in strategy.
        
        Returns:
        {
            "content": {
                "twitter": {
                    "posts": [
                        {
                            "text": "🚀 Exciting AI breakthrough...",
                            "media": ["image_url"],
                            "hashtags": ["#AI", "#Innovation"],
                            "thread_position": 1,
                            "character_count": 245
                        }
                    ],
                    "optimizations": ["emoji_usage", "hashtag_placement"]
                },
                "linkedin": {
                    "posts": [
                        {
                            "text": "Professional insights on AI...",
                            "media": [],
                            "hashtags": ["#ArtificialIntelligence"],
                            "format": "article",
                            "reading_time": "3 min"
                        }
                    ]
                }
            },
            "variants": {
                "a_b_testing": true,
                "variants_generated": 2
            },
            "quality_scores": {
                "engagement_potential": 8.5,
                "clarity": 9.0,
                "platform_fit": 9.5
            }
        }
        """
    
    async def adapt_tone(
        self,
        content: str,
        from_tone: str,
        to_tone: str
    ) -> str:
        """Adapt content tone (professional, casual, humorous, educational)."""
    
    async def generate_variants(
        self,
        base_content: str,
        num_variants: int = 3
    ) -> List[str]:
        """Generate A/B testing variants."""
    
    async def optimize_for_engagement(
        self,
        content: Dict,
        platform: str,
        audience_data: Optional[Dict] = None
    ) -> Dict:
        """Optimize content for maximum engagement."""
    
    async def validate_content(
        self,
        content: Dict,
        platform: str
    ) -> Tuple[bool, List[str]]:
        """Validate content meets platform requirements."""
```

### 3. Social Content Parser
**File**: `workflows/agents/social_content_parser.py`

```python
class SocialContentParser:
    """
    Parses and analyzes existing social media content.
    
    Responsibilities:
    - Extract content from various sources
    - Analyze competitor posts
    - Identify trending topics
    - Content repurposing
    - Performance pattern analysis
    """
    
    def __init__(self, mcp_agent: Agent, logger, config: Optional[Dict] = None):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.config = config or {}
        self.parsers = self._init_parsers()
    
    async def parse_content(
        self,
        source: str,
        content_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Parse content from various sources.
        
        Args:
            source: URL, file path, or raw content
            content_type: "url", "file", "text", or "auto"
        
        Returns:
        {
            "content_type": "article|post|thread|video",
            "platform": "twitter|linkedin|blog",
            "main_content": "...",
            "metadata": {
                "author": "...",
                "date": "...",
                "engagement": {...}
            },
            "key_points": [...],
            "sentiment": "positive|neutral|negative",
            "topics": ["AI", "technology"],
            "repurpose_potential": {
                "twitter": 0.9,
                "linkedin": 0.8,
                "instagram": 0.6
            }
        }
        """
    
    async def analyze_competitor_content(
        self,
        competitor_handles: List[str],
        platforms: List[str],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze competitor social media strategies."""
    
    async def identify_trending_topics(
        self,
        industry: str,
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify current trending topics in industry."""
    
    async def extract_best_practices(
        self,
        high_performing_posts: List[Dict]
    ) -> Dict[str, Any]:
        """Extract patterns from high-performing content."""
    
    async def suggest_repurposing(
        self,
        original_content: Dict,
        target_platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest how to repurpose content across platforms."""
```

### 4. Analytics Agent
**File**: `workflows/agents/analytics_agent.py`

```python
class AnalyticsAgent:
    """
    Tracks and analyzes social media performance metrics.
    
    Responsibilities:
    - Performance tracking setup
    - Engagement analysis
    - ROI calculation
    - Trend identification
    - Predictive analytics
    """
    
    def __init__(self, mcp_agent: Agent, logger, config: Optional[Dict] = None):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.config = config or {}
        self.metrics_definitions = self._load_metrics_definitions()
    
    async def setup_tracking(
        self,
        post_ids: List[str],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Setup analytics tracking for posts.
        
        Returns:
        {
            "tracking_id": "uuid",
            "posts_tracked": [...],
            "metrics_to_track": [
                "impressions", "engagement_rate", "clicks",
                "shares", "comments", "sentiment"
            ],
            "tracking_frequency": "hourly",
            "dashboard_url": "...",
            "alerts_configured": [
                {"metric": "engagement_rate", "threshold": 5.0}
            ]
        }
        """
    
    async def analyze_performance(
        self,
        post_ids: List[str],
        time_range: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze post performance.
        
        Returns:
        {
            "overall_performance": {
                "engagement_rate": 4.5,
                "total_reach": 15000,
                "total_impressions": 25000,
                "roi": 3.2
            },
            "by_platform": {
                "twitter": {...},
                "linkedin": {...}
            },
            "top_performing": [...],
            "insights": [
                "Posts with images get 2x more engagement",
                "Best posting time is 9 AM EST"
            ],
            "recommendations": [...]
        }
        """
    
    async def predict_performance(
        self,
        content: Dict,
        historical_data: Optional[Dict] = None
    ) -> Dict[str, float]:
        """Predict content performance based on historical data."""
    
    async def generate_report(
        self,
        analytics_data: Dict,
        format: str = "summary"
    ) -> Dict[str, Any]:
        """Generate analytics report (summary, detailed, executive)."""
    
    async def identify_trends(
        self,
        historical_data: List[Dict],
        time_period: str = "30d"
    ) -> List[Dict[str, Any]]:
        """Identify performance trends and patterns."""
```

### 5. Scheduling Agent
**File**: `workflows/agents/scheduling_agent.py`

```python
class SchedulingAgent:
    """
    Manages optimal content scheduling and posting queues.
    
    Responsibilities:
    - Optimal timing calculation
    - Queue management
    - Conflict resolution
    - Bulk scheduling
    - Calendar integration
    """
    
    def __init__(self, mcp_agent: Agent, logger, config: Optional[Dict] = None):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.config = config or {}
        self.timezone_handler = self._init_timezone_handler()
    
    async def schedule(
        self,
        content: Dict[str, Any],
        schedule_time: Optional[str] = None,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule content for posting.
        
        Returns:
        {
            "scheduled_posts": [
                {
                    "post_id": "uuid",
                    "platform": "twitter",
                    "scheduled_time": "2024-01-15T09:00:00Z",
                    "status": "queued",
                    "queue_position": 3
                }
            ],
            "conflicts_resolved": [],
            "optimization_applied": true,
            "estimated_reach": {
                "total": 25000,
                "by_platform": {...}
            }
        }
        """
    
    async def find_optimal_times(
        self,
        platforms: List[str],
        content_type: str,
        target_audience: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """Find optimal posting times for each platform."""
    
    async def manage_queue(
        self,
        action: str = "view"  # view, reorder, pause, resume
    ) -> Dict[str, Any]:
        """Manage the posting queue."""
    
    async def bulk_schedule(
        self,
        posts: List[Dict],
        distribution: str = "even"  # even, optimal, manual
    ) -> List[Dict[str, Any]]:
        """Schedule multiple posts with smart distribution."""
    
    async def handle_conflicts(
        self,
        new_post: Dict,
        existing_schedule: List[Dict]
    ) -> Dict[str, Any]:
        """Resolve scheduling conflicts."""
```

## Common Implementation Requirements

### 1. Base Agent Pattern

All agents should follow this pattern:

```python
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from mcp_agent.agents.agent import Agent
import logging

class [AgentName]:
    """Comprehensive docstring."""
    
    def __init__(
        self,
        mcp_agent: Agent,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        
        # Initialize agent-specific components
        self._initialize()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "model": "claude-3.5-sonnet",
            "max_tokens": 2000,
            "temperature": 0.7
        }
    
    def _initialize(self):
        """Initialize agent-specific resources."""
        pass
    
    async def _call_mcp_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Any:
        """Wrapper for MCP tool calls."""
        try:
            result = await self.mcp_agent.call_tool(tool_name, params)
            return result
        except Exception as e:
            self.logger.error(f"MCP tool call failed: {e}")
            raise
```

### 2. Error Handling

Each agent must implement robust error handling:

```python
async def method_with_error_handling(self, params):
    try:
        # Main logic
        result = await self._perform_operation(params)
        
        # Validate result
        if not self._validate_result(result):
            raise ValueError("Invalid result format")
        
        return result
        
    except asyncio.TimeoutError:
        self.logger.error("Operation timed out")
        return self._get_timeout_fallback()
        
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        # Return graceful fallback
        return self._get_error_fallback(str(e))
```

### 3. Logging Standards

Use structured logging:

```python
self.logger.info(f"[{self.__class__.__name__}] Starting operation", 
                 extra={"operation": "analyze", "params": params})

self.logger.debug(f"[{self.__class__.__name__}] Intermediate result",
                  extra={"result_size": len(result)})

self.logger.error(f"[{self.__class__.__name__}] Operation failed",
                  extra={"error": str(e), "traceback": traceback.format_exc()})
```

### 4. Testing Requirements

Create test files for each agent:

```python
# tests/test_[agent_name].py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from workflows.agents.[agent_name] import [AgentClass]

@pytest.fixture
def mock_mcp_agent():
    agent = Mock()
    agent.call_tool = AsyncMock()
    return agent

@pytest.fixture
def agent(mock_mcp_agent):
    return [AgentClass](mock_mcp_agent, logger=Mock())

@pytest.mark.asyncio
async def test_basic_functionality(agent):
    # Test basic agent functionality
    result = await agent.main_method(test_params)
    assert result["success"] == True

@pytest.mark.asyncio
async def test_error_handling(agent):
    # Test error scenarios
    agent.mcp_agent.call_tool.side_effect = Exception("Test error")
    result = await agent.main_method(test_params)
    assert result["success"] == False
```

## Integration Requirements

### 1. MCP Tool Integration

Each agent should use appropriate MCP tools:

```python
# Content Strategy Agent
await self.mcp_agent.call_tool("content_intent_analyze", {...})
await self.mcp_agent.call_tool("social_media_check_status", {...})

# Content Generation Agent  
await self.mcp_agent.call_tool("social_media_suggest_content", {...})

# Analytics Agent
await self.mcp_agent.call_tool("social_media_get_analytics", {...})

# Scheduling Agent
await self.mcp_agent.call_tool("social_media_schedule_post", {...})
```

### 2. Prompt Templates

Add prompts to `prompts/social_prompts.py`:

```python
CONTENT_STRATEGY_PROMPT = """
Develop a comprehensive content strategy based on:
Intent: {intent_analysis}
Platforms: {platforms}
Goals: {business_goals}

Provide a detailed strategy including:
1. Content themes and pillars
2. Platform-specific approaches
3. Posting frequency and timing
4. Hashtag strategy
5. Success metrics
"""

# Add similar prompts for each agent
```

### 3. Configuration

Add agent configs to `mcp_agent.config.yaml`:

```yaml
zenalto_agents:
  content_strategy:
    enabled: true
    model: "claude-3.5-sonnet"
    max_tokens: 3000
    temperature: 0.8
    
  content_generation:
    enabled: true
    model: "claude-3.5-sonnet"
    max_tokens: 4000
    temperature: 0.9
    
  # Continue for each agent...
```

## Performance Requirements

1. **Async Operations**: All I/O operations must be async
2. **Timeout Handling**: 30-second timeout for all operations
3. **Batch Processing**: Support batch operations where applicable
4. **Caching**: Implement caching for repeated operations
5. **Resource Cleanup**: Proper cleanup in `__del__` methods

## Success Criteria

- [ ] All 5 agents implemented with core functionality
- [ ] Each agent has >80% test coverage
- [ ] Integration with MCP tools working
- [ ] Error handling implemented
- [ ] Documentation complete
- [ ] Performance meets requirements

## Delivery Checklist

- [ ] 5 agent implementation files created
- [ ] 5 test files created
- [ ] Prompts added to social_prompts.py
- [ ] Configuration updated
- [ ] Integration tested with orchestration engine
- [ ] Documentation included in each file