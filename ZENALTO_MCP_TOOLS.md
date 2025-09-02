# ZenAlto MCP Tools & Social Media Integration

## Overview

ZenAlto's MCP (Model Context Protocol) tools provide seamless integration with social media platforms, enabling AI agents to interact with Twitter/X, Instagram, LinkedIn, Facebook, and YouTube through standardized interfaces.

## MCP Architecture in ZenAlto

### Tool Categories

```
MCP Tools in ZenAlto
├── Social Media Tools
│   ├── Platform Posting Tools
│   ├── Analytics & Insights Tools
│   ├── Content Management Tools
│   └── Scheduling Tools
├── Content Intelligence Tools
│   ├── Intent Analysis Tools
│   ├── Content Generation Tools
│   └── Optimization Tools
└── Utility Tools
    ├── Media Processing Tools
    ├── Search & Discovery Tools
    └── Data Management Tools
```

## Social Media Server

**Location**: `tools/social_media_server.py`
**Purpose**: Primary interface for social media platform interactions

### Core Methods

```python
class SocialMediaServer:
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get current status of all social media platform connections"""

    async def post_content(self, platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to specified social media platform"""

    async def get_analytics(self, platform: str, post_id: Optional[str] = None,
                           date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get analytics data for posts or account performance"""

    async def upload_media(self, platform: str, media_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload media to social media platform"""

    async def schedule_post(self, platform: str, content: Dict[str, Any],
                           scheduled_time: str) -> Dict[str, Any]:
        """Schedule a post for future publishing"""

    async def get_content_suggestions(self, platform: str, topic: str) -> Dict[str, Any]:
        """Get AI-generated content suggestions for a topic"""
```

### Platform Integration Details

#### Twitter/X Integration

```python
class TwitterClient:
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials["api_key"]
        self.api_secret = credentials["api_secret"]
        self.access_token = credentials["access_token"]
        self.access_secret = credentials["access_secret"]
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_secret
        )

    async def post_tweet(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post a tweet with text and optional media"""
        try:
            # Prepare tweet content
            tweet_text = content["text"]
            media_ids = []

            # Upload media if provided
            if content.get("media_urls"):
                for media_url in content["media_urls"]:
                    media_id = await self.upload_media(media_url)
                    media_ids.append(media_id)

            # Post tweet
            response = await self.client.create_tweet(
                text=tweet_text,
                media_ids=media_ids if media_ids else None
            )

            return {
                "success": True,
                "post_id": response.data["id"],
                "url": f"https://twitter.com/i/status/{response.data['id']}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_tweet_analytics(self, tweet_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a tweet"""
        try:
            response = await self.client.get_tweet(
                tweet_id,
                tweet_fields=["public_metrics", "created_at"]
            )

            metrics = response.data["public_metrics"]

            return {
                "success": True,
                "analytics": {
                    "impressions": metrics.get("impression_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0)
                },
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

#### LinkedIn Integration

```python
class LinkedInClient:
    def __init__(self, credentials: Dict[str, str]):
        self.client_id = credentials["client_id"]
        self.client_secret = credentials["client_secret"]
        self.access_token = credentials["access_token"]

        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )

    async def post_to_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        try:
            # Get user profile URN
            profile_url = "https://api.linkedin.com/v2/people/~"
            async with self.session.get(profile_url) as response:
                profile_data = await response.json()
                author_urn = profile_data["id"]

            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{author_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content["text"]
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # Add media if provided
            if content.get("media_urls"):
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": content.get("media_description", "")
                        },
                        "media": content["media_urls"][0],  # Simplified - single image
                        "title": {
                            "text": content.get("media_title", "")
                        }
                    }
                ]

            # Post to LinkedIn
            post_url = "https://api.linkedin.com/v2/ugcPosts"
            async with self.session.post(post_url, json=post_data) as response:
                if response.status == 201:
                    post_response = await response.json()
                    return {
                        "success": True,
                        "post_id": post_response["id"],
                        "url": f"https://www.linkedin.com/feed/update/{post_response['id']}",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get("message", "Unknown error"),
                        "timestamp": datetime.now().isoformat()
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

#### Instagram Integration

```python
class InstagramClient:
    def __init__(self, credentials: Dict[str, str]):
        self.app_id = credentials["app_id"]
        self.app_secret = credentials["app_secret"]
        self.access_token = credentials["access_token"]
        self.user_id = credentials["user_id"]

    async def post_to_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Instagram"""
        try:
            # Upload media first
            media_url = "https://graph.instagram.com/{user_id}/media"
            media_data = {
                "image_url": content["media_urls"][0],  # Single image for simplicity
                "caption": content["text"],
                "access_token": self.access_token
            }

            async with aiohttp.ClientSession() as session:
                # Step 1: Create media container
                async with session.post(media_url.format(user_id=self.user_id), data=media_data) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": "Failed to create media container",
                            "timestamp": datetime.now().isoformat()
                        }

                    media_response = await response.json()
                    container_id = media_response["id"]

                # Step 2: Publish the media
                publish_url = f"https://graph.instagram.com/{self.user_id}/media_publish"
                publish_data = {
                    "creation_id": container_id,
                    "access_token": self.access_token
                }

                async with session.post(publish_url, data=publish_data) as response:
                    if response.status == 200:
                        publish_response = await response.json()
                        return {
                            "success": True,
                            "post_id": publish_response["id"],
                            "url": f"https://www.instagram.com/p/{publish_response['id']}",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to publish media",
                            "timestamp": datetime.now().isoformat()
                        }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

## Content Intent Analysis Server

**Location**: `tools/content_intent_server.py`
**Purpose**: AI-powered analysis of user content requests

### Key Features

```python
class ContentIntentServer:
    async def analyze_intent(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze user request to understand content intent"""

    async def learn_user_preferences(self, user_id: str, intent_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn user preferences from content creation history"""

    async def get_content_suggestions(self, user_id: str, topic: str, platform: str) -> Dict[str, Any]:
        """Get personalized content suggestions based on user preferences"""
```

### Intent Analysis Process

1. **Request Parsing**: Extract key elements from user input
2. **Context Integration**: Incorporate conversation history and user preferences
3. **Platform Detection**: Identify target social media platforms
4. **Content Classification**: Determine content type and requirements
5. **Intent Structuring**: Format analysis results for downstream processing

## MCP Tool Definitions

### Social Media Tools

```python
SOCIAL_MEDIA_TOOLS = [
    Tool(
        name="get_platform_status",
        description="Get current status of all social media platform connections",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="post_content",
        description="Post content to specified social media platform",
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["twitter", "instagram", "linkedin", "facebook", "youtube"],
                    "description": "Target social media platform"
                },
                "content": {
                    "type": "object",
                    "description": "Content data including text, media, and metadata",
                    "properties": {
                        "text": {"type": "string", "description": "Post text content"},
                        "media_urls": {"type": "array", "items": {"type": "string"}, "description": "Media file URLs"},
                        "hashtags": {"type": "array", "items": {"type": "string"}, "description": "Hashtags to include"},
                        "link": {"type": "string", "description": "Link to include in post"}
                    }
                }
            },
            "required": ["platform", "content"]
        }
    ),
    Tool(
        name="get_analytics",
        description="Get analytics data for posts or account performance",
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["twitter", "instagram", "linkedin", "facebook", "youtube"],
                    "description": "Target social media platform"
                },
                "post_id": {"type": "string", "description": "Specific post ID (optional)"},
                "date_range": {
                    "type": "object",
                    "description": "Date range for analytics (optional)",
                    "properties": {
                        "start_date": {"type": "string", "description": "Start date (ISO format)"},
                        "end_date": {"type": "string", "description": "End date (ISO format)"}
                    }
                }
            },
            "required": ["platform"]
        }
    ),
    Tool(
        name="schedule_post",
        description="Schedule a post for future publishing",
        inputSchema={
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["twitter", "instagram", "linkedin", "facebook", "youtube"],
                    "description": "Target social media platform"
                },
                "content": {
                    "type": "object",
                    "description": "Post content data",
                    "properties": {
                        "text": {"type": "string", "description": "Post text content"},
                        "media_urls": {"type": "array", "items": {"type": "string"}, "description": "Media file URLs"}
                    }
                },
                "scheduled_time": {
                    "type": "string",
                    "description": "Scheduled posting time (ISO format)"
                }
            },
            "required": ["platform", "content", "scheduled_time"]
        }
    )
]
```

### Content Analysis Tools

```python
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
```

## Platform-Specific Implementations

### Rate Limiting & Throttling

```python
class RateLimiter:
    def __init__(self):
        self.platform_limits = {
            "twitter": {"requests_per_hour": 300, "burst_limit": 50},
            "linkedin": {"requests_per_hour": 100, "burst_limit": 20},
            "instagram": {"requests_per_hour": 200, "burst_limit": 30},
            "facebook": {"requests_per_hour": 200, "burst_limit": 30},
            "youtube": {"requests_per_day": 10000, "burst_limit": 100}
        }

        self.request_history = defaultdict(list)

    async def check_rate_limit(self, platform: str) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        history = self.request_history[platform]

        # Remove old requests outside the time window
        cutoff_time = now - timedelta(hours=1)
        history[:] = [req_time for req_time in history if req_time > cutoff_time]

        # Check current request count
        limits = self.platform_limits[platform]
        if len(history) >= limits["requests_per_hour"]:
            return False

        # Add current request to history
        history.append(now)
        return True

    async def wait_for_rate_limit(self, platform: str):
        """Wait until rate limit allows next request"""
        while not await self.check_rate_limit(platform):
            await asyncio.sleep(60)  # Wait 1 minute before checking again
