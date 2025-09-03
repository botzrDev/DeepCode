"""
Instagram API Client

Implements Instagram-specific API integration using instagram-private-api
for full functionality including posting.
"""

import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_client import BaseSocialClient

try:
    from instagram_private_api import Client as InstagramAPI
    INSTAGRAM_PRIVATE_API_AVAILABLE = True
except ImportError:
    INSTAGRAM_PRIVATE_API_AVAILABLE = False
    InstagramAPI = None


class InstagramClient(BaseSocialClient):
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
        
        if not INSTAGRAM_PRIVATE_API_AVAILABLE:
            raise ImportError("instagram-private-api is required. Install with: pip install instagram-private-api")
            
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
    
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to Instagram.
        
        Args:
            text: Caption text
            media: List of media file paths
            **kwargs: Additional parameters like is_reel, location, tags
        
        Returns:
            Dict containing post result
        """
        if not media:
            return {
                "success": False,
                "error": "Instagram requires at least one media file",
                "platform": "instagram"
            }
        
        try:
            media_path = media[0]  # Use first media file
            is_reel = kwargs.get('is_reel', False)
            location = kwargs.get('location')
            tags = kwargs.get('tags', [])
            
            # Determine media type
            if media_path.lower().endswith(('.mp4', '.mov')):
                if is_reel:
                    result = await self.post_reel(media_path, text, tags)
                else:
                    result = await self.post_video(media_path, text, tags)
            else:
                result = await self.post_photo(media_path, text, location, tags)
            
            if result.get('success'):
                return {
                    "success": True,
                    "post_id": result.get("post_id"),
                    "url": result.get("url"),
                    "platform": "instagram",
                    "published_at": datetime.now(),
                    "type": result.get("type", "photo")
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to post to Instagram: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }
    
    async def post_photo(
        self,
        image_path: str,
        caption: str,
        location: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Post a photo to Instagram."""
        
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
        caption: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Post a video to Instagram."""
        
        try:
            # For videos, we need a thumbnail - assume it's next to the video
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            
            result = await asyncio.to_thread(
                self.api.post_video,
                video_path,
                thumbnail_path,
                caption=caption
            )
            
            if result.get('status') == 'ok':
                media_id = result['media']['id']
                media_code = result['media']['code']
                
                return {
                    "success": True,
                    "post_id": media_id,
                    "url": f"https://www.instagram.com/p/{media_code}/",
                    "type": "video"
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
    
    async def post_reel(
        self,
        video_path: str,
        caption: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Post a reel to Instagram."""
        
        try:
            thumbnail_path = video_path.replace('.mp4', '_thumb.jpg')
            
            result = await asyncio.to_thread(
                self.api.post_video,
                video_path,
                thumbnail_path,
                caption=caption,
                to_reel=True
            )
            
            if result.get('status') == 'ok':
                media_id = result['media']['id']
                media_code = result['media']['code']
                
                return {
                    "success": True,
                    "post_id": media_id,
                    "url": f"https://www.instagram.com/reel/{media_code}/",
                    "type": "reel"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to post reel"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to post reel: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user's Instagram information."""
        
        try:
            result = await asyncio.to_thread(
                self.api.current_user
            )
            
            if result:
                return {
                    "success": True,
                    "user_info": {
                        "id": result.get('pk'),
                        "username": result.get('username'),
                        "full_name": result.get('full_name', ''),
                        "biography": result.get('biography', ''),
                        "follower_count": result.get('follower_count', 0),
                        "following_count": result.get('following_count', 0),
                        "media_count": result.get('media_count', 0),
                        "is_private": result.get('is_private', False),
                        "profile_pic_url": result.get('profile_pic_url', '')
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
        Get analytics for Instagram posts.
        
        Returns:
        {
            "success": bool,
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
                else:
                    analytics[post_id] = {}
                    
            except Exception as e:
                self.logger.error(f"Failed to get analytics for {post_id}: {e}")
                analytics[post_id] = {}
        
        return {
            "success": True,
            "metrics": analytics
        }
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete an Instagram post."""
        
        try:
            result = await asyncio.to_thread(
                self.api.delete_media,
                post_id
            )
            
            if result.get('status') == 'ok':
                return {
                    "success": True,
                    "message": f"Instagram post {post_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete post"
                }
        
        except Exception as e:
            self.logger.error(f"Failed to delete Instagram post {post_id}: {e}")
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
        Update an existing Instagram post.
        Note: Instagram has limited editing capabilities.
        """
        if text:
            try:
                result = await asyncio.to_thread(
                    self.api.edit_media,
                    post_id,
                    caption=text
                )
                
                if result.get('status') == 'ok':
                    return {
                        "success": True,
                        "post_id": post_id,
                        "updated_at": datetime.now(),
                        "message": "Caption updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update caption"
                    }
            
            except Exception as e:
                self.logger.error(f"Failed to update Instagram post {post_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "error": "No caption text provided for update"
            }
    
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
    
