"""
Social Content Parser Agent for ZENALTO Social Media Management

This agent handles parsing and processing of existing social media content,
analyzing competitor content, and extracting insights from social media data.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class SocialContentParser:
    """
    Social Content Parser Agent for analyzing existing social media content.

    Responsibilities:
    - Parse and analyze existing social media posts
    - Extract insights from competitor content
    - Identify trending topics and hashtags
    - Analyze engagement patterns
    - Process uploaded media and content files
    """

    def __init__(self, mcp_agent, logger: Optional[logging.Logger] = None):
        """
        Initialize the Social Content Parser Agent.

        Args:
            mcp_agent: MCP agent instance for tool calls
            logger: Optional logger instance
        """
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)

    async def parse_social_content(
        self, content_data: Dict[str, Any], analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Parse and analyze social media content.

        Args:
            content_data: Social media content to analyze
                - text: Post text content
                - platform: Source platform
                - media: Associated media files
                - metadata: Additional metadata
            analysis_type: Type of analysis (basic, comprehensive, competitive)

        Returns:
            Dict containing parsed content analysis
        """
        try:
            self.logger.info(f"Parsing social content with {analysis_type} analysis")

            analysis = {
                "parsing_id": self._generate_parsing_id(),
                "created_at": datetime.now().isoformat(),
                "analysis_type": analysis_type,
                "source_platform": content_data.get("platform", "unknown"),
                "content_analysis": {},
                "engagement_analysis": {},
                "trend_analysis": {},
                "hashtag_analysis": {},
                "media_analysis": {},
                "recommendations": [],
            }

            # Parse text content
            text_content = content_data.get("text", "")
            if text_content:
                analysis["content_analysis"] = self._analyze_text_content(text_content)

            # Analyze hashtags
            hashtags = self._extract_hashtags(text_content)
            if hashtags:
                analysis["hashtag_analysis"] = self._analyze_hashtags(hashtags)

            # Analyze media if present
            media_data = content_data.get("media", [])
            if media_data:
                analysis["media_analysis"] = self._analyze_media_content(media_data)

            # Analyze engagement patterns
            metrics = content_data.get("metrics", {})
            if metrics:
                analysis["engagement_analysis"] = self._analyze_engagement_metrics(
                    metrics
                )

            # Perform trend analysis if comprehensive
            if analysis_type in ["comprehensive", "competitive"]:
                analysis["trend_analysis"] = await self._analyze_content_trends(
                    content_data
                )

            # Generate recommendations
            analysis["recommendations"] = self._generate_content_recommendations(
                analysis
            )

            self.logger.info("Content parsing completed successfully")
            return analysis

        except Exception as e:
            self.logger.error(f"Error parsing social content: {str(e)}")
            return self._get_default_parsing_result(content_data)

    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content of social media post.

        Args:
            text: Post text content

        Returns:
            Dict containing text analysis
        """
        analysis = {
            "character_count": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r"[.!?]+", text)),
            "emoji_count": len(
                re.findall(
                    r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
                    text,
                )
            ),
            "url_count": len(
                re.findall(
                    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    text,
                )
            ),
            "mention_count": len(re.findall(r"@\w+", text)),
            "hashtag_count": len(re.findall(r"#\w+", text)),
            "tone": self._analyze_tone(text),
            "readability": self._analyze_readability(text),
            "key_topics": self._extract_key_topics(text),
            "sentiment": self._analyze_sentiment(text),
        }

        return analysis

    def _analyze_tone(self, text: str) -> str:
        """
        Analyze the tone of the text content.

        Args:
            text: Text to analyze

        Returns:
            String describing the tone
        """
        text_lower = text.lower()

        # Simple tone detection based on keywords
        if any(
            word in text_lower
            for word in ["excited", "amazing", "awesome", "love", "!", "🎉", "🚀"]
        ):
            return "enthusiastic"
        elif any(
            word in text_lower
            for word in ["professional", "industry", "business", "strategy"]
        ):
            return "professional"
        elif any(
            word in text_lower
            for word in ["question", "?", "what do you think", "thoughts"]
        ):
            return "inquisitive"
        elif any(word in text_lower for word in ["thank", "grateful", "appreciate"]):
            return "grateful"
        elif any(word in text_lower for word in ["funny", "lol", "😂", "haha"]):
            return "humorous"
        else:
            return "neutral"

    def _analyze_readability(self, text: str) -> str:
        """
        Analyze readability of text content.

        Args:
            text: Text to analyze

        Returns:
            String describing readability level
        """
        words = text.split()
        sentences = re.split(r"[.!?]+", text)

        if len(sentences) == 0 or len(words) == 0:
            return "unknown"

        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)

        # Simplified readability scoring
        if avg_words_per_sentence <= 10 and avg_chars_per_word <= 5:
            return "very_easy"
        elif avg_words_per_sentence <= 15 and avg_chars_per_word <= 6:
            return "easy"
        elif avg_words_per_sentence <= 20 and avg_chars_per_word <= 7:
            return "moderate"
        else:
            return "difficult"

    def _extract_key_topics(self, text: str) -> List[str]:
        """
        Extract key topics from text content.

        Args:
            text: Text to analyze

        Returns:
            List of key topics
        """
        # Simple keyword extraction
        words = text.lower().split()

        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "this",
            "that",
            "these",
            "those",
        }

        filtered_words = [
            word for word in words if word not in stop_words and len(word) > 3
        ]

        # Simple frequency-based topic extraction
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency and return top topics
        sorted_words = sorted(
            word_freq.keys(), key=lambda w: word_freq[w], reverse=True
        )
        return sorted_words[:5]

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text content.

        Args:
            text: Text to analyze

        Returns:
            String describing sentiment (positive, negative, neutral)
        """
        text_lower = text.lower()

        positive_words = [
            "love",
            "great",
            "awesome",
            "amazing",
            "excellent",
            "wonderful",
            "fantastic",
            "perfect",
            "best",
            "good",
            "happy",
            "excited",
        ]
        negative_words = [
            "hate",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "bad",
            "sad",
            "angry",
            "disappointed",
            "frustrated",
        ]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text content.

        Args:
            text: Text containing hashtags

        Returns:
            List of hashtags
        """
        hashtags = re.findall(r"#\w+", text)
        return [hashtag.lower() for hashtag in hashtags]

    def _analyze_hashtags(self, hashtags: List[str]) -> Dict[str, Any]:
        """
        Analyze hashtag usage and effectiveness.

        Args:
            hashtags: List of hashtags to analyze

        Returns:
            Dict containing hashtag analysis
        """
        analysis = {
            "total_count": len(hashtags),
            "unique_count": len(set(hashtags)),
            "hashtag_list": hashtags,
            "trending_potential": self._assess_trending_potential(hashtags),
            "category_distribution": self._categorize_hashtags(hashtags),
            "recommendations": [],
        }

        # Generate hashtag recommendations
        if len(hashtags) == 0:
            analysis["recommendations"].append(
                "Consider adding relevant hashtags to increase discoverability"
            )
        elif len(hashtags) > 10:
            analysis["recommendations"].append(
                "Consider reducing hashtag count for better engagement"
            )
        else:
            analysis["recommendations"].append(
                "Good hashtag usage - consider testing variations"
            )

        return analysis

    def _assess_trending_potential(self, hashtags: List[str]) -> str:
        """
        Assess trending potential of hashtags.

        Args:
            hashtags: List of hashtags

        Returns:
            String describing trending potential
        """
        # Simplified trending assessment
        trending_indicators = [
            "trend",
            "viral",
            "breaking",
            "new",
            "latest",
            "2024",
            "2025",
        ]

        for hashtag in hashtags:
            if any(indicator in hashtag.lower() for indicator in trending_indicators):
                return "high"

        if len(hashtags) >= 3:
            return "medium"
        else:
            return "low"

    def _categorize_hashtags(self, hashtags: List[str]) -> Dict[str, int]:
        """
        Categorize hashtags by type.

        Args:
            hashtags: List of hashtags

        Returns:
            Dict with hashtag categories and counts
        """
        categories = {
            "branded": 0,
            "topical": 0,
            "community": 0,
            "trending": 0,
            "niche": 0,
        }

        branded_indicators = ["brand", "company", "product"]
        topical_indicators = ["tips", "howto", "tutorial", "guide"]
        community_indicators = ["community", "family", "team", "together"]
        trending_indicators = ["trend", "viral", "popular"]

        for hashtag in hashtags:
            hashtag_lower = hashtag.lower()
            categorized = False

            if any(indicator in hashtag_lower for indicator in branded_indicators):
                categories["branded"] += 1
                categorized = True
            elif any(indicator in hashtag_lower for indicator in topical_indicators):
                categories["topical"] += 1
                categorized = True
            elif any(indicator in hashtag_lower for indicator in community_indicators):
                categories["community"] += 1
                categorized = True
            elif any(indicator in hashtag_lower for indicator in trending_indicators):
                categories["trending"] += 1
                categorized = True

            if not categorized:
                categories["niche"] += 1

        return categories

    def _analyze_media_content(
        self, media_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze media content associated with posts.

        Args:
            media_data: List of media items with metadata

        Returns:
            Dict containing media analysis
        """
        analysis = {
            "media_count": len(media_data),
            "media_types": {},
            "total_size": 0,
            "format_distribution": {},
            "recommendations": [],
        }

        for media_item in media_data:
            media_type = media_item.get("type", "unknown")
            media_format = media_item.get("format", "unknown")
            media_size = media_item.get("size", 0)

            analysis["media_types"][media_type] = (
                analysis["media_types"].get(media_type, 0) + 1
            )
            analysis["format_distribution"][media_format] = (
                analysis["format_distribution"].get(media_format, 0) + 1
            )
            analysis["total_size"] += media_size

        # Generate media recommendations
        if analysis["media_count"] == 0:
            analysis["recommendations"].append(
                "Consider adding visual content to increase engagement"
            )
        elif analysis["media_count"] > 5:
            analysis["recommendations"].append(
                "Multiple media items - ensure they add value to the message"
            )
        else:
            analysis["recommendations"].append("Good use of visual content")

        return analysis

    def _analyze_engagement_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze engagement metrics from social media posts.

        Args:
            metrics: Dictionary containing engagement metrics

        Returns:
            Dict containing engagement analysis
        """
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        views = metrics.get("views", 0)

        total_engagement = likes + comments + shares
        engagement_rate = (total_engagement / views * 100) if views > 0 else 0

        analysis = {
            "total_engagement": total_engagement,
            "engagement_rate": round(engagement_rate, 2),
            "engagement_breakdown": {
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "views": views,
            },
            "engagement_quality": self._assess_engagement_quality(
                likes, comments, shares
            ),
            "performance_level": self._assess_performance_level(engagement_rate),
        }

        return analysis

    def _assess_engagement_quality(self, likes: int, comments: int, shares: int) -> str:
        """
        Assess the quality of engagement based on interaction types.

        Args:
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares

        Returns:
            String describing engagement quality
        """
        total = likes + comments + shares
        if total == 0:
            return "no_engagement"

        comment_ratio = comments / total
        share_ratio = shares / total

        if share_ratio > 0.3:  # High share ratio indicates viral potential
            return "viral_potential"
        elif comment_ratio > 0.4:  # High comment ratio indicates strong discussion
            return "discussion_driver"
        elif share_ratio > 0.1:  # Moderate sharing
            return "shareable"
        else:  # Mostly likes
            return "passive_engagement"

    def _assess_performance_level(self, engagement_rate: float) -> str:
        """
        Assess performance level based on engagement rate.

        Args:
            engagement_rate: Calculated engagement rate percentage

        Returns:
            String describing performance level
        """
        if engagement_rate >= 10:
            return "excellent"
        elif engagement_rate >= 5:
            return "very_good"
        elif engagement_rate >= 2:
            return "good"
        elif engagement_rate >= 1:
            return "fair"
        else:
            return "poor"

    async def _analyze_content_trends(
        self, content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze content for trending elements and patterns.

        Args:
            content_data: Content data to analyze for trends

        Returns:
            Dict containing trend analysis
        """
        try:
            # Use MCP agent for trend analysis if available
            if hasattr(self.mcp_agent, "call_tool"):
                response = await self.mcp_agent.call_tool(
                    "trend_analysis", {"content": content_data}
                )
                if response:
                    return self._parse_trend_response(response)
        except Exception as e:
            self.logger.warning(f"MCP trend analysis failed: {str(e)}")

        # Fallback trend analysis
        return {
            "trending_topics": [],
            "viral_potential": "low",
            "trend_alignment": "unknown",
            "recommendations": ["Enable trend analysis tools for better insights"],
        }

    def _parse_trend_response(self, response: str) -> Dict[str, Any]:
        """Parse trend analysis response."""
        # Simplified parsing - in real implementation would parse structured response
        return {
            "trending_topics": ["example_trend"],
            "viral_potential": "medium",
            "trend_alignment": "good",
            "recommendations": ["Leverage trending topics in future content"],
        }

    def _generate_content_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on content analysis.

        Args:
            analysis: Complete content analysis

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # Text content recommendations
        content_analysis = analysis.get("content_analysis", {})
        if content_analysis.get("readability") == "difficult":
            recommendations.append("Simplify language for better readability")

        if content_analysis.get("emoji_count", 0) == 0:
            recommendations.append("Consider adding emojis to increase engagement")

        # Hashtag recommendations
        hashtag_analysis = analysis.get("hashtag_analysis", {})
        if hashtag_analysis.get("total_count", 0) < 3:
            recommendations.append(
                "Add more relevant hashtags to increase discoverability"
            )

        # Engagement recommendations
        engagement_analysis = analysis.get("engagement_analysis", {})
        if engagement_analysis.get("performance_level") == "poor":
            recommendations.append("Review content strategy - engagement below average")
        elif engagement_analysis.get("performance_level") == "excellent":
            recommendations.append(
                "Excellent performance - consider replicating this content style"
            )

        # Media recommendations
        media_analysis = analysis.get("media_analysis", {})
        if media_analysis.get("media_count", 0) == 0:
            recommendations.append("Add visual content to improve engagement rates")

        return recommendations

    def _generate_parsing_id(self) -> str:
        """Generate unique parsing ID."""
        return f"parse_{int(datetime.now().timestamp())}"

    def _get_default_parsing_result(
        self, content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide default parsing result when analysis fails.

        Args:
            content_data: Original content data

        Returns:
            Default parsing structure
        """
        return {
            "parsing_id": self._generate_parsing_id(),
            "created_at": datetime.now().isoformat(),
            "analysis_type": "basic",
            "source_platform": content_data.get("platform", "unknown"),
            "content_analysis": {"error": "Analysis failed"},
            "engagement_analysis": {},
            "trend_analysis": {},
            "hashtag_analysis": {},
            "media_analysis": {},
            "recommendations": [
                "Content parsing encountered errors - manual review recommended"
            ],
        }
