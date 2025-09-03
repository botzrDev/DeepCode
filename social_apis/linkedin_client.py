"""
LinkedIn API v2.0 Client

Implements LinkedIn-specific API integration with OAuth 2.0 authentication,
professional content posting, and profile management.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

from .base_client import BaseSocialClient


class LinkedInClient(BaseSocialClient):
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
    
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post an update to LinkedIn.
        
        Args:
            text: Post text content
            media: List of media URLs to attach
            **kwargs: Additional parameters like article_url, visibility
        
        Returns:
        {
            "success": bool,
            "post_id": str,
            "url": str,
            "error": Optional[str]
        }
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                # Get author URN (user or organization)
                author_urn = await self._get_author_urn(session)
                
                visibility = kwargs.get('visibility', 'PUBLIC')
                article_url = kwargs.get('article_url')
                
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
                elif media:
                    share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    share_content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "media": url
                        } for url in media
                    ]
                
                # Post the update
                async with session.post(
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
                            "platform": "linkedin",
                            "published_at": datetime.now(),
                            "visibility": visibility
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"LinkedIn API error: {error_text}")
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                            "platform": "linkedin"
                        }
                        
            except Exception as e:
                self.logger.error(f"Failed to post LinkedIn update: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "platform": "linkedin"
                }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user's LinkedIn profile information."""
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(
                    f"{self.BASE_URL}/people/~",
                    params={
                        "projection": "(id,firstName,lastName,headline,summary,profilePicture(displayImage~:playableStreams),positions,industry,location)"
                    }
                ) as response:
                    if response.status == 200:
                        profile_data = await response.json()
                        
                        # Extract localized names
                        first_name = profile_data.get("firstName", {}).get("localized", {})
                        last_name = profile_data.get("lastName", {}).get("localized", {})
                        
                        display_name = ""
                        if first_name:
                            display_name = list(first_name.values())[0]
                        if last_name:
                            display_name += " " + list(last_name.values())[0]
                        
                        # Get profile picture
                        profile_pic_url = ""
                        profile_pic = profile_data.get("profilePicture", {}).get("displayImage~", {})
                        if profile_pic and "elements" in profile_pic:
                            elements = profile_pic["elements"]
                            if elements and len(elements) > 0:
                                identifiers = elements[0].get("identifiers", [])
                                if identifiers:
                                    profile_pic_url = identifiers[0].get("identifier", "")
                        
                        return {
                            "success": True,
                            "user_info": {
                                "id": profile_data.get("id"),
                                "name": display_name.strip(),
                                "headline": profile_data.get("headline", ""),
                                "summary": profile_data.get("summary", ""),
                                "industry": profile_data.get("industry", ""),
                                "location": profile_data.get("location", {}).get("name", ""),
                                "profile_image_url": profile_pic_url
                            }
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"API error: {response.status} - {error_text}"
                        }
            
            except Exception as e:
                self.logger.error(f"Failed to get LinkedIn profile: {e}")
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
        Get analytics for LinkedIn posts.
        
        Returns:
        {
            "success": bool,
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
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for post_id in post_ids:
                try:
                    # Get post statistics
                    async with session.get(
                        f"{self.BASE_URL}/socialActions/{post_id}/comments"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Parse analytics data
                            analytics[post_id] = self._parse_analytics(data)
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
        """
        Delete a LinkedIn post.
        Note: LinkedIn API has limited delete capabilities.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.delete(
                    f"{self.BASE_URL}/ugcPosts/{post_id}"
                ) as response:
                    if response.status == 204:
                        return {
                            "success": True,
                            "message": f"LinkedIn post {post_id} deleted successfully"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to delete post: {response.status} - {error_text}"
                        }
            
            except Exception as e:
                self.logger.error(f"Failed to delete LinkedIn post {post_id}: {e}")
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
        Update an existing LinkedIn post.
        Note: LinkedIn doesn't support editing posts.
        """
        return {
            "success": False,
            "error": "LinkedIn does not support editing posts. Consider deleting and reposting."
        }
    
    async def _get_author_urn(self, session: aiohttp.ClientSession) -> str:
        """Get the author URN for posts (user or organization)."""
        if self.config.get('organization_id'):
            return f"urn:li:organization:{self.config['organization_id']}"
        else:
            # Get current user URN
            async with session.get(f"{self.BASE_URL}/people/~") as response:
                if response.status == 200:
                    data = await response.json()
                    return f"urn:li:person:{data['id']}"
        
        raise Exception("Failed to get author URN")
    
    def _get_post_url(self, post_id: str) -> str:
        """Generate LinkedIn post URL."""
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