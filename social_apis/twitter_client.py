"""
Twitter/X API v2.0 Client

Implements Twitter-specific API integration with OAuth 2.0 authentication,
content posting, analytics, and user management.
"""

from datetime import datetime
from typing import Dict, Any, List

from utils.platform_clients import BasePlatformClient
from models.social_models import PostAnalytics, PlatformType


class TwitterClient(BasePlatformClient):
    """Twitter/X API v2.0 client"""
    
    def _get_api_base_url(self) -> str:
        """Get Twitter API v2 base URL"""
        return "https://api.twitter.com/2"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get Twitter-specific rate limits"""
        return {
            "tweet_create": {"requests": 300, "window": 900},      # 300 per 15 min
            "tweet_read": {"requests": 75, "window": 900},         # 75 per 15 min
            "user_lookup": {"requests": 300, "window": 900},       # 300 per 15 min
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Twitter API connection"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/users/me"
            )
            
            if result["success"]:
                user_data = result["data"]["data"]
                return {
                    "success": True,
                    "platform": "twitter",
                    "user_id": user_data["id"],
                    "username": user_data["username"],
                    "display_name": user_data["name"],
                    "verified": user_data.get("verified", False),
                    "message": "Successfully connected to Twitter API"
                }
            else:
                return {
                    "success": False,
                    "platform": "twitter",
                    "error": result.get("error", "Connection test failed")
                }
        
        except Exception as e:
            self.logger.error(f"Twitter connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "twitter",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's Twitter profile"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/users/me",
                params={
                    "user.fields": "id,name,username,description,public_metrics,verified,profile_image_url"
                }
            )
            
            if result["success"]:
                user_data = result["data"]["data"]
                metrics = user_data.get("public_metrics", {})
                
                return {
                    "success": True,
                    "profile": {
                        "platform_user_id": user_data["id"],
                        "username": user_data["username"],
                        "display_name": user_data["name"],
                        "description": user_data.get("description", ""),
                        "verified": user_data.get("verified", False),
                        "profile_image_url": user_data.get("profile_image_url", ""),
                        "followers_count": metrics.get("followers_count", 0),
                        "following_count": metrics.get("following_count", 0),
                        "tweet_count": metrics.get("tweet_count", 0),
                        "listed_count": metrics.get("listed_count", 0)
                    }
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Twitter profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Post a tweet to Twitter"""
        
        try:
            # Prepare tweet data
            tweet_data = {"text": content}
            
            # Handle media attachments (if any)
            if media_urls:
                # For Twitter, we'd need to upload media first using media upload API
                # This is a simplified version - full implementation would handle media upload
                media_ids = await self._upload_media_files(media_urls)
                if media_ids:
                    tweet_data["media"] = {"media_ids": media_ids}
            
            result = await self._make_api_request(
                method="POST",
                endpoint="/tweets",
                data=tweet_data
            )
            
            if result["success"]:
                tweet_data = result["data"]["data"]
                return {
                    "success": True,
                    "platform": "twitter",
                    "platform_post_id": tweet_data["id"],
                    "content": tweet_data["text"],
                    "published_at": datetime.now().isoformat(),
                    "url": f"https://twitter.com/i/status/{tweet_data['id']}"
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to post tweet: {str(e)}"
            }
    
    async def _upload_media_files(self, media_urls: List[str]) -> List[str]:
        """Upload media files to Twitter (placeholder)"""
        # This would implement the Twitter media upload API
        # For now, returning empty list as placeholder
        self.logger.warning("Media upload not yet implemented for Twitter")
        return []
    
    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Get analytics for a specific tweet or account"""
        
        try:
            if post_id:
                # Get tweet analytics
                result = await self._make_api_request(
                    method="GET",
                    endpoint=f"/tweets/{post_id}",
                    params={
                        "tweet.fields": "public_metrics,created_at,author_id",
                        "expansions": "author_id"
                    }
                )
                
                if result["success"]:
                    tweet_data = result["data"]["data"]
                    metrics = tweet_data.get("public_metrics", {})
                    
                    analytics = PostAnalytics(
                        post_id=post_id,
                        platform_post_id=tweet_data["id"],
                        platform=PlatformType.TWITTER,
                        views=metrics.get("impression_count", 0),
                        likes=metrics.get("like_count", 0),
                        shares=metrics.get("retweet_count", 0),
                        comments=metrics.get("reply_count", 0),
                        clicks=metrics.get("url_link_clicks", 0),
                        impressions=metrics.get("impression_count", 0),
                        platform_metrics=metrics
                    )
                    
                    # Calculate engagement rate
                    analytics.calculate_engagement_rate()
                    
                    return {
                        "success": True,
                        "analytics": analytics.to_dict()
                    }
                else:
                    return result
            else:
                # Get account analytics (simplified)
                profile_result = await self.get_user_profile()
                
                if profile_result["success"]:
                    profile = profile_result["profile"]
                    
                    return {
                        "success": True,
                        "account_analytics": {
                            "followers_count": profile["followers_count"],
                            "following_count": profile["following_count"],
                            "tweet_count": profile["tweet_count"],
                            "listed_count": profile["listed_count"],
                            "collected_at": datetime.now().isoformat()
                        }
                    }
                else:
                    return profile_result
        
        except Exception as e:
            self.logger.error(f"Failed to get Twitter analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    async def delete_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Delete a tweet"""
        
        try:
            result = await self._make_api_request(
                method="DELETE",
                endpoint=f"/tweets/{tweet_id}"
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Tweet {tweet_id} deleted successfully"
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to delete tweet {tweet_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete tweet: {str(e)}"
            }
    
    async def get_mentions(self, max_results: int = 10) -> Dict[str, Any]:
        """Get recent mentions of the authenticated user"""
        
        try:
            # First get user ID
            profile_result = await self.get_user_profile()
            if not profile_result["success"]:
                return profile_result
            
            user_id = profile_result["profile"]["platform_user_id"]
            
            result = await self._make_api_request(
                method="GET",
                endpoint=f"/users/{user_id}/mentions",
                params={
                    "max_results": max_results,
                    "tweet.fields": "created_at,author_id,public_metrics",
                    "expansions": "author_id"
                }
            )
            
            if result["success"]:
                tweets = result["data"].get("data", [])
                users = {user["id"]: user for user in result["data"].get("includes", {}).get("users", [])}
                
                mentions = []
                for tweet in tweets:
                    author = users.get(tweet["author_id"], {})
                    mentions.append({
                        "tweet_id": tweet["id"],
                        "text": tweet["text"],
                        "created_at": tweet["created_at"],
                        "author": {
                            "id": author.get("id"),
                            "username": author.get("username"),
                            "name": author.get("name")
                        },
                        "metrics": tweet.get("public_metrics", {})
                    })
                
                return {
                    "success": True,
                    "mentions": mentions
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Twitter mentions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get mentions: {str(e)}"
            }