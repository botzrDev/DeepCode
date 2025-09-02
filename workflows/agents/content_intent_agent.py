"""
Content Intent Agent for Social Media Management

Handles user intent understanding and content goal analysis for social media management.
Processes natural language requests and extracts content objectives, target audiences,
and platform-specific requirements.
"""

import json
import logging
from typing import Dict, Any, List, Optional

# Import tiktoken for token calculation
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

# Import prompts from social media prompts
import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from prompts.social_prompts import (
    CONTENT_INTENT_ANALYSIS_PROMPT,
)


class ContentIntentAgent:
    """
    Content Intent Agent for understanding user social media goals

    Responsibilities:
    - Analyze user content requests and extract intent
    - Identify target platforms and audience
    - Determine content type and tone requirements
    - Track user preferences and learning patterns
    - Coordinate with other agents for content strategy
    """

    def __init__(
        self,
        mcp_agent,
        logger: Optional[logging.Logger] = None,
        enable_social_tools: bool = True,
    ):
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)
        self.enable_social_tools = enable_social_tools

        # Initialize token counter if available
        if TIKTOKEN_AVAILABLE:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None

    async def analyze_content_intent(
        self,
        user_request: str,
        conversation_history: List[Dict[str, Any]] = None,
        platform_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze user request to understand content intent and requirements

        Args:
            user_request: The user's natural language request
            conversation_history: Previous conversation context
            platform_context: Current platform connections and status

        Returns:
            Dict containing intent analysis results
        """
        try:
            # Prepare the prompt with context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n".join([
                    f"User: {msg.get('user', '')}\nAssistant: {msg.get('assistant', '')}"
                    for msg in conversation_history[-5:]  # Last 5 messages for context
                ])

            platform_info = ""
            if platform_context:
                connected_platforms = [
                    p for p, status in platform_context.items()
                    if status.get('connected', False)
                ]
                platform_info = f"Connected platforms: {', '.join(connected_platforms)}"

            prompt = CONTENT_INTENT_ANALYSIS_PROMPT.format(
                user_request=user_request,
                conversation_history=conversation_context,
                platform_context=platform_info
            )

            # Use MCP agent to analyze intent
            response = await self.mcp_agent.call_tool(
                "content_intent_analysis",
                {"prompt": prompt}
            )

            # Parse and validate the response
            intent_analysis = self._parse_intent_response(response)

            # Log the analysis
            self.logger.info(f"Content intent analyzed: {intent_analysis.get('intent_summary', '')}")

            return intent_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing content intent: {str(e)}")
            return self._get_default_intent_analysis(user_request)

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the intent analysis response from the AI model

        Args:
            response: Raw response from the AI model

        Returns:
            Parsed intent analysis dictionary
        """
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)

            # If not JSON, extract structured information from text
            return self._extract_intent_from_text(response)

        except json.JSONDecodeError:
            return self._extract_intent_from_text(response)

    def _extract_intent_from_text(self, response: str) -> Dict[str, Any]:
        """
        Extract intent information from unstructured text response

        Args:
            response: Text response from AI model

        Returns:
            Structured intent analysis
        """
        # Default structure
        intent_analysis = {
            "intent_summary": "Create social media content",
            "platforms": ["twitter", "instagram"],
            "audience": "General audience",
            "content_type": "Social media post",
            "tone": "Professional",
            "topics": [],
            "cta": "",
            "urgency": "Normal",
            "additional_requirements": ""
        }

        # Extract information from text (simplified implementation)
        response_lower = response.lower()

        # Detect platforms
        if "twitter" in response_lower or "x" in response_lower:
            intent_analysis["platforms"].append("twitter")
        if "instagram" in response_lower:
            intent_analysis["platforms"].append("instagram")
        if "linkedin" in response_lower:
            intent_analysis["platforms"].append("linkedin")
        if "facebook" in response_lower:
            intent_analysis["platforms"].append("facebook")
        if "youtube" in response_lower:
            intent_analysis["platforms"].append("youtube")

        # Remove duplicates
        intent_analysis["platforms"] = list(set(intent_analysis["platforms"]))

        return intent_analysis

    def _get_default_intent_analysis(self, user_request: str) -> Dict[str, Any]:
        """
        Provide default intent analysis when parsing fails

        Args:
            user_request: Original user request

        Returns:
            Default intent analysis structure
        """
        return {
            "intent_summary": f"Process request: {user_request[:100]}...",
            "platforms": ["twitter"],  # Default to Twitter
            "audience": "General audience",
            "content_type": "Social media post",
            "tone": "Professional",
            "topics": [],
            "cta": "",
            "urgency": "Normal",
            "additional_requirements": "AI-generated analysis"
        }

    async def learn_user_preferences(
        self,
        user_id: str,
        content_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Learn and update user content preferences based on history

        Args:
            user_id: Unique user identifier
            content_history: User's content creation history

        Returns:
            Updated user preferences
        """
        try:
            # Analyze content history to learn preferences
            preferences = {
                "preferred_platforms": [],
                "common_topics": [],
                "preferred_tones": [],
                "posting_patterns": {},
                "engagement_rates": {}
            }

            if content_history:
                # Extract preferences from history (simplified)
                platforms = [item.get('platform') for item in content_history if item.get('platform')]
                preferences["preferred_platforms"] = list(set(platforms))

                topics = []
                for item in content_history:
                    if item.get('topics'):
                        topics.extend(item['topics'])
                preferences["common_topics"] = list(set(topics))[:10]  # Top 10 topics

            return preferences

        except Exception as e:
            self.logger.error(f"Error learning user preferences: {str(e)}")
            return {}

    def calculate_token_usage(self, text: str) -> int:
        """
        Calculate token usage for text (if tiktoken is available)

        Args:
            text: Text to calculate tokens for

        Returns:
            Number of tokens used
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Rough estimation: 1 token ≈ 4 characters
            return len(text) // 4
