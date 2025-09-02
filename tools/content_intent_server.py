"""
Content Intent Analysis Server for ZenAlto

This MCP server provides AI-powered content intent analysis for social media management.
It analyzes user requests to understand content goals, target platforms, audience, and requirements.
"""

import os
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

# MCP Server imports
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Import social media prompts
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts.social_prompts import CONTENT_INTENT_ANALYSIS_PROMPT


class ContentIntentServer:
    """
    MCP Server for Content Intent Analysis

    Provides tools for:
    - Analyzing user content requests
    - Extracting intent and requirements
    - Understanding target platforms and audience
    - Learning user preferences over time
    """

    def __init__(self):
        self.server = Server("content-intent-server")
        self.logger = logging.getLogger(__name__)

        # User preference learning (would be stored in database)
        self.user_preferences = {}

    async def analyze_intent(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze user request to understand content intent

        Args:
            user_request: The user's natural language request
            context: Additional context (conversation history, platform status, etc.)

        Returns:
            Intent analysis results
        """
        try:
            # Prepare context for analysis
            conversation_history = ""
            platform_context = ""

            if context:
                if context.get("conversation_history"):
                    # Format conversation history
                    history_items = context["conversation_history"][-5:]  # Last 5 messages
                    conversation_history = "\n".join([
                        f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                        for msg in history_items
                    ])

                if context.get("platform_status"):
                    # Format platform connection status
                    connected_platforms = [
                        platform for platform, status in context["platform_status"].items()
                        if status.get("connected", False)
                    ]
                    platform_context = f"Connected platforms: {', '.join(connected_platforms)}"

            # Format the analysis prompt
            prompt = CONTENT_INTENT_ANALYSIS_PROMPT.format(
                user_request=user_request,
                conversation_history=conversation_history,
                platform_context=platform_context
            )

            # In a real implementation, this would call an AI model
            # For now, return a structured analysis
            intent_analysis = await self._perform_intent_analysis(prompt)

            return {
                "success": True,
                "intent_analysis": intent_analysis,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error analyzing intent: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _perform_intent_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Perform the actual intent analysis using AI

        Args:
            prompt: Formatted analysis prompt

        Returns:
            Structured intent analysis
        """
        # This is a simplified implementation
        # In a real system, this would call an AI model (Claude, GPT, etc.)

        # Extract basic information from the prompt
        prompt_lower = prompt.lower()

        # Default analysis structure
        analysis = {
            "intent_summary": "Create social media content",
            "platforms": ["twitter"],
            "audience": "General audience",
            "content_type": "Social media post",
            "tone": "Professional",
            "topics": [],
            "cta": "",
            "urgency": "Normal",
            "additional_requirements": ""
        }

        # Simple keyword-based analysis (would be replaced with AI)
        if "twitter" in prompt_lower or "tweet" in prompt_lower:
            analysis["platforms"].append("twitter")
        if "instagram" in prompt_lower or "insta" in prompt_lower:
            analysis["platforms"].append("instagram")
        if "linkedin" in prompt_lower:
            analysis["platforms"].append("linkedin")
        if "facebook" in prompt_lower or "fb" in prompt_lower:
            analysis["platforms"].append("facebook")
        if "youtube" in prompt_lower or "video" in prompt_lower:
            analysis["platforms"].append("youtube")

        # Remove duplicates
        analysis["platforms"] = list(set(analysis["platforms"]))

        # Determine content type
        if "thread" in prompt_lower:
            analysis["content_type"] = "Twitter thread"
        elif "reel" in prompt_lower or "short video" in prompt_lower:
            analysis["content_type"] = "Short video/Reel"
        elif "story" in prompt_lower:
            analysis["content_type"] = "Story"
        elif "post" in prompt_lower:
            analysis["content_type"] = "Social media post"

        # Determine tone
        if "casual" in prompt_lower or "friendly" in prompt_lower:
            analysis["tone"] = "Casual"
        elif "professional" in prompt_lower or "business" in prompt_lower:
            analysis["tone"] = "Professional"
        elif "humorous" in prompt_lower or "funny" in prompt_lower:
            analysis["tone"] = "Humorous"

        # Determine urgency
        if "urgent" in prompt_lower or "asap" in prompt_lower or "immediately" in prompt_lower:
            analysis["urgency"] = "High"
        elif "schedule" in prompt_lower or "later" in prompt_lower:
            analysis["urgency"] = "Scheduled"

        return analysis

    async def learn_user_preferences(self, user_id: str, intent_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Learn user preferences from intent analysis history

        Args:
            user_id: Unique user identifier
            intent_history: History of intent analyses

        Returns:
            Learned user preferences
        """
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {
                    "preferred_platforms": [],
                    "common_tones": [],
                    "preferred_content_types": [],
                    "common_topics": [],
                    "posting_patterns": {}
                }

            preferences = self.user_preferences[user_id]

            if intent_history:
                # Analyze history to learn preferences
                platforms = []
                tones = []
                content_types = []
                topics = []

                for intent in intent_history[-20:]:  # Last 20 analyses
                    platforms.extend(intent.get("platforms", []))
                    tones.append(intent.get("tone", ""))
                    content_types.append(intent.get("content_type", ""))
                    topics.extend(intent.get("topics", []))

                # Update preferences with most common values
                from collections import Counter

                preferences["preferred_platforms"] = [p for p, _ in Counter(platforms).most_common(3)]
                preferences["common_tones"] = [t for t, _ in Counter(tones).most_common(2)]
                preferences["preferred_content_types"] = [ct for ct, _ in Counter(content_types).most_common(2)]
                preferences["common_topics"] = [t for t, _ in Counter(topics).most_common(5)]

            return {
                "success": True,
                "user_id": user_id,
                "preferences": preferences,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error learning user preferences: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_content_suggestions(self, user_id: str, topic: str, platform: str) -> Dict[str, Any]:
        """
        Get personalized content suggestions based on user preferences

        Args:
            user_id: Unique user identifier
            topic: Content topic
            platform: Target platform

        Returns:
            Personalized content suggestions
        """
        try:
            preferences = self.user_preferences.get(user_id, {})

            # Generate suggestions based on preferences
            suggestions = {
                "topic": topic,
                "platform": platform,
                "suggested_content": [],
                "recommended_tone": preferences.get("common_tones", ["Professional"])[0],
                "suggested_hashtags": self._generate_hashtags(topic, platform),
                "personalization_notes": "Based on your posting history and preferences"
            }

            # Generate content suggestions
            content_ideas = self._generate_content_ideas(topic, platform, preferences)
            suggestions["suggested_content"] = content_ideas

            return {
                "success": True,
                "suggestions": suggestions,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error generating content suggestions: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _generate_hashtags(self, topic: str, platform: str) -> List[str]:
        """Generate relevant hashtags for topic and platform"""
        base_hashtags = [f"#{topic.replace(' ', '')}", f"#{topic.replace(' ', '').lower()}"]

        # Platform-specific hashtags
        platform_hashtags = {
            "twitter": ["#Twitter", "#SocialMedia"],
            "instagram": ["#Instagram", "#InstaDaily"],
            "linkedin": ["#LinkedIn", "#Professional"],
            "facebook": ["#Facebook", "#Community"],
            "youtube": ["#YouTube", "#Video"]
        }

        base_hashtags.extend(platform_hashtags.get(platform, []))
        return base_hashtags[:5]  # Limit to 5 hashtags

    def _generate_content_ideas(self, topic: str, platform: str, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content ideas based on preferences"""
        ideas = []

        # Basic content templates
        templates = [
            f"Sharing insights about {topic} and its impact on our industry",
            f"What I've learned about {topic} recently",
            f"Thoughts on {topic} and future trends",
            f"Quick tip: {topic} best practices",
            f"Question: What's your experience with {topic}?"
        ]

        preferred_tone = preferences.get("common_tones", ["Professional"])[0]

        for i, template in enumerate(templates):
            idea = {
                "id": f"idea_{i+1}",
                "content": template,
                "tone": preferred_tone,
                "estimated_engagement": "Medium",
                "hashtags": self._generate_hashtags(topic, platform)
            }
            ideas.append(idea)

        return ideas


# MCP Server Tool Handlers

async def handle_analyze_intent(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle analyze_intent tool call"""
    server = ContentIntentServer()

    user_request = arguments.get("user_request", "")
    context = arguments.get("context", {})

    result = await server.analyze_intent(user_request, context)

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_learn_preferences(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle learn_preferences tool call"""
    server = ContentIntentServer()

    user_id = arguments.get("user_id", "")
    intent_history = arguments.get("intent_history", [])

    result = await server.learn_user_preferences(user_id, intent_history)

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def handle_get_suggestions(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle get_suggestions tool call"""
    server = ContentIntentServer()

    user_id = arguments.get("user_id", "")
    topic = arguments.get("topic", "")
    platform = arguments.get("platform", "")

    result = await server.get_content_suggestions(user_id, topic, platform)

    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


# Tool definitions for MCP
CONTENT_INTENT_TOOLS = [
    Tool(
        name="analyze_intent",
        description="Analyze user request to understand content intent and requirements",
        inputSchema={
            "type": "object",
            "properties": {
                "user_request": {
                    "type": "string",
                    "description": "The user's natural language request"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context for analysis",
                    "properties": {
                        "conversation_history": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Previous conversation messages"
                        },
                        "platform_status": {
                            "type": "object",
                            "description": "Current platform connection status"
                        }
                    }
                }
            },
            "required": ["user_request"]
        }
    ),
    Tool(
        name="learn_preferences",
        description="Learn user preferences from content creation history",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Unique user identifier"
                },
                "intent_history": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "History of intent analyses"
                }
            },
            "required": ["user_id", "intent_history"]
        }
    ),
    Tool(
        name="get_suggestions",
        description="Get personalized content suggestions based on user preferences",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                            "description": "Unique user identifier"
                },
                "topic": {
                    "type": "string",
                    "description": "Content topic or theme"
                },
                "platform": {
                    "type": "string",
                    "enum": ["twitter", "instagram", "linkedin", "facebook", "youtube"],
                    "description": "Target social media platform"
                }
            },
            "required": ["user_id", "topic", "platform"]
        }
    )
]


if __name__ == "__main__":
    # This would be the main entry point when run as a server
    print("ZenAlto Content Intent Analysis MCP Server")
    print("This server provides AI-powered content intent analysis tools")
