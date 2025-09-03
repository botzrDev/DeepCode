# Development Assignment #9: Social Media API Clients Implementation

## Priority: 🟡 MEDIUM - Week 3

## Objective
Implement actual API client libraries for all supported social media platforms (Twitter/X, LinkedIn, Instagram, Facebook, YouTube) to enable real platform connectivity beyond the MCP mock implementations.

## Background
Current MCP servers provide the interface but lack actual platform API implementations. We need real API clients to connect to social media platforms.

## Deliverables

Create API client implementations in `social_apis/` directory.

### 1. Twitter/X Client
**File**: `social_apis/twitter_client.py`

```python
import tweepy
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

class TwitterClient:
    """
    Twitter/X API v2 client implementation.
    
    Features:
    - OAuth 2.0 authentication
    - Tweet posting and threading
    - Media upload
    - Analytics retrieval
    - Rate limit handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Twitter client.
        
        Config should include:
        - api_key
        - api_secret
        - access_token
        - access_token_secret
        - bearer_token (for app-only auth)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.api = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Tweepy client with v2 API."""
        try:
            # V2 client for new endpoints
            self.client = tweepy.Client(
                bearer_token=self.config.get('bearer_token'),
                consumer_key=self.config.get('api_key'),
                consumer_secret=self.config.get('api_secret'),
                access_token=self.config.get('access_token'),
                access_token_secret=self.config.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            
            # V1.1 API for media upload (still required)
            auth = tweepy.OAuth1UserHandler(
                self.config.get('api_key'),
                self.config.get('api_secret'),
                self.config.get('access_token'),
                self.config.get('access_token_secret')
            )
            self.api = tweepy.API(auth)
            
            self.logger.info("Twitter client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter client: {e}")
            raise
    
    async def post_tweet(
        self,
        text: str,
        media_ids: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        quote_tweet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a tweet.
        
        Returns:
        {
            "success": bool,
            "tweet_id": str,
            "url": str,
            "created_at": datetime,
            "error": Optional[str]
        }
        """
        try:
            # Post tweet with v2 API
            response = await asyncio.to_thread(
                self.client.create_tweet,
                text=text,
                media_ids=media_ids,
                in_reply_to_tweet_id=reply_to,
                quote_tweet_id=quote_tweet_id
            )
            
            tweet_data = response.data
            tweet_id = tweet_data['id']
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "url": f"https://twitter.com/i/web/status/{tweet_id}",
                "created_at": datetime.now(),
                "text": text
            }
            
        except tweepy.TooManyRequests as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later."
            }
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_thread(
        self,
        tweets: List[str],
        media_per_tweet: Optional[Dict[int, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
            media_per_tweet: Dict mapping tweet index to media IDs
        
        Returns:
        {
            "success": bool,
            "thread_id": str,
            "tweet_ids": List[str],
            "urls": List[str],
            "error": Optional[str]
        }
        """
        tweet_ids = []
        urls = []
        reply_to = None
        
        try:
            for idx, tweet_text in enumerate(tweets):
                media_ids = media_per_tweet.get(idx) if media_per_tweet else None
                
                result = await self.post_tweet(
                    text=tweet_text,
                    media_ids=media_ids,
                    reply_to=reply_to
                )
                
                if not result["success"]:
                    raise Exception(f"Failed to post tweet {idx + 1}: {result['error']}")
                
                tweet_ids.append(result["tweet_id"])
                urls.append(result["url"])
                reply_to = result["tweet_id"]  # Reply to previous tweet
                
                # Add delay between tweets to avoid rate limiting
                if idx < len(tweets) - 1:
                    await asyncio.sleep(2)
            
            return {
                "success": True,
                "thread_id": tweet_ids[0],
                "tweet_ids": tweet_ids,
                "urls": urls
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post thread: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_tweet_ids": tweet_ids
            }
    
    async def upload_media(
        self,
        media_path: str,
        media_type: str = "image",
        alt_text: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload media and return media ID.
        
        Args:
            media_path: Path to media file
            media_type: "image" or "video"
            alt_text: Alternative text for accessibility
        
        Returns:
            Media ID string or None if failed
        """
        try:
            # Use v1.1 API for media upload
            if media_type == "video":
                media = await asyncio.to_thread(
                    self.api.media_upload,
                    filename=media_path,
                    media_category="tweet_video"
                )
            else:
                media = await asyncio.to_thread(
                    self.api.media_upload,
                    filename=media_path
                )
            
            # Add alt text if provided
            if alt_text and media:
                await asyncio.to_thread(
                    self.api.create_media_metadata,
                    media_id=media.media_id_string,
                    alt_text=alt_text
                )
            
            return media.media_id_string
            
        except Exception as e:
            self.logger.error(f"Failed to upload media: {e}")
            return None
    
    async def get_analytics(
        self,
        tweet_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for tweets.
        
        Args:
            tweet_ids: List of tweet IDs
            metrics: Specific metrics to retrieve
        
        Returns:
        {
            "metrics": {
                "tweet_id": {
                    "impressions": int,
                    "engagements": int,
                    "retweets": int,
                    "likes": int,
                    "replies": int,
                    "url_clicks": int
                }
            }
        }
        """
        if not metrics:
            metrics = [
                'impression_count',
                'like_count',
                'retweet_count',
                'reply_count',
                'quote_count'
            ]
        
        try:
            response = await asyncio.to_thread(
                self.client.get_tweets,
                ids=tweet_ids,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            analytics = {}
            if response.data:
                for tweet in response.data:
                    analytics[tweet.id] = {
                        "impressions": tweet.public_metrics.get('impression_count', 0),
                        "likes": tweet.public_metrics.get('like_count', 0),
                        "retweets": tweet.public_metrics.get('retweet_count', 0),
                        "replies": tweet.public_metrics.get('reply_count', 0),
                        "quotes": tweet.public_metrics.get('quote_count', 0)
                    }
            
            return {"metrics": analytics}
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {e}")
            return {"metrics": {}}
    
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get authenticated user information.
        
        Returns:
        {
            "id": str,
            "username": str,
            "name": str,
            "followers_count": int,
            "following_count": int,
            "tweet_count": int,
            "verified": bool
        }
        """
        try:
            response = await asyncio.to_thread(
                self.client.get_me,
                user_fields=['public_metrics', 'verified']
            )
            
            if response.data:
                user = response.data
                return {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "followers_count": user.public_metrics.get('followers_count', 0),
                    "following_count": user.public_metrics.get('following_count', 0),
                    "tweet_count": user.public_metrics.get('tweet_count', 0),
                    "verified": user.verified
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return {}
```

### 2. LinkedIn Client
**File**: `social_apis/linkedin_client.py`

```python
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import json
import logging

class LinkedInClient:
    """
    LinkedIn API v2 client implementation.
    
    Features:
    - OAuth 2.0 authentication
    - Post creation (text, article, media)
    - Company page management
    - Analytics retrieval
    - Professional networking features
    """
    
    BASE_URL = "https://api.linkedin.com/v2"
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LinkedIn client.
        
        Config should include:
        - access_token
        - organization_id (optional, for company pages)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {config.get('access_token')}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def post_update(
        self,
        text: str,
        media_urls: Optional[List[str]] = None,
        article_url: Optional[str] = None,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """
        Post an update to LinkedIn.
        
        Args:
            text: Post text content
            media_urls: List of media URLs to attach
            article_url: URL to share as article
            visibility: PUBLIC, CONNECTIONS, or LOGGED_IN
        
        Returns:
        {
            "success": bool,
            "post_id": str,
            "url": str,
            "error": Optional[str]
        }
        """
        try:
            # Get author URN (user or organization)
            author_urn = await self._get_author_urn()
            
            # Build share content
            share_content = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Add article if provided
            if article_url:
                share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "originalUrl": article_url
                    }
                ]
            
            # Add images if provided
            elif media_urls:
                share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "media": url
                    } for url in media_urls
                ]
            
            # Post the update
            async with self.session.post(
                f"{self.BASE_URL}/ugcPosts",
                json=share_content
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    post_id = result.get("id")
                    
                    return {
                        "success": True,
                        "post_id": post_id,
                        "url": self._get_post_url(post_id),
                        "visibility": visibility
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"LinkedIn API error: {error_text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to post LinkedIn update: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_article(
        self,
        title: str,
        content: str,
        cover_image: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a long-form article to LinkedIn.
        
        Returns:
        {
            "success": bool,
            "article_id": str,
            "url": str,
            "error": Optional[str]
        }
        """
        # LinkedIn Articles API implementation
        # Note: This requires special permissions
        pass
    
    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for LinkedIn posts.
        
        Returns:
        {
            "metrics": {
                "post_id": {
                    "impressions": int,
                    "clicks": int,
                    "likes": int,
                    "comments": int,
                    "shares": int,
                    "engagement_rate": float
                }
            }
        }
        """
        if not metrics:
            metrics = ["impressions", "clicks", "likes", "comments", "shares"]
        
        analytics = {}
        
        for post_id in post_ids:
            try:
                # Get post statistics
                async with self.session.get(
                    f"{self.BASE_URL}/socialActions/{post_id}/comments"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse analytics data
                        analytics[post_id] = self._parse_analytics(data)
                        
            except Exception as e:
                self.logger.error(f"Failed to get analytics for {post_id}: {e}")
                analytics[post_id] = {}
        
        return {"metrics": analytics}
    
    async def _get_author_urn(self) -> str:
        """Get the author URN for posts (user or organization)."""
        if self.config.get('organization_id'):
            return f"urn:li:organization:{self.config['organization_id']}"
        else:
            # Get current user URN
            async with self.session.get(f"{self.BASE_URL}/me") as response:
                if response.status == 200:
                    data = await response.json()
                    return f"urn:li:person:{data['id']}"
        
        raise Exception("Failed to get author URN")
    
    def _get_post_url(self, post_id: str) -> str:
        """Generate LinkedIn post URL."""
        # Extract the numeric ID from the URN
        numeric_id = post_id.split(":")[-1]
        return f"https://www.linkedin.com/feed/update/{post_id}/"
    
    def _parse_analytics(self, data: Dict) -> Dict[str, Any]:
        """Parse analytics data from API response."""
        # Implementation depends on actual API response format
        return {
            "impressions": data.get("impressionCount", 0),
            "clicks": data.get("clickCount", 0),
            "likes": data.get("likeCount", 0),
            "comments": data.get("commentCount", 0),
            "shares": data.get("shareCount", 0)
        }
```

