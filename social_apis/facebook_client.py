"""
Facebook Graph API Client

Implements Facebook-specific API integration with OAuth 2.0 authentication,
page management, content posting, and analytics using facebook-sdk.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from .base_client import BaseSocialClient

try:
    import facebook
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False
    facebook = None


class FacebookClient(BaseSocialClient):
    """
    Facebook Graph API client implementation.
    
    Features:
    - OAuth 2.0 authentication
    - Page and profile posting
    - Media uploads
    - Analytics and insights
    - Page management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Facebook client.
        
        Config should include:
        - access_token
        - page_id (optional, for posting to pages)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if not FACEBOOK_SDK_AVAILABLE:
            # Use direct HTTP requests instead
            self.api = None
            self.headers = {
                "Authorization": f"Bearer {config.get('access_token')}",
                "Content-Type": "application/json"
            }
        else:
            # Use facebook-sdk if available
            self.api = facebook.GraphAPI(access_token=config.get('access_token'))
        
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Facebook.
        
        Args:
            text: Post message content
            media: List of media URLs or file paths
            **kwargs: Additional parameters like page_id, link
        
        Returns:
            Dict containing post result
        """
        try:
            page_id = kwargs.get('page_id', self.config.get('page_id'))
            endpoint = "/me/feed"  # Default to user timeline
            
            if page_id:
                # Post to a specific page
                endpoint = f"/{page_id}/feed"
            
            post_data = {
                "message": text
            }
            
            # Handle media attachments
            if media:
                if len(media) == 1 and media[0].startswith('http'):
                    # Single URL link
                    post_data["link"] = media[0]
                else:
                    # For multiple images, we'd need to use the batch API
                    # For now, just use the first media item
                    if media[0].startswith('http'):
                        post_data["link"] = media[0]
            
            # Add custom link if provided
            if kwargs.get('link'):
                post_data["link"] = kwargs.get('link')
            
            if self.api:
                # Use facebook-sdk
                result = await asyncio.to_thread(
                    self.api.put_object,
                    parent_object=endpoint.replace("/", "").replace("feed", ""),
                    connection_name="feed",
                    **post_data
                )
                post_id = result.get("id")
            else:
                # Use direct HTTP request
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.post(
                        f"{self.base_url}{endpoint}",
                        json=post_data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            post_id = result.get("id")
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"API error: {response.status} - {error_text}",
                                "platform": "facebook"
                            }
            
            if post_id:
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://www.facebook.com/{post_id}",
                    "platform": "facebook",
                    "published_at": datetime.now(),
                    "page_id": page_id
                }
            else:
                return {
                    "success": False,
                    "error": "No post ID returned",
                    "platform": "facebook"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to post to Facebook: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user's Facebook information."""
        
        try:
            if self.api:
                result = await asyncio.to_thread(
                    self.api.get_object,
                    id="me",
                    fields="id,name,email,picture.width(200).height(200)"
                )
            else:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(
                        f"{self.base_url}/me",
                        params={"fields": "id,name,email,picture.width(200).height(200)"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"API error: {response.status} - {error_text}"
                            }
            
            picture_url = ""
            if "picture" in result:
                picture_url = result["picture"].get("data", {}).get("url", "")
            
            return {
                "success": True,
                "user_info": {
                    "id": result["id"],
                    "name": result.get("name"),
                    "email": result.get("email"),
                    "picture_url": picture_url
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Facebook user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get analytics for Facebook posts."""
        
        if not metrics:
            metrics = ["post_impressions", "post_engaged_users", "post_reactions_by_type_total", "post_clicks"]
        
        analytics = {}
        
        for post_id in post_ids:
            try:
                if self.api:
                    result = await asyncio.to_thread(
                        self.api.get_object,
                        id=f"{post_id}/insights",
                        metric=",".join(metrics)
                    )
                    insights_data = result.get("data", [])
                else:
                    async with aiohttp.ClientSession(headers=self.headers) as session:
                        async with session.get(
                            f"{self.base_url}/{post_id}/insights",
                            params={"metric": ",".join(metrics)}
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                insights_data = result.get("data", [])
                            else:
                                insights_data = []
                
                # Parse insights data
                parsed_metrics = {}
                for insight in insights_data:
                    metric_name = insight.get("name")
                    metric_values = insight.get("values", [])
                    if metric_values:
                        parsed_metrics[metric_name] = metric_values[0].get("value", 0)
                
                analytics[post_id] = {
                    "impressions": parsed_metrics.get("post_impressions", 0),
                    "engaged_users": parsed_metrics.get("post_engaged_users", 0),
                    "likes": parsed_metrics.get("post_reactions_by_type_total", {}).get("like", 0),
                    "clicks": parsed_metrics.get("post_clicks", 0)
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get analytics for {post_id}: {e}")
                analytics[post_id] = {}
        
        return {
            "success": True,
            "metrics": analytics
        }

    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a Facebook post."""
        
        try:
            if self.api:
                result = await asyncio.to_thread(
                    self.api.delete_object,
                    id=post_id
                )
            else:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.delete(
                        f"{self.base_url}/{post_id}"
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Failed to delete post: {response.status} - {error_text}"
                            }
            
            if result.get("success", True):
                return {
                    "success": True,
                    "message": f"Facebook post {post_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete post"
                }
            
        except Exception as e:
            self.logger.error(f"Failed to delete Facebook post {post_id}: {e}")
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
        Update an existing Facebook post.
        Note: Facebook has limited post editing capabilities.
        """
        if text:
            try:
                post_data = {"message": text}
                
                if self.api:
                    result = await asyncio.to_thread(
                        self.api.put_object,
                        parent_object=post_id,
                        connection_name="",
                        **post_data
                    )
                else:
                    async with aiohttp.ClientSession(headers=self.headers) as session:
                        async with session.post(
                            f"{self.base_url}/{post_id}",
                            json=post_data
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                            else:
                                error_text = await response.text()
                                return {
                                    "success": False,
                                    "error": f"Failed to update post: {response.status} - {error_text}"
                                }
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "updated_at": datetime.now(),
                    "message": "Post updated successfully"
                }
                
            except Exception as e:
                self.logger.error(f"Failed to update Facebook post {post_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": "No message text provided for update"
            }
    