```

### Error Handling & Retry Logic

```python
class PlatformErrorHandler:
    async def handle_platform_error(self, platform: str, error: Exception, context: Dict) -> Dict:
        """
        Handle platform-specific errors with appropriate retry strategies

        Args:
            platform: The social media platform
            error: The exception that occurred
            context: Error context and retry information

        Returns:
            Recovery action or error response
        """

        retry_count = context.get("retry_count", 0)
        max_retries = context.get("max_retries", 3)

        if retry_count >= max_retries:
            return {
                "action": "fail",
                "error": f"Max retries exceeded for {platform}: {str(error)}"
            }

        # Platform-specific error handling
        if platform == "twitter":
            if "Rate limit exceeded" in str(error):
                delay = 60 * (2 ** retry_count)  # Exponential backoff
                return {
                    "action": "retry",
                    "delay": delay,
                    "reason": "Rate limit exceeded"
                }
            elif "Invalid authentication" in str(error):
                return {
                    "action": "reauthenticate",
                    "reason": "Authentication failed"
                }

        elif platform == "linkedin":
            if error.status == 429:  # Too Many Requests
                delay = 300  # 5 minutes
                return {
                    "action": "retry",
                    "delay": delay,
                    "reason": "Rate limit exceeded"
                }
            elif error.status == 401:  # Unauthorized
                return {
                    "action": "reauthenticate",
                    "reason": "Token expired"
                }

        elif platform == "instagram":
            if "OAuthAccessTokenException" in str(error):
                return {
                    "action": "reauthenticate",
                    "reason": "Access token invalid"
                }

        # Generic error handling
        return {
            "action": "retry",
            "delay": 30,
            "reason": f"Platform error: {str(error)}"
        }
```

### OAuth 2.0 Implementation

```python
class OAuthManager:
    def __init__(self):
        self.platform_configs = {
            "twitter": {
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "scopes": ["tweet.read", "tweet.write", "users.read"]
            },
            "linkedin": {
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "scopes": ["w_member_social", "r_liteprofile"]
            },
            "instagram": {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "scopes": ["user_profile", "user_media"]
            }
        }

    def generate_oauth_url(self, platform: str, state: str = None) -> str:
        """Generate OAuth authorization URL for platform"""
        config = self.platform_configs[platform]

        params = {
            "client_id": os.getenv(f"{platform.upper()}_CLIENT_ID"),
            "redirect_uri": os.getenv(f"{platform.upper()}_REDIRECT_URI"),
            "scope": " ".join(config["scopes"]),
            "response_type": "code",
            "state": state or self.generate_state()
        }

        if platform == "twitter":
            params["code_challenge"] = self.generate_code_challenge()
            params["code_challenge_method"] = "S256"

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config['auth_url']}?{query_string}"

    async def exchange_code_for_token(self, platform: str, code: str, code_verifier: str = None) -> Dict:
        """Exchange authorization code for access token"""
        config = self.platform_configs[platform]

        data = {
            "client_id": os.getenv(f"{platform.upper()}_CLIENT_ID"),
            "client_secret": os.getenv(f"{platform.upper()}_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv(f"{platform.upper()}_REDIRECT_URI")
        }

        if platform == "twitter" and code_verifier:
            data["code_verifier"] = code_verifier

        async with aiohttp.ClientSession() as session:
            async with session.post(config["token_url"], data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        "success": True,
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "expires_in": token_data.get("expires_in")
                    }
                else:
                    return {
                        "success": False,
                        "error": await response.text()
                    }

    def generate_state(self) -> str:
        """Generate random state parameter for OAuth"""
        return secrets.token_urlsafe(32)

    def generate_code_challenge(self) -> str:
        """Generate PKCE code challenge for Twitter OAuth"""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_challenge
```

## Testing & Mocking

### Platform API Mocking

```python
class MockPlatformClient:
    """Mock client for testing platform integrations"""

    def __init__(self, platform: str):
        self.platform = platform
        self.posts = []
        self.analytics = {}

    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock content posting"""
        post_id = f"mock_{self.platform}_{len(self.posts) + 1}"
        post = {
            "id": post_id,
            "platform": self.platform,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "url": f"https://{self.platform}.com/mock/{post_id}"
        }

        self.posts.append(post)

        # Generate mock analytics
        self.analytics[post_id] = {
            "impressions": random.randint(100, 1000),
            "engagements": random.randint(10, 100),
            "likes": random.randint(5, 50),
            "shares": random.randint(1, 20)
        }

        return {
            "success": True,
            "post_id": post_id,
            "url": post["url"],
            "timestamp": post["timestamp"]
        }

    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Mock analytics retrieval"""
        if post_id and post_id in self.analytics:
            return {
                "success": True,
                "analytics": self.analytics[post_id],
                "timestamp": datetime.now().isoformat()
            }
        elif not post_id:
            # Return aggregate analytics
            total_analytics = {
                "impressions": sum(a["impressions"] for a in self.analytics.values()),
                "engagements": sum(a["engagements"] for a in self.analytics.values()),
                "likes": sum(a["likes"] for a in self.analytics.values()),
                "shares": sum(a["shares"] for a in self.analytics.values())
            }
            return {
                "success": True,
                "analytics": total_analytics,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": f"Post {post_id} not found",
                "timestamp": datetime.now().isoformat()
            }
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_social_media_workflow():
    """Test complete social media posting workflow"""

    # Setup mock clients
    mock_clients = {
        "twitter": MockPlatformClient("twitter"),
        "linkedin": MockPlatformClient("linkedin")
    }

    # Test content posting
    content = {
        "text": "Exciting news about AI automation! #AI #Tech",
        "hashtags": ["#AI", "#Tech"],
        "media_urls": []
    }

    # Post to multiple platforms
    results = {}
    for platform, client in mock_clients.items():
        result = await client.post_content(content)
        results[platform] = result
        assert result["success"] == True
        assert "post_id" in result
        assert "url" in result

    # Verify analytics
    for platform, result in results.items():
        analytics = await mock_clients[platform].get_analytics(result["post_id"])
        assert analytics["success"] == True
        assert "impressions" in analytics["analytics"]
        assert "engagements" in analytics["analytics"]

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality"""

    rate_limiter = RateLimiter()

    # Test normal operation
    for i in range(10):
        allowed = await rate_limiter.check_rate_limit("twitter")
        assert allowed == True

    # Simulate rate limit exceeded
    # (This would require mocking time or using a test-specific rate limiter)
    pass

@pytest.mark.asyncio
async def test_oauth_flow():
    """Test OAuth 2.0 flow"""

    oauth_manager = OAuthManager()

    # Test URL generation
    auth_url = oauth_manager.generate_oauth_url("twitter")
    assert "twitter.com" in auth_url
    assert "client_id" in auth_url
    assert "code_challenge" in auth_url

    # Test token exchange (would require mocking HTTP responses)
    # token_result = await oauth_manager.exchange_code_for_token("twitter", "mock_code")
    # assert token_result["success"] == True
    pass
```

## Performance Monitoring

### Metrics Collection

```python
class PlatformMetrics:
    def __init__(self):
        self.metrics = defaultdict(dict)

    def record_request(self, platform: str, operation: str, success: bool, duration: float):
        """Record platform API request metrics"""
        key = f"{platform}_{operation}"

        if key not in self.metrics:
            self.metrics[key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_duration": 0.0,
                "average_duration": 0.0,
                "min_duration": float('inf'),
                "max_duration": 0.0
            }

        metrics = self.metrics[key]
        metrics["total_requests"] += 1

        if success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1

        metrics["total_duration"] += duration
        metrics["average_duration"] = metrics["total_duration"] / metrics["total_requests"]
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)

    def get_success_rate(self, platform: str, operation: str) -> float:
        """Get success rate for platform operation"""
        key = f"{platform}_{operation}"
        if key in self.metrics:
            metrics = self.metrics[key]
            total = metrics["total_requests"]
            successful = metrics["successful_requests"]
            return successful / total if total > 0 else 0.0
        return 0.0

    def get_average_duration(self, platform: str, operation: str) -> float:
        """Get average duration for platform operation"""
        key = f"{platform}_{operation}"
        return self.metrics[key].get("average_duration", 0.0)

    def get_platform_summary(self, platform: str) -> Dict[str, Any]:
        """Get summary metrics for platform"""
        platform_metrics = {
            key: value for key, value in self.metrics.items()
            if key.startswith(f"{platform}_")
        }

        if not platform_metrics:
            return {"error": f"No metrics found for {platform}"}

        summary = {
            "total_requests": sum(m["total_requests"] for m in platform_metrics.values()),
            "total_successful": sum(m["successful_requests"] for m in platform_metrics.values()),
            "total_failed": sum(m["failed_requests"] for m in platform_metrics.values()),
            "success_rate": 0.0,
            "average_duration": 0.0
        }

        if summary["total_requests"] > 0:
            summary["success_rate"] = summary["total_successful"] / summary["total_requests"]

        total_duration = sum(m["total_duration"] for m in platform_metrics.values())
        summary["average_duration"] = total_duration / summary["total_requests"] if summary["total_requests"] > 0 else 0.0

        return summary
```

### Health Monitoring

```python
class PlatformHealthMonitor:
    def __init__(self):
        self.health_status = {}
        self.last_check = {}

    async def check_platform_health(self, platform: str) -> Dict[str, Any]:
        """Check health status of platform integration"""
        try:
            # Perform basic connectivity check
            start_time = time.time()

            # This would be a lightweight API call to check platform status
            # For example, getting user profile or basic rate limit status
            health_check_result = await self.perform_health_check(platform)

            duration = time.time() - start_time

            health_data = {
                "platform": platform,
                "status": "healthy" if health_check_result["success"] else "unhealthy",
                "response_time": duration,
                "last_check": datetime.now().isoformat(),
                "details": health_check_result
            }

            self.health_status[platform] = health_data
            self.last_check[platform] = datetime.now()

            return health_data

        except Exception as e:
            health_data = {
                "platform": platform,
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

            self.health_status[platform] = health_data
            return health_data

    async def perform_health_check(self, platform: str) -> Dict[str, Any]:
        """Perform actual health check for platform"""
        # This would implement platform-specific health checks
        # For example, checking API rate limits, authentication status, etc.

        if platform == "twitter":
            # Check Twitter API status
            return await self.check_twitter_health()
        elif platform == "linkedin":
            # Check LinkedIn API status
            return await self.check_linkedin_health()
        elif platform == "instagram":
            # Check Instagram API status
            return await self.check_instagram_health()
        else:
            return {"success": False, "error": f"Health check not implemented for {platform}"}

    async def get_overall_health_status(self) -> Dict[str, Any]:
        """Get overall health status of all platforms"""
        overall_status = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {},
            "summary": {
                "total_platforms": len(self.health_status),
                "healthy_platforms": 0,
                "unhealthy_platforms": 0,
                "error_platforms": 0
            }
        }

        for platform, health in self.health_status.items():
            overall_status["platforms"][platform] = health

            if health["status"] == "healthy":
                overall_status["summary"]["healthy_platforms"] += 1
            elif health["status"] == "unhealthy":
                overall_status["summary"]["unhealthy_platforms"] += 1
            elif health["status"] == "error":
                overall_status["summary"]["error_platforms"] += 1

        return overall_status
```

This MCP tools documentation provides comprehensive coverage of ZenAlto's social media integration capabilities, including implementation details, error handling, testing strategies, and performance monitoring.</content>
<parameter name="filePath">/workspaces/DeepCode/ZENALTO_MCP_TOOLS.md
