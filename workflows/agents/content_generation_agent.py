"""
Content Generation Agent for ZenAlto Social Media Management

Generates optimized social media content based on strategy.

Responsibilities:
- Platform-specific content creation
- Tone and style adaptation
- Media recommendations
- A/B testing variants
- Content optimization
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime
import uuid
import re


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

    def __init__(
        self,
        mcp_agent,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        self.platform_limits = self._load_platform_limits()
        
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
        self.variant_templates = {}
    
    def _load_platform_limits(self) -> Dict[str, Any]:
        """Load platform-specific limits and requirements."""
        return {
            "twitter": {
                "max_length": 280,
                "hashtag_limit": 3,
                "optimal_hashtags": 2,
                "media_types": ["image", "gif", "video"],
                "max_images": 4,
                "max_video_length": 140
            },
            "instagram": {
                "max_length": 2200,
                "hashtag_limit": 30,
                "optimal_hashtags": 8,
                "media_types": ["image", "video", "carousel", "reel"],
                "max_images": 10,
                "max_video_length": 60
            },
            "linkedin": {
                "max_length": 3000,
                "hashtag_limit": 5,
                "optimal_hashtags": 3,
                "media_types": ["image", "video", "document"],
                "max_images": 9,
                "max_video_length": 600
            },
            "facebook": {
                "max_length": 63206,
                "hashtag_limit": 10,
                "optimal_hashtags": 5,
                "media_types": ["image", "video", "link"],
                "max_images": 10,
                "max_video_length": 240
            },
            "youtube": {
                "max_length": 5000,
                "hashtag_limit": 15,
                "optimal_hashtags": 10,
                "media_types": ["video", "thumbnail"],
                "max_video_length": 86400  # 24 hours
            }
        }

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
        try:
            self.logger.info(f"Generating content with {tone} tone for strategy")
            
            optimization_params = optimization_params or {}
            platforms = strategy.get("platforms", {})
            
            generated_content = {}
            
            for platform, platform_config in platforms.items():
                self.logger.info(f"Generating content for {platform}")
                
                platform_content = await self._generate_platform_content(
                    platform,
                    platform_config,
                    strategy,
                    tone,
                    optimization_params
                )
                
                generated_content[platform] = platform_content
            
            # Generate A/B testing variants if requested
            variants_info = {"a_b_testing": False, "variants_generated": 0}
            if optimization_params.get("generate_variants", False):
                variants_info = await self._generate_content_variants(generated_content)
            
            # Calculate quality scores
            quality_scores = await self._calculate_quality_scores(generated_content, strategy)
            
            result = {
                "content_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "content": generated_content,
                "variants": variants_info,
                "quality_scores": quality_scores,
                "tone_used": tone,
                "strategy_id": strategy.get("strategy_id"),
                "success": True
            }
            
            # Cache generated content
            self.content_cache[result["content_id"]] = result
            
            self.logger.info(f"Content generation completed for {len(platforms)} platforms")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            return self._get_error_response("generate", str(e))

    async def adapt_tone(
        self,
        content: str,
        from_tone: str,
        to_tone: str
    ) -> str:
        """Adapt content tone (professional, casual, humorous, educational)."""
        try:
            self.logger.info(f"Adapting tone from {from_tone} to {to_tone}")
            
            # Use MCP tool for tone adaptation
            try:
                adapted_content = await self._call_mcp_tool("social_media_adapt_tone", {
                    "content": content,
                    "from_tone": from_tone,
                    "to_tone": to_tone
                })
                
                if adapted_content:
                    return adapted_content
            except Exception as e:
                self.logger.warning(f"MCP tone adaptation failed: {e}")
            
            # Fallback to rule-based adaptation
            return self._rule_based_tone_adaptation(content, from_tone, to_tone)
            
        except Exception as e:
            self.logger.error(f"Error adapting tone: {e}")
            return content  # Return original content if adaptation fails

    async def generate_variants(
        self,
        base_content: str,
        num_variants: int = 3
    ) -> List[str]:
        """Generate A/B testing variants."""
        try:
            self.logger.info(f"Generating {num_variants} content variants")
            
            variants = []
            
            for i in range(num_variants):
                variant = await self._create_content_variant(base_content, i + 1)
                variants.append(variant)
            
            self.logger.info(f"Generated {len(variants)} variants successfully")
            return variants
            
        except Exception as e:
            self.logger.error(f"Error generating variants: {e}")
            return [base_content]  # Return original if variants fail

    async def optimize_for_engagement(
        self,
        content: Dict,
        platform: str,
        audience_data: Optional[Dict] = None
    ) -> Dict:
        """Optimize content for maximum engagement."""
        try:
            self.logger.info(f"Optimizing content for engagement on {platform}")
            
            optimized_content = content.copy()
            optimizations_applied = []
            
            # Get platform limits
            platform_limits = self.platform_limits.get(platform, {})
            
            # Optimize text content
            if "text" in content:
                optimized_text, text_optimizations = await self._optimize_text_for_engagement(
                    content["text"], platform, audience_data
                )
                optimized_content["text"] = optimized_text
                optimizations_applied.extend(text_optimizations)
            
            # Optimize hashtags
            if "hashtags" in content:
                optimized_hashtags = self._optimize_hashtags(
                    content["hashtags"], platform_limits
                )
                optimized_content["hashtags"] = optimized_hashtags
                if optimized_hashtags != content["hashtags"]:
                    optimizations_applied.append("hashtag_optimization")
            
            # Add engagement elements
            engagement_elements = self._add_engagement_elements(platform, audience_data)
            if engagement_elements:
                optimized_content.update(engagement_elements)
                optimizations_applied.append("engagement_elements_added")
            
            # Add optimization metadata
            optimized_content["optimizations"] = optimizations_applied
            optimized_content["optimization_score"] = self._calculate_optimization_score(optimizations_applied)
            
            self.logger.info(f"Content optimized with {len(optimizations_applied)} improvements")
            return optimized_content
            
        except Exception as e:
            self.logger.error(f"Error optimizing content: {e}")
            return content

    async def validate_content(
        self,
        content: Dict,
        platform: str
    ) -> Tuple[bool, List[str]]:
        """Validate content meets platform requirements."""
        try:
            self.logger.info(f"Validating content for {platform}")
            
            validation_errors = []
            platform_limits = self.platform_limits.get(platform, {})
            
            # Validate text length
            if "text" in content:
                text_length = len(content["text"])
                max_length = platform_limits.get("max_length", 1000)
                
                if text_length > max_length:
                    validation_errors.append(
                        f"Text too long: {text_length} characters (max: {max_length})"
                    )
            
            # Validate hashtag count
            if "hashtags" in content:
                hashtag_count = len(content["hashtags"])
                max_hashtags = platform_limits.get("hashtag_limit", 10)
                
                if hashtag_count > max_hashtags:
                    validation_errors.append(
                        f"Too many hashtags: {hashtag_count} (max: {max_hashtags})"
                    )
            
            # Validate media
            if "media" in content:
                media_errors = self._validate_media(content["media"], platform_limits)
                validation_errors.extend(media_errors)
            
            # Platform-specific validations
            platform_errors = self._platform_specific_validation(content, platform)
            validation_errors.extend(platform_errors)
            
            is_valid = len(validation_errors) == 0
            
            self.logger.info(f"Content validation: {'PASSED' if is_valid else 'FAILED'}")
            return is_valid, validation_errors
            
        except Exception as e:
            self.logger.error(f"Error validating content: {e}")
            return False, [f"Validation error: {str(e)}"]

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

    async def _generate_platform_content(
        self,
        platform: str,
        platform_config: Dict,
        strategy: Dict,
        tone: str,
        optimization_params: Dict
    ) -> Dict[str, Any]:
        """Generate content for a specific platform."""
        
        platform_limits = self.platform_limits.get(platform, {})
        intent_analysis = strategy.get("intent_analysis", {})
        content_themes = strategy.get("content_themes", ["general"])
        hashtag_strategy = strategy.get("hashtag_strategy", {})
        
        # Generate main content text
        content_text = await self._generate_content_text(
            platform, platform_config, intent_analysis, tone
        )
        
        # Select appropriate hashtags
        hashtags = self._select_hashtags(hashtag_strategy, platform_limits)
        
        # Determine media recommendations
        media_suggestions = self._suggest_media(platform, content_themes, intent_analysis)
        
        # Generate posts (single or thread)
        posts = []
        
        if platform_config.get("thread", False) and len(content_text) > platform_limits.get("max_length", 280):
            # Create thread
            thread_posts = self._create_thread(content_text, platform_limits)
            for i, thread_text in enumerate(thread_posts):
                post = {
                    "text": thread_text,
                    "media": media_suggestions if i == 0 else [],  # Media only on first post
                    "hashtags": hashtags if i == 0 else [],  # Hashtags only on first post
                    "thread_position": i + 1,
                    "character_count": len(thread_text)
                }
                posts.append(post)
        else:
            # Single post
            # Truncate if necessary
            max_length = platform_limits.get("max_length", 280)
            if len(content_text) > max_length:
                content_text = content_text[:max_length-3] + "..."
            
            post = {
                "text": content_text,
                "media": media_suggestions,
                "hashtags": hashtags,
                "thread_position": 1,
                "character_count": len(content_text)
            }
            
            # Add platform-specific fields
            if platform == "linkedin" and platform_config.get("article", False):
                post["format"] = "article"
                post["reading_time"] = f"{max(1, len(content_text) // 200)} min"
            
            posts.append(post)
        
        # Generate optimizations applied
        optimizations = self._get_platform_optimizations(platform, posts)
        
        return {
            "posts": posts,
            "optimizations": optimizations,
            "platform_config": platform_config
        }

    async def _generate_content_text(
        self,
        platform: str,
        platform_config: Dict,
        intent_analysis: Dict,
        tone: str
    ) -> str:
        """Generate the main content text for a platform."""
        
        # Use MCP tool for content generation
        try:
            content_prompt = self._create_content_prompt(platform, intent_analysis, tone)
            
            generated_text = await self._call_mcp_tool("social_media_generate_content", {
                "prompt": content_prompt,
                "platform": platform,
                "tone": tone,
                "max_length": platform_config.get("max_length", 280)
            })
            
            if generated_text:
                return generated_text
                
        except Exception as e:
            self.logger.warning(f"MCP content generation failed: {e}")
        
        # Fallback to template-based generation
        return self._template_based_generation(platform, intent_analysis, tone)

    def _create_content_prompt(self, platform: str, intent_analysis: Dict, tone: str) -> str:
        """Create prompt for content generation."""
        intent_summary = intent_analysis.get("intent_summary", "Create engaging content")
        topics = intent_analysis.get("topics", [])
        audience = intent_analysis.get("audience", "general audience")
        
        prompt = f"""
        Create {tone} content for {platform} that:
        - Addresses: {intent_summary}
        - Covers topics: {', '.join(topics) if topics else 'general interest'}
        - Targets: {audience}
        - Optimized for {platform} best practices
        """
        
        return prompt.strip()

    def _template_based_generation(self, platform: str, intent_analysis: Dict, tone: str) -> str:
        """Generate content using templates as fallback."""
        
        intent_summary = intent_analysis.get("intent_summary", "Share interesting content")
        topics = intent_analysis.get("topics", ["technology"])
        
        templates = {
            "professional": "Exploring {topic}: {summary} What are your thoughts on this?",
            "casual": "Just discovered something cool about {topic}! {summary} 🤔",
            "humorous": "So apparently {topic} is a thing... {summary} Who knew? 😄",
            "educational": "Let's dive into {topic}: {summary} Key takeaways in thread below 👇"
        }
        
        template = templates.get(tone, templates["professional"])
        topic = topics[0] if topics else "this topic"
        
        return template.format(topic=topic, summary=intent_summary)

    def _select_hashtags(self, hashtag_strategy: Dict, platform_limits: Dict) -> List[str]:
        """Select appropriate hashtags for the platform."""
        all_hashtags = []
        
        # Add primary hashtags
        all_hashtags.extend(hashtag_strategy.get("primary", []))
        
        # Add secondary hashtags
        all_hashtags.extend(hashtag_strategy.get("secondary", []))
        
        # Add trending hashtags
        all_hashtags.extend(hashtag_strategy.get("trending", []))
        
        # Limit to platform's optimal number
        optimal_count = platform_limits.get("optimal_hashtags", 3)
        
        return all_hashtags[:optimal_count]

    def _suggest_media(self, platform: str, content_themes: List[str], intent_analysis: Dict) -> List[str]:
        """Suggest media based on platform and content."""
        media_suggestions = []
        
        platform_media = self.platform_limits.get(platform, {}).get("media_types", ["image"])
        
        # Suggest based on content themes
        if "education" in content_themes and "image" in platform_media:
            media_suggestions.append("infographic")
        
        if "engagement" in content_themes and "video" in platform_media:
            media_suggestions.append("short_video")
        
        if platform == "instagram":
            media_suggestions.append("high_quality_image")
        
        return media_suggestions[:2]  # Limit suggestions

    def _create_thread(self, content_text: str, platform_limits: Dict) -> List[str]:
        """Break content into thread posts."""
        max_length = platform_limits.get("max_length", 280) - 20  # Reserve space for numbering
        
        # Split by sentences
        sentences = re.split(r'[.!?]+', content_text)
        thread_posts = []
        current_post = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_post + sentence) < max_length:
                current_post += sentence + ". "
            else:
                if current_post:
                    thread_posts.append(current_post.strip())
                current_post = sentence + ". "
        
        # Add remaining content
        if current_post:
            thread_posts.append(current_post.strip())
        
        # Add thread numbering
        numbered_posts = []
        for i, post in enumerate(thread_posts):
            if i == 0:
                numbered_posts.append(f"{post} 🧵")
            else:
                numbered_posts.append(f"{i+1}/{len(thread_posts)} {post}")
        
        return numbered_posts

    def _get_platform_optimizations(self, platform: str, posts: List[Dict]) -> List[str]:
        """Get list of optimizations applied for platform."""
        optimizations = []
        
        # Check for emoji usage
        for post in posts:
            if any(char for char in post["text"] if ord(char) > 127):  # Simple emoji check
                optimizations.append("emoji_usage")
                break
        
        # Check for hashtag placement
        for post in posts:
            if post.get("hashtags"):
                optimizations.append("hashtag_placement")
                break
        
        # Platform-specific optimizations
        if platform == "twitter" and len(posts) > 1:
            optimizations.append("thread_creation")
        
        if platform == "linkedin" and any(post.get("format") == "article" for post in posts):
            optimizations.append("article_format")
        
        return optimizations

    async def _generate_content_variants(self, content: Dict) -> Dict[str, Any]:
        """Generate A/B testing variants for all platform content."""
        variants_generated = 0
        
        for platform, platform_content in content.items():
            for post in platform_content.get("posts", []):
                original_text = post["text"]
                variants = await self.generate_variants(original_text, 2)
                post["variants"] = variants
                variants_generated += len(variants)
        
        return {
            "a_b_testing": True,
            "variants_generated": variants_generated
        }

    async def _create_content_variant(self, base_content: str, variant_number: int) -> str:
        """Create a single content variant."""
        # Simple variant generation strategies
        
        if variant_number == 1:
            # Add question variant
            return f"{base_content} What do you think?"
        
        elif variant_number == 2:
            # Add call-to-action variant
            return f"{base_content} Share your experience in the comments!"
        
        elif variant_number == 3:
            # Emoji variant
            return f"✨ {base_content} 🚀"
        
        else:
            # Default variant with slight rewording
            return base_content.replace(".", "!").replace("interesting", "fascinating")

    async def _calculate_quality_scores(self, content: Dict, strategy: Dict) -> Dict[str, float]:
        """Calculate quality scores for generated content."""
        
        total_engagement_potential = 0
        total_clarity = 0
        total_platform_fit = 0
        
        total_posts = 0
        for platform, platform_content in content.items():
            for post in platform_content.get("posts", []):
                platform_limits = self.platform_limits.get(platform, {})
                
                # Engagement potential (based on hashtags, emojis, questions)
                engagement_score = self._calculate_engagement_potential(post, platform)
                total_engagement_potential += engagement_score
                
                # Clarity (based on readability)
                clarity_score = self._calculate_clarity_score(post["text"])
                total_clarity += clarity_score
                
                # Platform fit (based on length, format adherence)
                platform_fit_score = self._calculate_platform_fit(post, platform, platform_limits)
                total_platform_fit += platform_fit_score
                
                total_posts += 1
        
        if total_posts == 0:
            return {"engagement_potential": 0.0, "clarity": 0.0, "platform_fit": 0.0}
        
        return {
            "engagement_potential": round(total_engagement_potential / total_posts, 1),
            "clarity": round(total_clarity / total_posts, 1),
            "platform_fit": round(total_platform_fit / total_posts, 1)
        }

    def _calculate_engagement_potential(self, post: Dict, platform: str) -> float:
        """Calculate engagement potential score for a post."""
        score = 5.0  # Base score
        
        text = post.get("text", "")
        
        # Boost for questions
        if "?" in text:
            score += 1.5
        
        # Boost for hashtags
        if post.get("hashtags"):
            score += 1.0
        
        # Boost for emojis
        if any(ord(char) > 127 for char in text):
            score += 1.0
        
        # Boost for media
        if post.get("media"):
            score += 1.5
        
        # Platform-specific boosts
        if platform == "twitter" and post.get("thread_position", 1) == 1:
            score += 0.5
        
        return min(score, 10.0)

    def _calculate_clarity_score(self, text: str) -> float:
        """Calculate clarity score based on readability."""
        # Simple readability metrics
        words = text.split()
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return 5.0
        
        avg_words_per_sentence = len(words) / sentences
        
        # Optimal range is 10-20 words per sentence
        if 10 <= avg_words_per_sentence <= 20:
            clarity_score = 9.0
        elif avg_words_per_sentence < 10:
            clarity_score = 8.0  # Too short
        else:
            clarity_score = 7.0  # Too long
        
        return clarity_score

    def _calculate_platform_fit(self, post: Dict, platform: str, platform_limits: Dict) -> float:
        """Calculate how well the post fits platform requirements."""
        score = 8.0  # Base score
        
        text_length = post.get("character_count", len(post.get("text", "")))
        max_length = platform_limits.get("max_length", 1000)
        
        # Length optimization
        if text_length <= max_length * 0.8:  # Good length
            score += 1.5
        elif text_length <= max_length:  # Acceptable length
            score += 0.5
        else:  # Too long
            score -= 2.0
        
        # Hashtag optimization
        hashtag_count = len(post.get("hashtags", []))
        optimal_hashtags = platform_limits.get("optimal_hashtags", 3)
        
        if hashtag_count == optimal_hashtags:
            score += 1.0
        elif hashtag_count <= platform_limits.get("hashtag_limit", 10):
            score += 0.5
        
        return min(max(score, 0), 10.0)

    async def _optimize_text_for_engagement(
        self,
        text: str,
        platform: str,
        audience_data: Optional[Dict]
    ) -> Tuple[str, List[str]]:
        """Optimize text content for engagement."""
        optimized_text = text
        optimizations = []
        
        # Add question if none exists
        if "?" not in text and platform in ["twitter", "facebook"]:
            optimized_text += " What are your thoughts?"
            optimizations.append("question_added")
        
        # Add emojis if platform supports them
        if platform in ["twitter", "instagram"] and not any(ord(char) > 127 for char in text):
            optimized_text = f"✨ {optimized_text}"
            optimizations.append("emoji_added")
        
        # Optimize for readability
        if len(text.split()) > 25:  # Long text
            # Add line breaks for readability
            sentences = text.split('. ')
            if len(sentences) > 2:
                optimized_text = '. \n\n'.join(sentences)
                optimizations.append("readability_improved")
        
        return optimized_text, optimizations

    def _optimize_hashtags(self, hashtags: List[str], platform_limits: Dict) -> List[str]:
        """Optimize hashtag selection for platform."""
        optimal_count = platform_limits.get("optimal_hashtags", 3)
        max_count = platform_limits.get("hashtag_limit", 10)
        
        # Ensure we don't exceed limits
        if len(hashtags) > max_count:
            hashtags = hashtags[:max_count]
        
        # Optimize to ideal count
        if len(hashtags) > optimal_count:
            # Keep most relevant hashtags (first ones are usually most relevant)
            hashtags = hashtags[:optimal_count]
        
        return hashtags

    def _add_engagement_elements(self, platform: str, audience_data: Optional[Dict]) -> Dict[str, Any]:
        """Add platform-specific engagement elements."""
        elements = {}
        
        if platform == "twitter":
            elements["call_to_action"] = "Retweet if you agree!"
        elif platform == "instagram":
            elements["story_suggestion"] = "Share to your story!"
        elif platform == "linkedin":
            elements["professional_cta"] = "Let's connect and discuss!"
        
        return elements

    def _calculate_optimization_score(self, optimizations: List[str]) -> float:
        """Calculate optimization score based on applied optimizations."""
        base_score = 5.0
        optimization_values = {
            "emoji_usage": 1.0,
            "hashtag_placement": 1.0,
            "question_added": 1.5,
            "engagement_elements_added": 1.0,
            "readability_improved": 1.0
        }
        
        for optimization in optimizations:
            base_score += optimization_values.get(optimization, 0.5)
        
        return min(base_score, 10.0)

    def _rule_based_tone_adaptation(self, content: str, from_tone: str, to_tone: str) -> str:
        """Rule-based tone adaptation as fallback."""
        adapted_content = content
        
        if to_tone == "casual":
            adapted_content = adapted_content.replace(".", "!")
            adapted_content = f"Hey! {adapted_content} 😊"
        elif to_tone == "professional":
            adapted_content = adapted_content.replace("!", ".")
            adapted_content = adapted_content.replace(" 😊", "")
        elif to_tone == "humorous":
            adapted_content = f"{adapted_content} 😄"
        
        return adapted_content

    def _validate_media(self, media: List[str], platform_limits: Dict) -> List[str]:
        """Validate media against platform requirements."""
        errors = []
        
        max_images = platform_limits.get("max_images", 4)
        if len(media) > max_images:
            errors.append(f"Too many media items: {len(media)} (max: {max_images})")
        
        supported_types = platform_limits.get("media_types", ["image"])
        for media_item in media:
            # Simple media type detection
            if "video" in media_item.lower() and "video" not in supported_types:
                errors.append("Video not supported on this platform")
        
        return errors

    def _platform_specific_validation(self, content: Dict, platform: str) -> List[str]:
        """Platform-specific content validation."""
        errors = []
        
        if platform == "twitter":
            # Twitter-specific validations
            if content.get("thread_position", 1) > 25:  # Twitter thread limit
                errors.append("Thread too long (max 25 tweets)")
        
        elif platform == "instagram":
            # Instagram requires visual content
            if not content.get("media"):
                errors.append("Instagram posts require visual content")
        
        elif platform == "linkedin":
            # LinkedIn professional content validation
            text = content.get("text", "")
            if len(text.split()) < 10:
                errors.append("LinkedIn content should be more substantial (minimum 10 words)")
        
        return errors

    def _get_error_response(self, operation: str, error_message: str) -> Dict[str, Any]:
        """Get standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }