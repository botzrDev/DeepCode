# ZENALTO Integration Assignment #2: Agent Implementation

## Objective
Implement the core ZENALTO agents that handle social media content creation, strategy, and analytics while integrating seamlessly with the existing DeepCode agent architecture.

## Background
ZENALTO requires specialized agents for social media management. These agents will work alongside existing DeepCode agents, following the same patterns and interfaces but focusing on social media workflows.

## Key Requirements

### 1. Agent Consistency
- Follow existing DeepCode agent patterns and interfaces
- Use same async/await patterns as existing agents
- Integrate with existing MCP framework
- Maintain same logging and error handling standards

### 2. Social Media Specialization
- Platform-specific content optimization
- Intent analysis for conversational input
- Strategy planning for multi-platform campaigns
- Analytics and performance tracking

## Agent Implementations Required

### 1. Content Intent Agent

**File**: `workflows/agents/content_intent_agent.py`

```python
"""
Content Intent Analysis Agent for ZENALTO

Analyzes user requests to understand social media content goals, target platforms,
audience demographics, and content requirements.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp_agent.agents.agent import Agent
from prompts.social_prompts import (
    CONTENT_INTENT_ANALYSIS_PROMPT,
    PLATFORM_DETECTION_PROMPT,
    AUDIENCE_ANALYSIS_PROMPT
)

class ContentIntentAgent:
    def __init__(self, mcp_agent: Agent, logger: logging.Logger):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.name = "content_intent_agent"
    
    async def analyze_content_intent(
        self,
        user_request: str,
        conversation_history: List[Dict[str, Any]] = None,
        platform_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for intent analysis
        
        Args:
            user_request: Natural language content request
            conversation_history: Previous conversation context
            platform_context: Current platform connection status
            
        Returns:
            Structured intent analysis
        """
        self.logger.info(f"Analyzing content intent for request: {user_request[:100]}...")
        
        try:
            # Step 1: Basic intent parsing
            basic_intent = await self._parse_basic_intent(user_request)
            
            # Step 2: Platform detection
            platforms = await self._detect_target_platforms(
                user_request, 
                platform_context
            )
            
            # Step 3: Audience analysis
            audience = await self._analyze_target_audience(
                user_request,
                platforms,
                conversation_history
            )
            
            # Step 4: Content classification
            content_classification = await self._classify_content_type(
                user_request,
                platforms
            )
            
            # Step 5: Context integration
            context_analysis = await self._integrate_context(
                user_request,
                conversation_history,
                basic_intent
            )
            
            # Compile final analysis
            intent_analysis = {
                "intent_summary": basic_intent["summary"],
                "platforms": platforms,
                "audience": audience,
                "content_type": content_classification["type"],
                "tone": content_classification["tone"],
                "topics": basic_intent["topics"],
                "urgency": context_analysis["urgency"],
                "additional_requirements": context_analysis["requirements"],
                "confidence_score": self._calculate_confidence([
                    basic_intent, platforms, audience, content_classification
                ]),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Intent analysis completed with confidence {intent_analysis['confidence_score']}")
            return intent_analysis
            
        except Exception as e:
            self.logger.error(f"Error in content intent analysis: {str(e)}")
            return {
                "error": str(e),
                "intent_summary": "Failed to analyze intent",
                "platforms": [],
                "confidence_score": 0.0,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _parse_basic_intent(self, user_request: str) -> Dict[str, Any]:
        """Extract basic intent and topics from user request"""
        
        prompt = CONTENT_INTENT_ANALYSIS_PROMPT.format(
            user_request=user_request
        )
        
        response = await self.mcp_agent.call_tool(
            "content_intent_analysis",
            {"prompt": prompt, "user_request": user_request}
        )
        
        return json.loads(response)
    
    async def _detect_target_platforms(
        self,
        user_request: str,
        platform_context: Dict[str, Any] = None
    ) -> List[str]:
        """Detect which social media platforms are targeted"""
        
        platform_context = platform_context or {}
        
        prompt = PLATFORM_DETECTION_PROMPT.format(
            user_request=user_request,
            connected_platforms=list(platform_context.keys())
        )
        
        response = await self.mcp_agent.call_tool(
            "platform_detection",
            {"prompt": prompt, "user_request": user_request}
        )
        
        detected_platforms = json.loads(response).get("platforms", [])
        
        # Filter by connected platforms if specified
        if platform_context:
            connected = [p for p, status in platform_context.items() 
                        if status.get("connected", False)]
            detected_platforms = [p for p in detected_platforms if p in connected]
        
        return detected_platforms or ["twitter"]  # Default fallback
    
    async def _analyze_target_audience(
        self,
        user_request: str,
        platforms: List[str],
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze target audience demographics and characteristics"""
        
        conversation_history = conversation_history or []
        
        prompt = AUDIENCE_ANALYSIS_PROMPT.format(
            user_request=user_request,
            platforms=", ".join(platforms),
            conversation_context=json.dumps(conversation_history[-5:])  # Last 5 messages
        )
        
        response = await self.mcp_agent.call_tool(
            "audience_analysis",
            {"prompt": prompt, "user_request": user_request}
        )
        
        return json.loads(response)
    
    async def _classify_content_type(
        self,
        user_request: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Classify the type and tone of requested content"""
        
        # Platform-specific content type mapping
        platform_content_types = {
            "twitter": ["tweet", "thread", "poll", "reply"],
            "linkedin": ["post", "article", "update", "question"],
            "instagram": ["post", "story", "reel", "carousel"],
            "facebook": ["post", "story", "event", "poll"],
            "youtube": ["video", "short", "community_post"]
        }
        
        # Analyze content type based on request
        prompt = f"""
        Analyze this social media content request and classify it:
        
        Request: {user_request}
        Target Platforms: {', '.join(platforms)}
        
        Determine:
        1. Content type (post, article, thread, story, etc.)
        2. Appropriate tone (professional, casual, humorous, inspirational, etc.)
        3. Content format requirements
        
        Return as JSON: {{"type": "...", "tone": "...", "format": "..."}}
        """
        
        response = await self.mcp_agent.call_tool(
            "content_classification",
            {"prompt": prompt, "user_request": user_request}
        )
        
        return json.loads(response)
    
    async def _integrate_context(
        self,
        user_request: str,
        conversation_history: List[Dict[str, Any]] = None,
        basic_intent: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Integrate conversation context and determine urgency/requirements"""
        
        conversation_history = conversation_history or []
        basic_intent = basic_intent or {}
        
        # Analyze urgency indicators
        urgency_indicators = ["urgent", "asap", "now", "immediately", "quickly"]
        urgency = "high" if any(indicator in user_request.lower() 
                              for indicator in urgency_indicators) else "normal"
        
        # Extract additional requirements
        requirements = []
        if "hashtag" in user_request.lower():
            requirements.append("include_hashtags")
        if "image" in user_request.lower() or "photo" in user_request.lower():
            requirements.append("include_media")
        if "schedule" in user_request.lower():
            requirements.append("schedule_posting")
        if "analytics" in user_request.lower():
            requirements.append("track_performance")
        
        return {
            "urgency": urgency,
            "requirements": requirements,
            "context_integration": True
        }
    
    def _calculate_confidence(self, analysis_components: List[Dict]) -> float:
        """Calculate confidence score for the intent analysis"""
        
        # Simple confidence calculation based on successful components
        successful_components = sum(1 for component in analysis_components 
                                  if component and not component.get("error"))
        total_components = len(analysis_components)
        
        base_confidence = successful_components / total_components if total_components > 0 else 0
        
        # Adjust based on specific factors
        # This would be enhanced with ML models in production
        return min(base_confidence * 0.95, 0.95)  # Cap at 95%
    
    async def learn_user_preferences(
        self,
        user_id: str,
        intent_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Learn user preferences from historical intent analyses"""
        
        try:
            # Analyze patterns in user's content requests
            platform_preferences = {}
            tone_preferences = {}
            topic_patterns = []
            
            for intent in intent_history:
                # Platform usage patterns
                for platform in intent.get("platforms", []):
                    platform_preferences[platform] = platform_preferences.get(platform, 0) + 1
                
                # Tone preferences
                tone = intent.get("tone", "professional")
                tone_preferences[tone] = tone_preferences.get(tone, 0) + 1
                
                # Topic patterns
                topics = intent.get("topics", [])
                topic_patterns.extend(topics)
            
            # Calculate preferences
            preferences = {
                "preferred_platforms": sorted(platform_preferences.items(), 
                                            key=lambda x: x[1], reverse=True),
                "preferred_tone": max(tone_preferences.items(), 
                                    key=lambda x: x[1])[0] if tone_preferences else "professional",
                "common_topics": list(set(topic_patterns)),
                "user_id": user_id,
                "analysis_count": len(intent_history),
                "updated_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Updated preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error learning user preferences: {str(e)}")
            return {"error": str(e), "user_id": user_id}
```

### 2. Content Strategy Agent

**File**: `workflows/agents/content_strategy_agent.py`

```python
"""
Content Strategy Agent for ZENALTO

Plans optimal content distribution strategies, timing, and platform-specific adaptations
based on intent analysis and platform best practices.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

class ContentStrategyAgent:
    def __init__(self, mcp_agent: Agent, logger: logging.Logger):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.name = "content_strategy_agent"
        
        # Platform-specific best practices
        self.platform_strategies = {
            "twitter": {
                "optimal_times": [9, 12, 15, 18],  # Hours
                "max_length": 280,
                "hashtag_limit": 2,
                "tone_preferences": ["casual", "engaging", "timely"]
            },
            "linkedin": {
                "optimal_times": [8, 12, 17],
                "max_length": 3000,
                "hashtag_limit": 5,
                "tone_preferences": ["professional", "insightful", "industry-focused"]
            },
            "instagram": {
                "optimal_times": [11, 14, 17, 20],
                "max_length": 2200,
                "hashtag_limit": 30,
                "tone_preferences": ["visual", "casual", "lifestyle"]
            }
        }
    
    async def plan_content_strategy(
        self,
        intent_analysis: Dict[str, Any],
        platform_preferences: Dict[str, Any] = None,
        user_analytics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Plan comprehensive content strategy based on intent analysis
        
        Args:
            intent_analysis: Results from ContentIntentAgent
            platform_preferences: User's platform preferences and settings
            user_analytics: Historical performance data
            
        Returns:
            Comprehensive content strategy
        """
        
        self.logger.info("Planning content strategy...")
        
        try:
            platforms = intent_analysis.get("platforms", [])
            content_type = intent_analysis.get("content_type", "post")
            audience = intent_analysis.get("audience", {})
            urgency = intent_analysis.get("urgency", "normal")
            
            # Step 1: Platform selection and prioritization
            platform_strategy = await self._optimize_platform_selection(
                platforms, audience, user_analytics
            )
            
            # Step 2: Timing optimization
            timing_strategy = await self._optimize_timing(
                platforms, urgency, user_analytics
            )
            
            # Step 3: Content adaptation strategy
            adaptation_strategy = await self._plan_content_adaptation(
                platforms, content_type, intent_analysis
            )
            
            # Step 4: Engagement optimization
            engagement_strategy = await self._plan_engagement_optimization(
                platforms, audience, intent_analysis
            )
            
            # Step 5: Performance prediction
            performance_prediction = await self._predict_performance(
                platform_strategy, adaptation_strategy, user_analytics
            )
            
            strategy = {
                "platform_strategy": platform_strategy,
                "timing_strategy": timing_strategy,
                "adaptation_strategy": adaptation_strategy,
                "engagement_strategy": engagement_strategy,
                "performance_prediction": performance_prediction,
                "execution_priority": self._determine_execution_priority(urgency, platforms),
                "success_metrics": self._define_success_metrics(platforms, intent_analysis),
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Content strategy planned for {len(platforms)} platforms")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error planning content strategy: {str(e)}")
            return {
                "error": str(e),
                "platform_strategy": {},
                "timing_strategy": {},
                "created_at": datetime.now().isoformat()
            }
    
    async def _optimize_platform_selection(
        self,
        platforms: List[str],
        audience: Dict[str, Any],
        user_analytics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize platform selection based on audience and performance data"""
        
        platform_scores = {}
        user_analytics = user_analytics or {}
        
        for platform in platforms:
            score = 0.5  # Base score
            
            # Audience alignment
            if platform in ["linkedin"] and "professional" in audience.get("type", "").lower():
                score += 0.3
            elif platform in ["instagram"] and "visual" in audience.get("preferences", []):
                score += 0.3
            elif platform in ["twitter"] and "tech" in audience.get("interests", []):
                score += 0.2
            
            # Historical performance
            if platform in user_analytics.get("platform_performance", {}):
                performance = user_analytics["platform_performance"][platform]
                avg_engagement = performance.get("avg_engagement_rate", 0)
                if avg_engagement > 0.05:  # 5% engagement rate
                    score += 0.2
                elif avg_engagement > 0.02:  # 2% engagement rate
                    score += 0.1
            
            platform_scores[platform] = min(score, 1.0)
        
        # Sort by priority
        sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "primary_platform": sorted_platforms[0][0] if sorted_platforms else "twitter",
            "platform_priorities": dict(sorted_platforms),
            "recommended_sequence": [p[0] for p in sorted_platforms]
        }
    
    async def _optimize_timing(
        self,
        platforms: List[str],
        urgency: str,
        user_analytics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Optimize posting timing for each platform"""
        
        user_analytics = user_analytics or {}
        current_time = datetime.now()
        
        timing_recommendations = {}
        
        for platform in platforms:
            platform_config = self.platform_strategies.get(platform, {})
            optimal_hours = platform_config.get("optimal_times", [12])
            
            if urgency == "high":
                # Post immediately or within 1 hour
                recommended_time = current_time + timedelta(minutes=5)
            else:
                # Find next optimal time
                current_hour = current_time.hour
                next_optimal = None
                
                for hour in optimal_hours:
                    if hour > current_hour:
                        next_optimal = current_time.replace(
                            hour=hour, minute=0, second=0, microsecond=0
                        )
                        break
                
                if not next_optimal:
                    # Next day, first optimal hour
                    next_optimal = (current_time + timedelta(days=1)).replace(
                        hour=optimal_hours[0], minute=0, second=0, microsecond=0
                    )
                
                recommended_time = next_optimal
            
            timing_recommendations[platform] = {
                "recommended_time": recommended_time.isoformat(),
                "optimal_hours": optimal_hours,
                "timezone": "UTC",  # This would be user-configurable
                "urgency_applied": urgency == "high"
            }
        
        return timing_recommendations
    
    async def _plan_content_adaptation(
        self,
        platforms: List[str],
        content_type: str,
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan how content should be adapted for each platform"""
        
        adaptations = {}
        
        for platform in platforms:
            platform_config = self.platform_strategies.get(platform, {})
            
            adaptation = {
                "max_length": platform_config.get("max_length", 1000),
                "hashtag_strategy": {
                    "limit": platform_config.get("hashtag_limit", 5),
                    "recommended_tags": await self._suggest_hashtags(platform, intent_analysis)
                },
                "tone_adaptation": self._adapt_tone(
                    intent_analysis.get("tone", "professional"),
                    platform_config.get("tone_preferences", [])
                ),
                "content_format": self._determine_content_format(platform, content_type),
                "media_requirements": self._determine_media_requirements(platform, content_type)
            }
            
            adaptations[platform] = adaptation
        
        return adaptations
    
    async def _suggest_hashtags(
        self,
        platform: str,
        intent_analysis: Dict[str, Any]
    ) -> List[str]:
        """Suggest relevant hashtags for the platform and content"""
        
        topics = intent_analysis.get("topics", [])
        audience = intent_analysis.get("audience", {})
        
        # This would integrate with hashtag research APIs in production
        # For now, basic topic-based suggestions
        
        hashtag_suggestions = []
        
        for topic in topics[:3]:  # Limit to top 3 topics
            # Clean and format topic as hashtag
            hashtag = f"#{topic.replace(' ', '').lower()}"
            hashtag_suggestions.append(hashtag)
        
        # Add platform-specific trending hashtags (mock data)
        if platform == "twitter":
            hashtag_suggestions.extend(["#tech", "#innovation"])
        elif platform == "linkedin":
            hashtag_suggestions.extend(["#professional", "#business"])
        elif platform == "instagram":
            hashtag_suggestions.extend(["#lifestyle", "#inspiration"])
        
        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(hashtag_suggestions))
        platform_limit = self.platform_strategies.get(platform, {}).get("hashtag_limit", 5)
        
        return unique_hashtags[:platform_limit]
```

### 3. Content Generation Agent

**File**: `workflows/agents/content_generation_agent.py`

```python
"""
Content Generation Agent for ZENALTO

Generates optimized social media content based on intent analysis and strategy planning.
Handles platform-specific formatting, tone adaptation, and media integration.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from prompts.social_prompts import (
    CONTENT_GENERATION_PROMPT,
    PLATFORM_OPTIMIZATION_PROMPT,
    HASHTAG_GENERATION_PROMPT
)

class ContentGenerationAgent:
    def __init__(self, mcp_agent: Agent, logger: logging.Logger):
        self.mcp_agent = mcp_agent
        self.logger = logger
        self.name = "content_generation_agent"
        
        # Content templates for different platforms
        self.content_templates = {
            "twitter": {
                "single": "Simple tweet format",
                "thread": "Multi-tweet thread format",
                "poll": "Twitter poll format"
            },
            "linkedin": {
                "post": "Professional LinkedIn post",
                "article": "Long-form LinkedIn article",
                "question": "Engagement-focused question post"
            },
            "instagram": {
                "post": "Visual-focused Instagram post",
                "story": "Instagram story content",
                "carousel": "Multi-image carousel post"
            }
        }
    
    async def generate_content(
        self,
        intent_analysis: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimized content for all target platforms
        
        Args:
            intent_analysis: Results from ContentIntentAgent
            strategy: Strategy from ContentStrategyAgent
            
        Returns:
            Platform-optimized content for each target platform
        """
        
        self.logger.info("Generating content for platforms...")
        
        try:
            platforms = intent_analysis.get("platforms", [])
            platform_content = {}
            
            # Generate base content
            base_content = await self._generate_base_content(intent_analysis)
            
            # Adapt for each platform
            for platform in platforms:
                platform_strategy = strategy.get("adaptation_strategy", {}).get(platform, {})
                
                adapted_content = await self._adapt_content_for_platform(
                    base_content,
                    platform,
                    platform_strategy,
                    intent_analysis
                )
                
                platform_content[platform] = adapted_content
            
            result = {
                "base_content": base_content,
                "platform_content": platform_content,
                "generation_metadata": {
                    "platforms_generated": len(platform_content),
                    "content_type": intent_analysis.get("content_type", "post"),
                    "tone": intent_analysis.get("tone", "professional"),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"Generated content for {len(platforms)} platforms")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return {
                "error": str(e),
                "platform_content": {},
                "generated_at": datetime.now().isoformat()
            }
    
    async def _generate_base_content(
        self,
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate base content that will be adapted for each platform"""
        
        prompt = CONTENT_GENERATION_PROMPT.format(
            intent_summary=intent_analysis.get("intent_summary", ""),
            topics=", ".join(intent_analysis.get("topics", [])),
            audience=intent_analysis.get("audience", {}),
            tone=intent_analysis.get("tone", "professional"),
            content_type=intent_analysis.get("content_type", "post")
        )
        
        response = await self.mcp_agent.call_tool(
            "content_generation",
            {
                "prompt": prompt,
                "intent_analysis": intent_analysis
            }
        )
        
        base_content = json.loads(response)
        
        return {
            "main_text": base_content.get("text", ""),
            "key_points": base_content.get("key_points", []),
            "call_to_action": base_content.get("call_to_action", ""),
            "media_suggestions": base_content.get("media_suggestions", []),
            "tone_indicators": base_content.get("tone_indicators", [])
        }
    
    async def _adapt_content_for_platform(
        self,
        base_content: Dict[str, Any],
        platform: str,
        platform_strategy: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt base content for specific platform requirements"""
        
        # Platform-specific optimization
        optimization_prompt = PLATFORM_OPTIMIZATION_PROMPT.format(
            base_text=base_content.get("main_text", ""),
            platform=platform,
            max_length=platform_strategy.get("max_length", 1000),
            tone=platform_strategy.get("tone_adaptation", "professional"),
            content_format=platform_strategy.get("content_format", "post")
        )
        
        optimized_response = await self.mcp_agent.call_tool(
            "platform_optimization",
            {
                "prompt": optimization_prompt,
                "platform": platform,
                "base_content": base_content
            }
        )
        
        optimized_content = json.loads(optimized_response)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(
            platform,
            intent_analysis,
            platform_strategy
        )
        
        # Format final content
        adapted_content = {
            "text": optimized_content.get("optimized_text", ""),
            "hashtags": hashtags,
            "media_urls": [],  # Will be populated by media processing
            "platform_specific": {
                "character_count": len(optimized_content.get("optimized_text", "")),
                "estimated_engagement": self._estimate_engagement(platform, optimized_content),
                "posting_tips": optimized_content.get("posting_tips", []),
                "optimal_format": platform_strategy.get("content_format", "post")
            },
            "call_to_action": base_content.get("call_to_action", ""),
            "generated_at": datetime.now().isoformat()
        }
        
        return adapted_content
    
    async def _generate_hashtags(
        self,
        platform: str,
        intent_analysis: Dict[str, Any],
        platform_strategy: Dict[str, Any]
    ) -> List[str]:
        """Generate platform-appropriate hashtags"""
        
        hashtag_strategy = platform_strategy.get("hashtag_strategy", {})
        suggested_tags = hashtag_strategy.get("recommended_tags", [])
        
        if suggested_tags:
            return suggested_tags
        
        # Fallback hashtag generation
        prompt = HASHTAG_GENERATION_PROMPT.format(
            topics=", ".join(intent_analysis.get("topics", [])),
            platform=platform,
            audience=intent_analysis.get("audience", {}),
            limit=hashtag_strategy.get("limit", 5)
        )
        
        response = await self.mcp_agent.call_tool(
            "hashtag_generation",
            {
                "prompt": prompt,
                "platform": platform,
                "topics": intent_analysis.get("topics", [])
            }
        )
        
        hashtag_data = json.loads(response)
        return hashtag_data.get("hashtags", [])
    
    def _estimate_engagement(
        self,
        platform: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate potential engagement for the generated content"""
        
        # This would integrate with ML models in production
        # For now, basic heuristic-based estimation
        
        text_length = len(content.get("optimized_text", ""))
        has_hashtags = len(content.get("hashtags", [])) > 0
        has_call_to_action = bool(content.get("call_to_action"))
        
        # Platform-specific engagement factors
        engagement_factors = {
            "twitter": {"optimal_length": 100, "hashtag_boost": 0.2},
            "linkedin": {"optimal_length": 150, "hashtag_boost": 0.1},
            "instagram": {"optimal_length": 125, "hashtag_boost": 0.3}
        }
        
        platform_config = engagement_factors.get(platform, {"optimal_length": 100, "hashtag_boost": 0.1})
        
        # Base engagement score
        base_score = 0.3
        
        # Length optimization
        if text_length <= platform_config["optimal_length"] * 1.2:
            base_score += 0.1
        
        # Hashtag boost
        if has_hashtags:
            base_score += platform_config["hashtag_boost"]
        
        # Call to action boost
        if has_call_to_action:
            base_score += 0.1
        
        return {
            "estimated_rate": min(base_score, 0.8),  # Cap at 80%
            "confidence": 0.6,  # Medium confidence for heuristic-based
            "factors": {
                "text_length_optimized": text_length <= platform_config["optimal_length"] * 1.2,
                "has_hashtags": has_hashtags,
                "has_call_to_action": has_call_to_action
            }
        }
```

## Testing Requirements

### 1. Unit Tests for Each Agent
```python
# Test content intent analysis
@pytest.mark.asyncio
async def test_content_intent_analysis():
    agent = ContentIntentAgent(mock_mcp_agent, mock_logger)
    
    result = await agent.analyze_content_intent(
        "Create a professional LinkedIn post about AI trends"
    )
    
    assert result["platforms"] == ["linkedin"]
    assert result["tone"] == "professional" 
    assert "AI" in result["topics"]
    assert result["confidence_score"] > 0.7

# Test content generation
@pytest.mark.asyncio
async def test_content_generation():
    agent = ContentGenerationAgent(mock_mcp_agent, mock_logger)
    
    intent_analysis = {
        "intent_summary": "Create engaging post about AI",
        "platforms": ["twitter", "linkedin"],
        "tone": "professional",
        "topics": ["AI", "technology"]
    }
    
    strategy = {
        "adaptation_strategy": {
            "twitter": {"max_length": 280},
            "linkedin": {"max_length": 3000}
        }
    }
    
    result = await agent.generate_content(intent_analysis, strategy)
    
    assert "platform_content" in result
    assert "twitter" in result["platform_content"]
    assert "linkedin" in result["platform_content"]
    assert len(result["platform_content"]["twitter"]["text"]) <= 280
```

## Success Criteria
- [ ] All agents follow existing DeepCode patterns
- [ ] Agents integrate seamlessly with MCP framework
- [ ] Content generation produces platform-optimized output
- [ ] Intent analysis achieves >85% accuracy on test cases
- [ ] Strategy planning considers platform best practices
- [ ] Performance matches existing DeepCode agents (< 10 second response time)

## Dependencies
- MCP framework integration
- Social media prompt templates
- Platform API specifications
- Testing infrastructure setup

## Timeline
- **Week 1**: Implement ContentIntentAgent
- **Week 2**: Implement ContentStrategyAgent and ContentGenerationAgent  
- **Week 3**: Integration testing and optimization
- **Week 4**: Performance tuning and documentation