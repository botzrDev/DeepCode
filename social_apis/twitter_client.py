"""
Twitter/X API v2.0 Client

Implements Twitter-specific API integration with OAuth 2.0 authentication,
content posting, analytics, and user management using tweepy library.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    tweepy = None

from .base_client import BaseSocialClient


class TwitterClient(BaseSocialClient):
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
        if not TWEEPY_AVAILABLE:
            raise ImportError("tweepy is required. Install with: pip install tweepy")
            
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
    
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post a tweet to Twitter.
        
        Args:
            text: Tweet text content
            media: List of media file paths to upload
            **kwargs: Additional parameters like reply_to, quote_tweet_id
        
        Returns:
            Dict containing post result with tweet_id and URL
        """
        try:
            media_ids = None
            
            # Handle media upload if provided
            if media:
                media_ids = []
                for media_path in media:
                    media_id = await self.upload_media(media_path)
                    if media_id:
                        media_ids.append(media_id)
            
            # Post tweet with v2 API
            response = await asyncio.to_thread(
                self.client.create_tweet,
                text=text,
                media_ids=media_ids,
                in_reply_to_tweet_id=kwargs.get('reply_to'),
                quote_tweet_id=kwargs.get('quote_tweet_id')
            )
            
            tweet_data = response.data
            tweet_id = tweet_data['id']
            
            return {
                "success": True,
                "post_id": tweet_id,
                "url": f"https://twitter.com/i/web/status/{tweet_id}",
                "platform": "twitter",
                "published_at": datetime.now(),
                "text": text
            }
            
        except tweepy.TooManyRequests as e:
            self.logger.warning(f"Rate limit exceeded: {e}")
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "platform": "twitter"
            }
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter"
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user's Twitter profile information."""
        
        try:
            response = await asyncio.to_thread(
                self.client.get_me,
                user_fields=['public_metrics', 'verified', 'description', 'profile_image_url']
            )
            
            if response.data:
                user = response.data
                return {
                    "success": True,
                    "user_info": {
                        "id": user.id,
                        "username": user.username,
                        "name": user.name,
                        "description": getattr(user, 'description', ''),
                        "followers_count": user.public_metrics.get('followers_count', 0),
                        "following_count": user.public_metrics.get('following_count', 0),
                        "tweet_count": user.public_metrics.get('tweet_count', 0),
                        "verified": getattr(user, 'verified', False),
                        "profile_image_url": getattr(user, 'profile_image_url', '')
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get user information"
                }
            
        except Exception as e:
            self.logger.error(f"Failed to get user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for tweets.
        
        Args:
            post_ids: List of tweet IDs
            metrics: Specific metrics to retrieve
        
        Returns:
        {
            "success": bool,
            "metrics": {
                "tweet_id": {
                    "impressions": int,
                    "likes": int,
                    "retweets": int,
                    "replies": int,
                    "quotes": int
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
                ids=post_ids,
                tweet_fields=['public_metrics', 'created_at']
            )
            
            analytics = {}
            if response.data:
                for tweet in response.data:
                    tweet_metrics = tweet.public_metrics or {}
                    analytics[tweet.id] = {
                        "impressions": tweet_metrics.get('impression_count', 0),
                        "likes": tweet_metrics.get('like_count', 0),
                        "retweets": tweet_metrics.get('retweet_count', 0),
                        "replies": tweet_metrics.get('reply_count', 0),
                        "quotes": tweet_metrics.get('quote_count', 0)
                    }
            
            return {
                "success": True,
                "metrics": analytics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "metrics": {}
            }
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a tweet."""
        
        try:
            response = await asyncio.to_thread(
                self.client.delete_tweet,
                id=post_id
            )
            
            if response.data and response.data.get('deleted'):
                return {
                    "success": True,
                    "message": f"Tweet {post_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete tweet"
                }
        
        except Exception as e:
            self.logger.error(f"Failed to delete tweet {post_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_post(
        self,
        post_id: str,
        text: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing tweet.
        Note: Twitter doesn't support editing tweets, so this will return an error.
        """
        return {
            "success": False,
            "error": "Twitter does not support editing tweets. Consider deleting and reposting."
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
    
    async def post_thread(
        self,
        tweets: List[str],
        media_per_tweet: Optional[Dict[int, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts
            media_per_tweet: Dict mapping tweet index to media file paths
        
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
                media = media_per_tweet.get(idx) if media_per_tweet else None
                
                result = await self.post_content(
                    text=tweet_text,
                    media=media,
                    reply_to=reply_to
                )
                
                if not result["success"]:
                    raise Exception(f"Failed to post tweet {idx + 1}: {result['error']}")
                
                tweet_ids.append(result["post_id"])
                urls.append(result["url"])
                reply_to = result["post_id"]  # Reply to previous tweet
                
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