### 3. Instagram Client
**File**: `social_apis/instagram_client.py`

```python
from instagram_private_api import Client as InstagramAPI
import asyncio
from typing import Dict, Any, List, Optional
import logging

class InstagramClient:
    """
    Instagram API client implementation.
    
    Note: Uses instagram-private-api for full functionality.
    Official API has limited features.
    
    Features:
    - Post photos and videos
    - Stories
    - Reels
    - IGTV
    - Analytics
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Instagram client.
        
        Config should include:
        - username
        - password
        OR
        - access_token (for Graph API)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Instagram API client."""
        try:
            if self.config.get('username') and self.config.get('password'):
                # Private API for full functionality
                self.api = InstagramAPI(
                    self.config['username'],
                    self.config['password']
                )
            elif self.config.get('access_token'):
                # Use Graph API (limited functionality)
                self._init_graph_api()
            else:
                raise ValueError("Instagram credentials not provided")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Instagram client: {e}")
            raise
    
    async def post_photo(
        self,
        image_path: str,
        caption: str,
        location: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a photo to Instagram.
        
        Returns:
        {
            "success": bool,
            "post_id": str,
            "url": str,
            "error": Optional[str]
        }
        """
        try:
            # Process tags (user mentions)
            if tags:
                usertags = [{"user_id": await self._get_user_id(tag), "position": [0.5, 0.5]} 
                          for tag in tags]
            else:
                usertags = None
            
            # Upload photo
            result = await asyncio.to_thread(
                self.api.post_photo,
                image_path,
                caption=caption,
                location=location,
                usertags=usertags
            )
            
            if result.get('status') == 'ok':
                media_id = result['media']['id']
                media_code = result['media']['code']
                
                return {
                    "success": True,
                    "post_id": media_id,
                    "url": f"https://www.instagram.com/p/{media_code}/",
                    "type": "photo"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to post photo"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to post photo: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_video(
        self,
        video_path: str,
        thumbnail_path: str,
        caption: str,
        is_reel: bool = False
    ) -> Dict[str, Any]:
        """
        Post a video or reel to Instagram.
        
        Returns:
        {
            "success": bool,
            "post_id": str,
            "url": str,
            "type": str,  # "video" or "reel"
            "error": Optional[str]
        }
        """
        try:
            if is_reel:
                # Post as reel
                result = await asyncio.to_thread(
                    self.api.post_video,
                    video_path,
                    thumbnail_path,
                    caption=caption,
                    to_reel=True
                )
                post_type = "reel"
            else:
                # Post as regular video
                result = await asyncio.to_thread(
                    self.api.post_video,
                    video_path,
                    thumbnail_path,
                    caption=caption
                )
                post_type = "video"
            
            if result.get('status') == 'ok':
                media_id = result['media']['id']
                media_code = result['media']['code']
                
                return {
                    "success": True,
                    "post_id": media_id,
                    "url": f"https://www.instagram.com/p/{media_code}/",
                    "type": post_type
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to post video"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to post video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def post_story(
        self,
        media_path: str,
        media_type: str = "photo",
        caption: Optional[str] = None,
        mentions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a story to Instagram.
        
        Returns:
        {
            "success": bool,
            "story_id": str,
            "expires_at": datetime,
            "error": Optional[str]
        }
        """
        try:
            if media_type == "photo":
                result = await asyncio.to_thread(
                    self.api.post_photo_story,
                    media_path,
                    caption=caption
                )
            else:
                result = await asyncio.to_thread(
                    self.api.post_video_story,
                    media_path,
                    caption=caption
                )
            
            if result.get('status') == 'ok':
                return {
                    "success": True,
                    "story_id": result['media']['id'],
                    "expires_at": result['media'].get('expiring_at')
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to post story"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to post story: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_analytics(
        self,
        post_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Get analytics for Instagram posts.
        
        Returns:
        {
            "metrics": {
                "post_id": {
                    "likes": int,
                    "comments": int,
                    "saves": int,
                    "impressions": int,
                    "reach": int,
                    "engagement_rate": float
                }
            }
        }
        """
        analytics = {}
        
        for post_id in post_ids:
            try:
                # Get media info
                result = await asyncio.to_thread(
                    self.api.media_info,
                    post_id
                )
                
                if result.get('status') == 'ok':
                    media = result['items'][0]
                    
                    analytics[post_id] = {
                        "likes": media.get('like_count', 0),
                        "comments": media.get('comment_count', 0),
                        "saves": media.get('saved_count', 0),
                        "impressions": media.get('impression_count', 0),
                        "reach": media.get('reach_count', 0)
                    }
                    
                    # Calculate engagement rate
                    total_interactions = (
                        analytics[post_id]["likes"] +
                        analytics[post_id]["comments"] +
                        analytics[post_id]["saves"]
                    )
                    reach = analytics[post_id]["reach"] or 1
                    analytics[post_id]["engagement_rate"] = (total_interactions / reach) * 100
                    
            except Exception as e:
                self.logger.error(f"Failed to get analytics for {post_id}: {e}")
                analytics[post_id] = {}
        
        return {"metrics": analytics}
    
    async def _get_user_id(self, username: str) -> str:
        """Get user ID from username."""
        try:
            result = await asyncio.to_thread(
                self.api.username_info,
                username
            )
            return result['user']['pk']
        except:
            return None
```

### 4. Base Client Interface
**File**: `social_apis/base_client.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseSocialClient(ABC):
    """
    Abstract base class for social media API clients.
    
    All platform clients should inherit from this class.
    """
    
    @abstractmethod
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Post content to the platform."""
        pass
    
    @abstractmethod
    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get analytics for posts."""
        pass
    
    @abstractmethod
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information."""
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        pass
    
    @abstractmethod
    async def update_post(
        self,
        post_id: str,
        text: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing post."""
        pass
```

### 5. Client Factory
**File**: `social_apis/client_factory.py`

```python
from typing import Dict, Any, Optional
from .twitter_client import TwitterClient
from .linkedin_client import LinkedInClient
from .instagram_client import InstagramClient
from .facebook_client import FacebookClient
from .youtube_client import YouTubeClient
from .base_client import BaseSocialClient

class SocialMediaClientFactory:
    """
    Factory for creating social media API clients.
    """
    
    CLIENTS = {
        "twitter": TwitterClient,
        "linkedin": LinkedInClient,
        "instagram": InstagramClient,
        "facebook": FacebookClient,
        "youtube": YouTubeClient
    }
    
    @classmethod
    def create_client(
        cls,
        platform: str,
        config: Dict[str, Any]
    ) -> Optional[BaseSocialClient]:
        """
        Create a social media client for the specified platform.
        
        Args:
            platform: Platform name (twitter, linkedin, etc.)
            config: Platform-specific configuration
        
        Returns:
            Initialized client or None if platform not supported
        """
        client_class = cls.CLIENTS.get(platform.lower())
        
        if client_class:
            return client_class(config)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms."""
        return list(cls.CLIENTS.keys())
```

## Configuration

Add to `mcp_agent.config.yaml`:

```yaml
social_api_clients:
  twitter:
    api_key: "${TWITTER_API_KEY}"
    api_secret: "${TWITTER_API_SECRET}"
    access_token: "${TWITTER_ACCESS_TOKEN}"
    access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
    bearer_token: "${TWITTER_BEARER_TOKEN}"
    rate_limit_retry: true
    
  linkedin:
    client_id: "${LINKEDIN_CLIENT_ID}"
    client_secret: "${LINKEDIN_CLIENT_SECRET}"
    redirect_uri: "http://localhost:8501/callback/linkedin"
    
  instagram:
    username: "${INSTAGRAM_USERNAME}"
    password: "${INSTAGRAM_PASSWORD}"
    # OR use Graph API
    access_token: "${INSTAGRAM_ACCESS_TOKEN}"
    
  facebook:
    app_id: "${FACEBOOK_APP_ID}"
    app_secret: "${FACEBOOK_APP_SECRET}"
    access_token: "${FACEBOOK_ACCESS_TOKEN}"
    
  youtube:
    api_key: "${YOUTUBE_API_KEY}"
    client_id: "${YOUTUBE_CLIENT_ID}"
    client_secret: "${YOUTUBE_CLIENT_SECRET}"
```

## Error Handling

Each client must implement:

```python
class APIError(Exception):
    """Base API error."""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass

class AuthenticationError(APIError):
    """Authentication failed."""
    pass

class ContentError(APIError):
    """Content validation failed."""
    pass
```

## Testing Requirements

### 1. Mock Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_twitter_post():
    """Test Twitter posting."""
    with patch('tweepy.Client') as mock_client:
        mock_client.create_tweet = AsyncMock(return_value={
            "data": {"id": "123456"}
        })
        
        client = TwitterClient(config)
        result = await client.post_tweet("Test tweet")
        
        assert result["success"] == True
        assert result["tweet_id"] == "123456"
```

### 2. Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_twitter_connection():
    """Test real Twitter API connection."""
    # Only run with real credentials
    if not os.getenv("TWITTER_API_KEY"):
        pytest.skip("No Twitter credentials")
    
    client = TwitterClient(real_config)
    user_info = await client.get_user_info()
    
    assert "username" in user_info
    assert "followers_count" in user_info
```

## Rate Limiting

Implement rate limit handling:

```python
class RateLimiter:
    """Rate limiting handler for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old calls
        self.call_times = [t for t in self.call_times if t > minute_ago]
        
        if len(self.call_times) >= self.calls_per_minute:
            # Wait until oldest call expires
            wait_time = 60 - (now - self.call_times[0]) + 1
            await asyncio.sleep(wait_time)
        
        self.call_times.append(now)
```

## Success Criteria

- [ ] All 5 platform clients implemented
- [ ] OAuth authentication working
- [ ] Content posting functional
- [ ] Media upload working
- [ ] Analytics retrieval implemented
- [ ] Rate limiting handled
- [ ] Error handling comprehensive
- [ ] Tests passing

## Dependencies

```txt
tweepy>=4.14.0
linkedin-api>=2.0.0
instagram-private-api>=1.6.0
facebook-sdk>=3.1.0
google-api-python-client>=2.100.0
aiohttp>=3.9.0
```

## Delivery Checklist

- [ ] 5 platform client implementations
- [ ] Base client interface
- [ ] Client factory
- [ ] Error handling classes
- [ ] Rate limiting implementation
- [ ] Unit tests for each client
- [ ] Integration test suite
- [ ] Configuration documentation
- [ ] Dependencies added to requirements.txt