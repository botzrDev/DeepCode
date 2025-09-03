"""
Content Generation Agent for ZENALTO Social Media Management

This agent handles the actual generation of social media content based on
intent analysis and strategy, creating platform-optimized posts, captions,
and other content elements.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class ContentGenerationAgent:
    """
    Content Generation Agent for creating social media content.

    Responsibilities:
    - Generate platform-specific content based on strategy
    - Create engaging captions, hashtags, and calls-to-action
    - Optimize content for each platform's requirements
    - Ensure content aligns with brand voice and strategy
    - Handle content variations and A/B testing suggestions
    """

    def __init__(self, mcp_agent, logger: Optional[logging.Logger] = None):
        """
        Initialize the Content Generation Agent.

        Args:
            mcp_agent: MCP agent instance for tool calls
            logger: Optional logger instance
        """
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)

        # Platform-specific constraints and requirements
        self.platform_specs = {
            "twitter": {
                "max_length": 280,
                "hashtag_limit": 3,
                "optimal_hashtags": 2,
                "media_types": ["image", "gif", "video"],
            },
            "instagram": {
                "max_length": 2200,
                "hashtag_limit": 30,
                "optimal_hashtags": 8,
                "media_types": ["image", "video", "carousel", "reel"],
            },
            "linkedin": {
                "max_length": 3000,
                "hashtag_limit": 5,
                "optimal_hashtags": 3,
                "media_types": ["image", "video", "document", "article"],
            },
            "facebook": {
                "max_length": 63206,
                "hashtag_limit": 3,
                "optimal_hashtags": 2,
                "media_types": ["image", "video", "link", "event"],
            },
            "youtube": {
                "title_length": 100,
                "description_length": 5000,
                "hashtag_limit": 15,
                "optimal_hashtags": 8,
                "media_types": ["video", "shorts", "live"],
            },
        }

    async def generate_content(
        self,
        intent_analysis: Dict[str, Any],
        strategy: Dict[str, Any],
        user_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive social media content based on intent and strategy.

        Args:
            intent_analysis: Results from content intent analysis
            strategy: Content strategy from strategy agent
            user_preferences: User's content preferences

        Returns:
            Dict containing generated content for all target platforms
        """
        try:
            self.logger.info("Starting content generation...")

            platforms = intent_analysis.get("platforms", [])
            content_type = intent_analysis.get("content_type", "Social media post")
            # Note: topics, tone, cta will be used in future enhancements
            # topics = intent_analysis.get('topics', [])
            # tone = intent_analysis.get('tone', 'Professional')
            # cta = intent_analysis.get('cta', '')

            # Generate content for each platform
            generated_content = {
                "generation_id": self._generate_content_id(),
                "created_at": datetime.now().isoformat(),
                "intent_summary": intent_analysis.get("intent_summary", ""),
                "platforms": platforms,
                "content_type": content_type,
                "platform_content": {},
            }

            for platform in platforms:
                self.logger.info(f"Generating content for {platform}")
                platform_content = await self._generate_platform_content(
                    platform, intent_analysis, strategy, user_preferences
                )
                generated_content["platform_content"][platform] = platform_content

            # Add cross-platform recommendations
            generated_content["cross_platform_tips"] = self._get_cross_platform_tips(
                platforms
            )
            generated_content["content_variations"] = self._suggest_content_variations(
                generated_content
            )
            
            # Add generation metadata for consistency with spec
            generated_content["generation_metadata"] = {
                "platforms_generated": len(platforms),
                "content_type": content_type,
                "tone": intent_analysis.get("tone", "professional"),
                "generated_at": generated_content["created_at"]
            }

            self.logger.info(f"Content generated for {len(platforms)} platforms")
            return generated_content

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return self._get_default_content(intent_analysis)

    async def _generate_platform_content(
        self,
        platform: str,
        intent_analysis: Dict[str, Any],
        strategy: Dict[str, Any],
        user_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate content for a specific platform.

        Args:
            platform: Target platform
            intent_analysis: Intent analysis results
            strategy: Content strategy
            user_preferences: User preferences

        Returns:
            Dict containing platform-specific content
        """
        try:
            # Use MCP agent to generate content if available
            if hasattr(self.mcp_agent, "call_tool"):
                prompt = self._build_generation_prompt(
                    platform, intent_analysis, strategy
                )
                response = await self.mcp_agent.call_tool(
                    "content_generation", {"prompt": prompt, "platform": platform}
                )

                # Parse and validate response
                if response:
                    return self._parse_generation_response(response, platform)

        except Exception as e:
            self.logger.warning(
                f"MCP content generation failed for {platform}: {str(e)}"
            )

        # Fallback to built-in generation
        return self._generate_platform_content_fallback(
            platform, intent_analysis, strategy
        )

    def _build_generation_prompt(
        self, platform: str, intent_analysis: Dict[str, Any], strategy: Dict[str, Any]
    ) -> str:
        """
        Build prompt for content generation.

        Args:
            platform: Target platform
            intent_analysis: Intent analysis results
            strategy: Content strategy

        Returns:
            Formatted prompt string
        """
        from prompts.social_prompts import CONTENT_GENERATION_PROMPT

        platform_requirements = self.platform_specs.get(platform, {})
        # Note: platform_strategy will be used in future enhancements
        # platform_strategy = strategy.get('platform_strategies', {}).get(platform, {})

        return CONTENT_GENERATION_PROMPT.format(
            intent_analysis=json.dumps(intent_analysis, indent=2),
            platform_requirements=json.dumps(platform_requirements, indent=2),
            user_preferences=json.dumps({}, indent=2),  # TODO: Use actual preferences
            brand_guidelines=json.dumps({}, indent=2),  # TODO: Use actual guidelines
        )

    def _parse_generation_response(
        self, response: str, platform: str
    ) -> Dict[str, Any]:
        """
        Parse content generation response.

        Args:
            response: Raw response from content generation
            platform: Target platform

        Returns:
            Parsed content dictionary
        """
        try:
            if response.strip().startswith("{"):
                parsed = json.loads(response)
                if (
                    "platform_content" in parsed
                    and platform in parsed["platform_content"]
                ):
                    return parsed["platform_content"][platform]
                return parsed
            else:
                # Extract content from text response
                return self._extract_content_from_text(response, platform)

        except json.JSONDecodeError:
            return self._extract_content_from_text(response, platform)

    def _extract_content_from_text(
        self, response: str, platform: str
    ) -> Dict[str, Any]:
        """
        Extract content from unstructured text response.

        Args:
            response: Text response
            platform: Target platform

        Returns:
            Structured content dictionary
        """
        # Basic extraction logic
        lines = response.split("\n")
        content = {
            "main_content": response[:200],  # First 200 chars as main content
            "hashtags": [],
            "emojis": [],
            "media_suggestions": f"Suggested media for {platform}",
            "posting_tips": f"Optimize for {platform} best practices",
        }

        # Extract hashtags
        hashtags = []
        for line in lines:
            if "#" in line:
                words = line.split()
                for word in words:
                    if word.startswith("#") and len(word) > 1:
                        hashtags.append(word)

        content["hashtags"] = hashtags[
            : self.platform_specs.get(platform, {}).get("optimal_hashtags", 3)
        ]

        return content

    def _generate_platform_content_fallback(
        self, platform: str, intent_analysis: Dict[str, Any], strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback content generation when MCP tools are unavailable.

        Args:
            platform: Target platform
            intent_analysis: Intent analysis results
            strategy: Content strategy

        Returns:
            Generated content dictionary
        """
        intent_summary = intent_analysis.get("intent_summary", "")
        topics = intent_analysis.get("topics", [])
        tone = intent_analysis.get("tone", "Professional")
        cta = intent_analysis.get("cta", "")

        # Platform-specific content templates
        templates = {
            "twitter": {
                "main_content": self._generate_twitter_content(
                    intent_summary, topics, tone, cta
                ),
                "hashtags": self._generate_hashtags(topics, 2),
                "emojis": ["🚀", "💡"],
                "media_suggestions": "Eye-catching image or short video",
                "posting_tips": "Tweet during peak hours (9-10am, 1-3pm, 5-6pm)",
            },
            "instagram": {
                "main_content": self._generate_instagram_content(
                    intent_summary, topics, tone, cta
                ),
                "hashtags": self._generate_hashtags(topics, 8),
                "emojis": ["✨", "🎯", "💪"],
                "media_suggestions": "High-quality image or reel with engaging visuals",
                "posting_tips": "Post when followers are most active (11am-1pm, 5-7pm)",
            },
            "linkedin": {
                "main_content": self._generate_linkedin_content(
                    intent_summary, topics, tone, cta
                ),
                "hashtags": self._generate_hashtags(topics, 3),
                "emojis": ["🔗", "📈", "💼"],
                "media_suggestions": "Professional infographic or industry-related image",
                "posting_tips": "Share during business hours (8-10am, 12-2pm weekdays)",
            },
            "facebook": {
                "main_content": self._generate_facebook_content(
                    intent_summary, topics, tone, cta
                ),
                "hashtags": self._generate_hashtags(topics, 2),
                "emojis": ["👍", "🎉", "📢"],
                "media_suggestions": "Engaging image or video that encourages sharing",
                "posting_tips": "Post when audience is most active (1-3pm, 7-9pm)",
            },
            "youtube": {
                "title": self._generate_youtube_title(intent_summary, topics),
                "description": self._generate_youtube_description(
                    intent_summary, topics, cta
                ),
                "hashtags": self._generate_hashtags(topics, 8),
                "emojis": ["🎬", "⭐", "🔥"],
                "media_suggestions": "Compelling thumbnail and well-structured video content",
                "posting_tips": "Upload during optimal times (2-4pm weekdays, 9am-11am weekends)",
            },
        }

        return templates.get(platform, templates["twitter"])

    def _generate_twitter_content(
        self, intent: str, topics: List[str], tone: str, cta: str
    ) -> str:
        """Generate Twitter-optimized content."""
        content = intent[:180]  # Leave room for hashtags and CTA
        if cta:
            content += f"\n\n{cta}"
        return content

    def _generate_instagram_content(
        self, intent: str, topics: List[str], tone: str, cta: str
    ) -> str:
        """Generate Instagram-optimized content."""
        content = f"{intent}\n\n"
        if topics:
            content += f"Key topics: {', '.join(topics[:3])}\n\n"
        if cta:
            content += f"{cta}\n\n"
        content += "What are your thoughts? Let us know in the comments! 👇"
        return content

    def _generate_linkedin_content(
        self, intent: str, topics: List[str], tone: str, cta: str
    ) -> str:
        """Generate LinkedIn-optimized content."""
        content = f"{intent}\n\n"
        content += "Here's my perspective:\n\n"
        if topics:
            for i, topic in enumerate(topics[:3], 1):
                content += f"{i}. {topic.capitalize()}\n"
            content += "\n"
        if cta:
            content += f"{cta}\n\n"
        content += "What's your experience with this? I'd love to hear your thoughts in the comments."
        return content

    def _generate_facebook_content(
        self, intent: str, topics: List[str], tone: str, cta: str
    ) -> str:
        """Generate Facebook-optimized content."""
        content = f"{intent}\n\n"
        if topics:
            content += f"We're focusing on: {', '.join(topics)}\n\n"
        if cta:
            content += f"{cta}\n\n"
        content += "Tag someone who needs to see this! 👥"
        return content

    def _generate_youtube_title(self, intent: str, topics: List[str]) -> str:
        """Generate YouTube title."""
        if len(intent) <= 60:
            return intent
        return intent[:57] + "..."

    def _generate_youtube_description(
        self, intent: str, topics: List[str], cta: str
    ) -> str:
        """Generate YouTube description."""
        description = f"{intent}\n\n"
        if topics:
            description += "In this video, we cover:\n"
            for topic in topics[:5]:
                description += f"• {topic}\n"
            description += "\n"
        if cta:
            description += f"{cta}\n\n"
        description += (
            "Don't forget to like, subscribe, and hit the notification bell! 🔔"
        )
        return description

    def _generate_hashtags(self, topics: List[str], count: int) -> List[str]:
        """
        Generate hashtags based on topics.

        Args:
            topics: List of content topics
            count: Number of hashtags to generate

        Returns:
            List of hashtags
        """
        if not topics:
            return ["#content", "#socialmedia"][:count]

        hashtags = []
        for topic in topics:
            # Clean and format topic as hashtag
            hashtag = "#" + topic.lower().replace(" ", "").replace("-", "").replace(
                "_", ""
            )
            if len(hashtag) > 2:  # Ensure hashtag is meaningful
                hashtags.append(hashtag)

        # Add some general hashtags if we need more
        general_hashtags = [
            "#content",
            "#socialmedia",
            "#marketing",
            "#engagement",
            "#digital",
        ]
        hashtags.extend(general_hashtags)

        return hashtags[:count]

    def _get_cross_platform_tips(self, platforms: List[str]) -> List[str]:
        """
        Get tips for managing content across multiple platforms.

        Args:
            platforms: List of target platforms

        Returns:
            List of cross-platform tips
        """
        tips = [
            "Adapt content format for each platform while maintaining core message",
            "Use platform-specific hashtags and features",
            "Post at optimal times for each platform",
            "Engage with audience using platform-appropriate tone",
        ]

        if len(platforms) > 2:
            tips.extend(
                [
                    "Create a content calendar to manage multiple platforms",
                    "Use scheduling tools to maintain consistent posting",
                    "Monitor performance across platforms and optimize accordingly",
                ]
            )

        return tips

    def _suggest_content_variations(
        self, generated_content: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Suggest content variations for A/B testing.

        Args:
            generated_content: Generated content dictionary

        Returns:
            Dictionary of variation suggestions
        """
        return {
            "headline_variations": [
                "Try different hook openings",
                "Test question vs statement formats",
                "Experiment with emoji placement",
            ],
            "cta_variations": [
                "Test different call-to-action wordings",
                "Try direct vs subtle CTAs",
                "Experiment with CTA placement",
            ],
            "hashtag_variations": [
                "Test trending vs niche hashtags",
                "Vary hashtag count per platform",
                "Try branded vs generic hashtags",
            ],
        }

    def _generate_content_id(self) -> str:
        """Generate unique content ID."""
        return f"content_{int(datetime.now().timestamp())}"

    def _get_default_content(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide default content when generation fails.

        Args:
            intent_analysis: Intent analysis for fallback

        Returns:
            Default content structure
        """
        return {
            "generation_id": self._generate_content_id(),
            "created_at": datetime.now().isoformat(),
            "intent_summary": intent_analysis.get("intent_summary", ""),
            "platforms": intent_analysis.get("platforms", ["twitter"]),
            "content_type": intent_analysis.get("content_type", "Social media post"),
            "platform_content": {
                "twitter": {
                    "main_content": "Engaging social media content coming soon! 🚀",
                    "hashtags": ["#content", "#socialmedia"],
                    "emojis": ["🚀", "💡"],
                    "media_suggestions": "Eye-catching visual",
                    "posting_tips": "Post during peak engagement hours",
                }
            },
            "cross_platform_tips": ["Adapt content for each platform"],
            "content_variations": {"headline_variations": ["Try different approaches"]},
        }
