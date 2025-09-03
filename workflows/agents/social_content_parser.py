"""
Social Content Parser for ZenAlto Social Media Management

Parses and analyzes existing social media content.

Responsibilities:
- Extract content from various sources
- Analyze competitor posts
- Identify trending topics
- Content repurposing
- Performance pattern analysis
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import uuid
import re
from urllib.parse import urlparse


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

    def __init__(
        self,
        mcp_agent,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        self.parsers = self._init_parsers()
        
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
        self.content_cache = {}
        self.competitor_cache = {}
        self.trending_cache = {}
    
    def _init_parsers(self) -> Dict[str, Any]:
        """Initialize content parsers for different platforms and sources."""
        return {
            "url_patterns": {
                "twitter": [r"twitter\.com", r"x\.com"],
                "instagram": [r"instagram\.com"],
                "linkedin": [r"linkedin\.com"],
                "facebook": [r"facebook\.com"],
                "youtube": [r"youtube\.com", r"youtu\.be"]
            },
            "content_types": {
                "article": [".html", ".htm", "blog", "article"],
                "post": ["post", "status", "update"],
                "thread": ["thread", "tweets"],
                "video": [".mp4", ".mov", ".avi", "youtube", "video"]
            }
        }

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
        try:
            self.logger.info(f"Parsing content from source: {source[:100]}...")
            
            # Auto-detect content type if not specified
            if content_type == "auto":
                content_type = self._detect_content_type(source)
            
            # Parse based on content type
            if content_type == "url":
                parsed_data = await self._parse_url_content(source)
            elif content_type == "file":
                parsed_data = await self._parse_file_content(source)
            elif content_type == "text":
                parsed_data = await self._parse_text_content(source)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Enhance parsed data with analysis
            enhanced_data = await self._enhance_parsed_content(parsed_data)
            
            # Cache the result
            cache_key = f"{content_type}_{hash(source)}"
            self.content_cache[cache_key] = enhanced_data
            
            self.logger.info("Content parsing completed successfully")
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Error parsing content: {e}")
            return self._get_error_response("parse_content", str(e))

    async def analyze_competitor_content(
        self,
        competitor_handles: List[str],
        platforms: List[str],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze competitor social media strategies."""
        try:
            self.logger.info(f"Analyzing {len(competitor_handles)} competitors across {len(platforms)} platforms")
            
            analysis_results = {
                "analysis_id": str(uuid.uuid4()),
                "analyzed_at": datetime.now().isoformat(),
                "time_range_days": days_back,
                "competitors": competitor_handles,
                "platforms": platforms,
                "competitor_data": {},
                "cross_platform_insights": {},
                "competitive_gaps": [],
                "strategic_recommendations": []
            }
            
            # Analyze each competitor on each platform
            for competitor in competitor_handles:
                competitor_data = {}
                
                for platform in platforms:
                    platform_analysis = await self._analyze_competitor_on_platform(
                        competitor, platform, days_back
                    )
                    competitor_data[platform] = platform_analysis
                
                analysis_results["competitor_data"][competitor] = competitor_data
            
            # Generate cross-platform insights
            analysis_results["cross_platform_insights"] = self._generate_cross_platform_insights(
                analysis_results["competitor_data"]
            )
            
            # Identify competitive gaps
            analysis_results["competitive_gaps"] = self._identify_competitive_gaps(
                analysis_results["competitor_data"]
            )
            
            # Generate strategic recommendations
            analysis_results["strategic_recommendations"] = self._generate_competitive_recommendations(
                analysis_results
            )
            
            # Cache results
            cache_key = f"competitors_{'-'.join(competitor_handles)}_{'-'.join(platforms)}"
            self.competitor_cache[cache_key] = analysis_results
            
            self.logger.info("Competitor analysis completed")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitor content: {e}")
            return self._get_error_response("analyze_competitor_content", str(e))

    async def identify_trending_topics(
        self,
        industry: str,
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify current trending topics in industry."""
        try:
            self.logger.info(f"Identifying trending topics in {industry} across {platforms}")
            
            trending_topics = []
            
            for platform in platforms:
                platform_trends = await self._get_platform_trending_topics(industry, platform)
                
                for trend in platform_trends:
                    # Check if topic already exists across platforms
                    existing_topic = next(
                        (t for t in trending_topics if t["topic"].lower() == trend["topic"].lower()),
                        None
                    )
                    
                    if existing_topic:
                        existing_topic["platforms"].append(platform)
                        existing_topic["total_mentions"] += trend.get("mentions", 0)
                        existing_topic["momentum"] = max(existing_topic["momentum"], trend.get("momentum", 0))
                    else:
                        trending_topics.append({
                            "topic": trend["topic"],
                            "platforms": [platform],
                            "total_mentions": trend.get("mentions", 0),
                            "momentum": trend.get("momentum", 0),
                            "category": trend.get("category", "general"),
                            "sentiment": trend.get("sentiment", "neutral"),
                            "related_hashtags": trend.get("hashtags", []),
                            "opportunity_score": self._calculate_opportunity_score(trend, industry)
                        })
            
            # Sort by momentum and opportunity score
            trending_topics.sort(
                key=lambda x: (x["momentum"] * x["opportunity_score"]), 
                reverse=True
            )
            
            # Cache results
            cache_key = f"trending_{industry}_{'-'.join(platforms)}"
            self.trending_cache[cache_key] = {
                "timestamp": datetime.now().isoformat(),
                "topics": trending_topics
            }
            
            self.logger.info(f"Identified {len(trending_topics)} trending topics")
            return trending_topics[:20]  # Return top 20 topics
            
        except Exception as e:
            self.logger.error(f"Error identifying trending topics: {e}")
            return []

    async def extract_best_practices(
        self,
        high_performing_posts: List[Dict]
    ) -> Dict[str, Any]:
        """Extract patterns from high-performing content."""
        try:
            self.logger.info(f"Extracting best practices from {len(high_performing_posts)} posts")
            
            best_practices = {
                "analysis_date": datetime.now().isoformat(),
                "posts_analyzed": len(high_performing_posts),
                "content_patterns": {},
                "timing_patterns": {},
                "engagement_patterns": {},
                "hashtag_patterns": {},
                "media_patterns": {},
                "actionable_insights": []
            }
            
            # Analyze content patterns
            best_practices["content_patterns"] = self._analyze_content_patterns(high_performing_posts)
            
            # Analyze timing patterns
            best_practices["timing_patterns"] = self._analyze_timing_patterns(high_performing_posts)
            
            # Analyze engagement patterns
            best_practices["engagement_patterns"] = self._analyze_engagement_patterns(high_performing_posts)
            
            # Analyze hashtag patterns
            best_practices["hashtag_patterns"] = self._analyze_hashtag_patterns(high_performing_posts)
            
            # Analyze media patterns
            best_practices["media_patterns"] = self._analyze_media_patterns(high_performing_posts)
            
            # Generate actionable insights
            best_practices["actionable_insights"] = self._generate_actionable_insights(best_practices)
            
            self.logger.info("Best practices extraction completed")
            return best_practices
            
        except Exception as e:
            self.logger.error(f"Error extracting best practices: {e}")
            return self._get_error_response("extract_best_practices", str(e))

    async def suggest_repurposing(
        self,
        original_content: Dict,
        target_platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Suggest how to repurpose content across platforms."""
        try:
            self.logger.info(f"Suggesting repurposing for {len(target_platforms)} platforms")
            
            repurposing_suggestions = []
            
            for platform in target_platforms:
                suggestion = await self._create_repurposing_suggestion(original_content, platform)
                repurposing_suggestions.append(suggestion)
            
            # Sort by feasibility score
            repurposing_suggestions.sort(
                key=lambda x: x["feasibility_score"], 
                reverse=True
            )
            
            self.logger.info(f"Generated {len(repurposing_suggestions)} repurposing suggestions")
            return repurposing_suggestions
            
        except Exception as e:
            self.logger.error(f"Error suggesting repurposing: {e}")
            return []

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

    def _detect_content_type(self, source: str) -> str:
        """Detect content type from source."""
        if source.startswith(("http://", "https://")):
            return "url"
        elif source.startswith("/") or "\\" in source or "." in source:
            return "file"
        else:
            return "text"

    async def _parse_url_content(self, url: str) -> Dict[str, Any]:
        """Parse content from URL."""
        
        # Detect platform from URL
        platform = self._detect_platform_from_url(url)
        
        try:
            # Use MCP tool to fetch content
            raw_content = await self._call_mcp_tool("fetch_url_content", {"url": url})
            
            if raw_content:
                parsed_data = self._extract_content_from_html(raw_content, platform)
            else:
                # Fallback parsing
                parsed_data = self._create_fallback_content(url, platform)
                
        except Exception as e:
            self.logger.warning(f"Failed to fetch URL content: {e}")
            parsed_data = self._create_fallback_content(url, platform)
        
        return parsed_data

    async def _parse_file_content(self, file_path: str) -> Dict[str, Any]:
        """Parse content from file."""
        
        try:
            # Determine file type
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension in ['txt', 'md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "content_type": "article",
                    "platform": "file",
                    "main_content": content,
                    "metadata": {
                        "file_type": file_extension,
                        "file_path": file_path
                    }
                }
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Error parsing file: {e}")
            return self._create_fallback_content(file_path, "file")

    async def _parse_text_content(self, text: str) -> Dict[str, Any]:
        """Parse raw text content."""
        
        return {
            "content_type": "post",
            "platform": "text",
            "main_content": text,
            "metadata": {
                "length": len(text),
                "word_count": len(text.split())
            }
        }

    def _detect_platform_from_url(self, url: str) -> str:
        """Detect social media platform from URL."""
        
        domain = urlparse(url).netloc.lower()
        
        for platform, patterns in self.parsers["url_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, domain):
                    return platform
        
        return "web"

    def _extract_content_from_html(self, html_content: str, platform: str) -> Dict[str, Any]:
        """Extract structured content from HTML."""
        
        # Basic HTML content extraction (would use proper HTML parser in production)
        main_content = re.sub(r'<[^>]+>', '', html_content)  # Strip HTML tags
        main_content = re.sub(r'\s+', ' ', main_content).strip()  # Clean whitespace
        
        return {
            "content_type": self._determine_content_type_from_text(main_content),
            "platform": platform,
            "main_content": main_content[:2000],  # Truncate for processing
            "metadata": {
                "extracted_from": "html",
                "original_length": len(html_content)
            }
        }

    def _determine_content_type_from_text(self, text: str) -> str:
        """Determine content type from text analysis."""
        
        if len(text) > 1000:
            return "article"
        elif len(text.split('\n')) > 5:
            return "thread"
        elif "video" in text.lower() or "watch" in text.lower():
            return "video"
        else:
            return "post"

    def _create_fallback_content(self, source: str, platform: str) -> Dict[str, Any]:
        """Create fallback content structure when parsing fails."""
        
        return {
            "content_type": "unknown",
            "platform": platform,
            "main_content": f"Content from: {source}",
            "metadata": {
                "parsing_status": "failed",
                "source": source
            },
            "key_points": [],
            "sentiment": "neutral",
            "topics": [],
            "repurpose_potential": {}
        }

    async def _enhance_parsed_content(self, parsed_data: Dict) -> Dict[str, Any]:
        """Enhance parsed content with additional analysis."""
        
        main_content = parsed_data.get("main_content", "")
        
        # Extract key points
        parsed_data["key_points"] = self._extract_key_points(main_content)
        
        # Analyze sentiment
        parsed_data["sentiment"] = await self._analyze_sentiment(main_content)
        
        # Extract topics
        parsed_data["topics"] = self._extract_topics(main_content)
        
        # Calculate repurposing potential
        parsed_data["repurpose_potential"] = self._calculate_repurpose_potential(parsed_data)
        
        return parsed_data

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content."""
        
        # Simple key point extraction (would use NLP in production)
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        for sentence in sentences[:5]:  # Top 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                key_points.append(sentence)
        
        return key_points

    async def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content."""
        
        try:
            # Use MCP tool for sentiment analysis
            sentiment_result = await self._call_mcp_tool("analyze_sentiment", {"text": content})
            if sentiment_result:
                return sentiment_result.get("sentiment", "neutral")
        except Exception:
            pass
        
        # Fallback sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content."""
        
        # Simple topic extraction (would use NLP/ML in production)
        common_topics = [
            "technology", "AI", "machine learning", "business", "marketing",
            "social media", "innovation", "startup", "productivity", "leadership"
        ]
        
        content_lower = content.lower()
        found_topics = []
        
        for topic in common_topics:
            if topic in content_lower:
                found_topics.append(topic)
        
        return found_topics[:5]  # Return top 5 topics

    def _calculate_repurpose_potential(self, parsed_data: Dict) -> Dict[str, float]:
        """Calculate repurposing potential for different platforms."""
        
        content_type = parsed_data.get("content_type", "post")
        main_content = parsed_data.get("main_content", "")
        platform = parsed_data.get("platform", "unknown")
        
        potential = {}
        
        # Base potential scores
        base_scores = {
            "twitter": 0.7,
            "linkedin": 0.6,
            "instagram": 0.5,
            "facebook": 0.6,
            "youtube": 0.3
        }
        
        for target_platform, base_score in base_scores.items():
            score = base_score
            
            # Adjust based on content type
            if content_type == "article":
                if target_platform == "linkedin":
                    score += 0.2
                elif target_platform == "twitter":
                    score += 0.1  # Can be broken into threads
            
            elif content_type == "video":
                if target_platform == "youtube":
                    score += 0.4
                elif target_platform == "instagram":
                    score += 0.3
            
            # Adjust based on content length
            word_count = len(main_content.split())
            if word_count > 500:  # Long content
                if target_platform in ["linkedin", "facebook"]:
                    score += 0.1
                elif target_platform == "twitter":
                    score += 0.2  # Good for threads
            
            # Don't repurpose to the same platform
            if target_platform == platform:
                score *= 0.3
            
            potential[target_platform] = min(score, 1.0)
        
        return potential

    async def _analyze_competitor_on_platform(
        self,
        competitor: str,
        platform: str,
        days_back: int
    ) -> Dict[str, Any]:
        """Analyze a specific competitor on a platform."""
        
        try:
            # Use MCP tool to get competitor data
            competitor_data = await self._call_mcp_tool("get_competitor_posts", {
                "handle": competitor,
                "platform": platform,
                "days_back": days_back
            })
            
            if competitor_data:
                return self._analyze_competitor_posts(competitor_data)
            
        except Exception as e:
            self.logger.warning(f"Failed to get competitor data for {competitor}: {e}")
        
        # Fallback analysis
        return self._create_mock_competitor_analysis(competitor, platform)

    def _analyze_competitor_posts(self, posts_data: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor posts data."""
        
        if not posts_data:
            return {"error": "No posts data available"}
        
        analysis = {
            "total_posts": len(posts_data),
            "avg_engagement": 0,
            "top_performing_posts": [],
            "common_hashtags": [],
            "posting_frequency": "unknown",
            "content_themes": [],
            "posting_times": []
        }
        
        # Calculate average engagement
        total_engagement = sum(post.get("engagement", 0) for post in posts_data)
        analysis["avg_engagement"] = total_engagement / len(posts_data) if posts_data else 0
        
        # Find top performing posts
        sorted_posts = sorted(posts_data, key=lambda x: x.get("engagement", 0), reverse=True)
        analysis["top_performing_posts"] = sorted_posts[:3]
        
        # Extract common hashtags
        all_hashtags = []
        for post in posts_data:
            all_hashtags.extend(post.get("hashtags", []))
        
        from collections import Counter
        hashtag_counts = Counter(all_hashtags)
        analysis["common_hashtags"] = [tag for tag, count in hashtag_counts.most_common(10)]
        
        return analysis

    def _create_mock_competitor_analysis(self, competitor: str, platform: str) -> Dict[str, Any]:
        """Create mock competitor analysis when real data is unavailable."""
        
        return {
            "total_posts": 25,
            "avg_engagement": 4.2,
            "top_performing_posts": [
                {"content": f"Sample high-performing post from {competitor}", "engagement": 8.5}
            ],
            "common_hashtags": ["#trending", "#content", "#social"],
            "posting_frequency": "daily",
            "content_themes": ["education", "engagement", "promotion"],
            "posting_times": ["09:00", "17:00"],
            "mock_data": True
        }

    async def _get_platform_trending_topics(self, industry: str, platform: str) -> List[Dict]:
        """Get trending topics for a platform in an industry."""
        
        try:
            # Use MCP tool to get trending topics
            trending_data = await self._call_mcp_tool("get_trending_topics", {
                "industry": industry,
                "platform": platform
            })
            
            if trending_data:
                return trending_data
                
        except Exception as e:
            self.logger.warning(f"Failed to get trending topics for {platform}: {e}")
        
        # Fallback trending topics
        return self._create_mock_trending_topics(industry, platform)

    def _create_mock_trending_topics(self, industry: str, platform: str) -> List[Dict]:
        """Create mock trending topics."""
        
        base_topics = {
            "technology": ["AI", "Machine Learning", "Blockchain", "Cloud Computing"],
            "business": ["Remote Work", "Digital Transformation", "Startup", "Leadership"],
            "marketing": ["Content Marketing", "Social Media", "SEO", "Influencer Marketing"]
        }
        
        topics = base_topics.get(industry, ["General Topic", "Industry News"])
        
        return [
            {
                "topic": topic,
                "mentions": 1000 + i * 100,
                "momentum": 0.8 - i * 0.1,
                "category": industry,
                "sentiment": "positive",
                "hashtags": [f"#{topic.replace(' ', '')}", f"#{industry}"]
            }
            for i, topic in enumerate(topics)
        ]

    def _calculate_opportunity_score(self, trend: Dict, industry: str) -> float:
        """Calculate opportunity score for a trend."""
        
        base_score = 0.5
        
        # Higher score for industry-relevant trends
        if industry.lower() in trend.get("topic", "").lower():
            base_score += 0.3
        
        # Higher score for positive sentiment
        if trend.get("sentiment") == "positive":
            base_score += 0.2
        
        # Score based on momentum
        momentum = trend.get("momentum", 0)
        base_score += momentum * 0.3
        
        return min(base_score, 1.0)

    def _generate_cross_platform_insights(self, competitor_data: Dict) -> Dict[str, Any]:
        """Generate insights across platforms."""
        
        insights = {
            "consistent_themes": [],
            "platform_specific_strategies": {},
            "engagement_leaders": {},
            "content_gap_opportunities": []
        }
        
        # Find consistent themes across competitors and platforms
        all_themes = []
        for competitor, platforms in competitor_data.items():
            for platform, data in platforms.items():
                if not data.get("mock_data"):
                    all_themes.extend(data.get("content_themes", []))
        
        from collections import Counter
        theme_counts = Counter(all_themes)
        insights["consistent_themes"] = [theme for theme, count in theme_counts.most_common(5)]
        
        return insights

    def _identify_competitive_gaps(self, competitor_data: Dict) -> List[str]:
        """Identify gaps in competitive landscape."""
        
        gaps = []
        
        # Analyze posting frequency gaps
        posting_frequencies = []
        for competitor, platforms in competitor_data.items():
            for platform, data in platforms.items():
                if data.get("posting_frequency"):
                    posting_frequencies.append(data["posting_frequency"])
        
        if "daily" not in posting_frequencies:
            gaps.append("Opportunity for daily posting frequency")
        
        # Add more gap analysis
        gaps.extend([
            "Underutilized video content format",
            "Limited interactive content (polls, Q&A)",
            "Insufficient cross-platform content adaptation"
        ])
        
        return gaps

    def _generate_competitive_recommendations(self, analysis: Dict) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        
        recommendations = []
        
        # Based on gaps
        gaps = analysis.get("competitive_gaps", [])
        for gap in gaps:
            if "video" in gap.lower():
                recommendations.append("Invest in video content strategy")
            elif "interactive" in gap.lower():
                recommendations.append("Increase interactive content (polls, Q&A)")
        
        # Based on successful patterns
        cross_platform = analysis.get("cross_platform_insights", {})
        consistent_themes = cross_platform.get("consistent_themes", [])
        
        if consistent_themes:
            recommendations.append(f"Focus on proven themes: {', '.join(consistent_themes[:3])}")
        
        # General recommendations
        recommendations.extend([
            "Monitor competitor posting times and adjust schedule",
            "Adapt high-performing competitor content formats",
            "Identify unique positioning opportunities"
        ])
        
        return recommendations

    def _analyze_content_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in high-performing content."""
        
        patterns = {
            "avg_length": 0,
            "common_words": [],
            "content_types": {},
            "structure_patterns": []
        }
        
        if not posts:
            return patterns
        
        # Analyze length
        lengths = [len(post.get("content", "")) for post in posts]
        patterns["avg_length"] = sum(lengths) / len(lengths)
        
        # Analyze common words
        all_words = []
        for post in posts:
            content = post.get("content", "").lower()
            words = re.findall(r'\b\w+\b', content)
            all_words.extend(words)
        
        from collections import Counter
        word_counts = Counter(all_words)
        patterns["common_words"] = [word for word, count in word_counts.most_common(10)]
        
        return patterns

    def _analyze_timing_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns in posts."""
        
        patterns = {
            "peak_hours": [],
            "peak_days": [],
            "posting_frequency": "unknown"
        }
        
        # Mock timing analysis (would use real timestamp data)
        patterns["peak_hours"] = ["09:00", "17:00", "20:00"]
        patterns["peak_days"] = ["Monday", "Wednesday", "Friday"]
        patterns["posting_frequency"] = "2-3 times per day"
        
        return patterns

    def _analyze_engagement_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement patterns."""
        
        patterns = {
            "avg_engagement_rate": 0,
            "high_engagement_factors": [],
            "engagement_distribution": {}
        }
        
        if posts:
            engagement_rates = [post.get("engagement_rate", 0) for post in posts]
            patterns["avg_engagement_rate"] = sum(engagement_rates) / len(engagement_rates)
        
        patterns["high_engagement_factors"] = [
            "Visual content (images/videos)",
            "Questions and polls",
            "Timely/trending topics",
            "Personal stories"
        ]
        
        return patterns

    def _analyze_hashtag_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze hashtag usage patterns."""
        
        patterns = {
            "avg_hashtag_count": 0,
            "most_effective_hashtags": [],
            "hashtag_performance": {}
        }
        
        all_hashtags = []
        hashtag_counts = []
        
        for post in posts:
            hashtags = post.get("hashtags", [])
            all_hashtags.extend(hashtags)
            hashtag_counts.append(len(hashtags))
        
        if hashtag_counts:
            patterns["avg_hashtag_count"] = sum(hashtag_counts) / len(hashtag_counts)
        
        from collections import Counter
        hashtag_frequency = Counter(all_hashtags)
        patterns["most_effective_hashtags"] = [tag for tag, count in hashtag_frequency.most_common(10)]
        
        return patterns

    def _analyze_media_patterns(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze media usage patterns."""
        
        patterns = {
            "media_usage_rate": 0,
            "preferred_media_types": [],
            "media_performance": {}
        }
        
        if not posts:
            return patterns
        
        posts_with_media = [post for post in posts if post.get("media")]
        patterns["media_usage_rate"] = len(posts_with_media) / len(posts)
        
        patterns["preferred_media_types"] = ["images", "videos", "infographics"]
        
        return patterns

    def _generate_actionable_insights(self, best_practices: Dict) -> List[str]:
        """Generate actionable insights from patterns."""
        
        insights = []
        
        # Content insights
        content_patterns = best_practices.get("content_patterns", {})
        avg_length = content_patterns.get("avg_length", 0)
        
        if avg_length > 0:
            insights.append(f"Optimal content length: ~{int(avg_length)} characters")
        
        # Timing insights
        timing_patterns = best_practices.get("timing_patterns", {})
        peak_hours = timing_patterns.get("peak_hours", [])
        
        if peak_hours:
            insights.append(f"Post during peak engagement times: {', '.join(peak_hours)}")
        
        # Hashtag insights
        hashtag_patterns = best_practices.get("hashtag_patterns", {})
        avg_hashtags = hashtag_patterns.get("avg_hashtag_count", 0)
        
        if avg_hashtags > 0:
            insights.append(f"Use approximately {int(avg_hashtags)} hashtags per post")
        
        # Media insights
        media_patterns = best_practices.get("media_patterns", {})
        media_rate = media_patterns.get("media_usage_rate", 0)
        
        if media_rate > 0.5:
            insights.append("Include visual content in majority of posts")
        
        return insights

    async def _create_repurposing_suggestion(
        self,
        original_content: Dict,
        target_platform: str
    ) -> Dict[str, Any]:
        """Create repurposing suggestion for a target platform."""
        
        original_platform = original_content.get("platform", "unknown")
        content_type = original_content.get("content_type", "post")
        
        suggestion = {
            "target_platform": target_platform,
            "original_platform": original_platform,
            "repurposing_type": self._determine_repurposing_type(content_type, target_platform),
            "feasibility_score": self._calculate_feasibility_score(original_content, target_platform),
            "required_adaptations": [],
            "content_suggestions": {},
            "effort_level": "medium"
        }
        
        # Generate specific adaptations needed
        suggestion["required_adaptations"] = self._get_required_adaptations(
            original_content, target_platform
        )
        
        # Generate content suggestions
        suggestion["content_suggestions"] = await self._generate_platform_content_suggestions(
            original_content, target_platform
        )
        
        # Determine effort level
        suggestion["effort_level"] = self._calculate_effort_level(suggestion)
        
        return suggestion

    def _determine_repurposing_type(self, content_type: str, target_platform: str) -> str:
        """Determine the type of repurposing needed."""
        
        if content_type == "article" and target_platform == "twitter":
            return "article_to_thread"
        elif content_type == "video" and target_platform == "instagram":
            return "video_adaptation"
        elif content_type == "post" and target_platform == "linkedin":
            return "post_expansion"
        else:
            return "general_adaptation"

    def _calculate_feasibility_score(self, original_content: Dict, target_platform: str) -> float:
        """Calculate feasibility score for repurposing."""
        
        repurpose_potential = original_content.get("repurpose_potential", {})
        base_score = repurpose_potential.get(target_platform, 0.5)
        
        # Adjust based on content quality
        if original_content.get("sentiment") == "positive":
            base_score += 0.1
        
        # Adjust based on topic relevance
        topics = original_content.get("topics", [])
        if len(topics) > 0:
            base_score += 0.1
        
        return min(base_score, 1.0)

    def _get_required_adaptations(self, original_content: Dict, target_platform: str) -> List[str]:
        """Get list of required adaptations for repurposing."""
        
        adaptations = []
        
        main_content = original_content.get("main_content", "")
        content_type = original_content.get("content_type", "post")
        
        # Platform-specific adaptations
        if target_platform == "twitter":
            if len(main_content) > 280:
                adaptations.append("Break into thread or shorten content")
            adaptations.append("Add relevant hashtags (max 3)")
            adaptations.append("Make content more conversational")
        
        elif target_platform == "linkedin":
            adaptations.append("Make tone more professional")
            adaptations.append("Add industry context")
            adaptations.append("Include call-to-action for networking")
        
        elif target_platform == "instagram":
            adaptations.append("Add high-quality visual content")
            adaptations.append("Use relevant hashtags (up to 30)")
            adaptations.append("Make content more visual/story-driven")
        
        # Content type specific adaptations
        if content_type == "article":
            adaptations.append("Extract key points for social format")
            adaptations.append("Create compelling hook/opening")
        
        return adaptations

    async def _generate_platform_content_suggestions(
        self,
        original_content: Dict,
        target_platform: str
    ) -> Dict[str, Any]:
        """Generate platform-specific content suggestions."""
        
        main_content = original_content.get("main_content", "")
        topics = original_content.get("topics", [])
        
        suggestions = {
            "adapted_text": "",
            "hashtags": [],
            "media_suggestions": [],
            "posting_tips": []
        }
        
        # Adapt text for platform
        if target_platform == "twitter":
            suggestions["adapted_text"] = self._adapt_for_twitter(main_content)
            suggestions["hashtags"] = [f"#{topic.replace(' ', '')}" for topic in topics[:3]]
            suggestions["posting_tips"] = ["Keep it conversational", "Engage with replies"]
        
        elif target_platform == "linkedin":
            suggestions["adapted_text"] = self._adapt_for_linkedin(main_content)
            suggestions["hashtags"] = [f"#{topic.replace(' ', '')}" for topic in topics[:5]]
            suggestions["posting_tips"] = ["Add professional context", "Tag relevant connections"]
        
        elif target_platform == "instagram":
            suggestions["adapted_text"] = self._adapt_for_instagram(main_content)
            suggestions["hashtags"] = [f"#{topic.replace(' ', '')}" for topic in topics[:10]]
            suggestions["media_suggestions"] = ["High-quality image", "Story graphics"]
            suggestions["posting_tips"] = ["Use visual storytelling", "Post during peak hours"]
        
        return suggestions

    def _adapt_for_twitter(self, content: str) -> str:
        """Adapt content for Twitter."""
        if len(content) <= 280:
            return content
        
        # Create thread starter
        return f"{content[:250]}... 🧵"

    def _adapt_for_linkedin(self, content: str) -> str:
        """Adapt content for LinkedIn."""
        return f"Professional insight: {content}\n\nWhat's your experience with this?"

    def _adapt_for_instagram(self, content: str) -> str:
        """Adapt content for Instagram."""
        return f"✨ {content[:100]}... ✨\n\n#inspiration #content"

    def _calculate_effort_level(self, suggestion: Dict) -> str:
        """Calculate effort level for repurposing."""
        
        adaptations_count = len(suggestion.get("required_adaptations", []))
        feasibility_score = suggestion.get("feasibility_score", 0.5)
        
        if feasibility_score > 0.8 and adaptations_count <= 3:
            return "low"
        elif feasibility_score > 0.6 and adaptations_count <= 5:
            return "medium"
        else:
            return "high"

    def _get_error_response(self, operation: str, error_message: str) -> Dict[str, Any]:
        """Get standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }