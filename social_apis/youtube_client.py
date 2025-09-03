"""
YouTube Data API v3.0 Client

Implements YouTube-specific API integration with OAuth 2.0 authentication,
video uploads, channel management, and analytics using Google API client.
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base_client import BaseSocialClient

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    build = None
    MediaFileUpload = None
    Credentials = None


class YouTubeClient(BaseSocialClient):
    """
    YouTube Data API v3.0 client implementation.
    
    Features:
    - OAuth 2.0 authentication
    - Video uploads
    - Channel management
    - Video analytics
    - Community posts (limited)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize YouTube client.
        
        Config should include:
        - access_token
        - refresh_token
        - client_id
        - client_secret
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if not GOOGLE_API_AVAILABLE:
            self.youtube = None
            self.base_url = "https://www.googleapis.com/youtube/v3"
            self.headers = {
                "Authorization": f"Bearer {config.get('access_token')}",
                "Content-Type": "application/json"
            }
        else:
            # Use Google API client
            credentials = Credentials(
                token=config.get('access_token'),
                refresh_token=config.get('refresh_token'),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=config.get('client_id'),
                client_secret=config.get('client_secret'),
                scopes=["https://www.googleapis.com/auth/youtube.upload", 
                       "https://www.googleapis.com/auth/youtube"]
            )
            self.youtube = build('youtube', 'v3', credentials=credentials)
    
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upload video to YouTube.
        
        Args:
            text: Video title and description
            media: List containing video file path
            **kwargs: Additional parameters like privacy_status, tags
        
        Returns:
            Dict containing upload result
        """
        if not media or len(media) == 0:
            return {
                "success": False,
                "error": "Video file is required for YouTube upload",
                "platform": "youtube"
            }
        
        video_file = media[0]
        title = kwargs.get('title', text[:100])  # YouTube title limit
        description = kwargs.get('description', text)
        privacy_status = kwargs.get('privacy_status', 'private')
        tags = kwargs.get('tags', [])
        
        try:
            if self.youtube:
                # Use Google API client
                body = {
                    'snippet': {
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'categoryId': '22'  # People & Blogs category
                    },
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
                
                media_upload = MediaFileUpload(
                    video_file,
                    chunksize=-1,
                    resumable=True
                )
                
                request = self.youtube.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media_upload
                )
                
                response = await asyncio.to_thread(request.execute)
                
                if response:
                    video_id = response['id']
                    return {
                        "success": True,
                        "post_id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "platform": "youtube",
                        "published_at": datetime.now(),
                        "title": title,
                        "privacy_status": privacy_status
                    }
                else:
                    return {
                        "success": False,
                        "error": "Upload failed - no response from YouTube",
                        "platform": "youtube"
                    }
            else:
                # Direct HTTP approach (more complex for file uploads)
                return {
                    "success": False,
                    "error": "YouTube video upload requires Google API client library",
                    "platform": "youtube"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to upload to YouTube: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": "youtube"
            }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user's YouTube channel information."""
        
        try:
            if self.youtube:
                request = self.youtube.channels().list(
                    part="snippet,statistics,brandingSettings",
                    mine=True
                )
                response = await asyncio.to_thread(request.execute)
                channels = response.get("items", [])
            else:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(
                        f"{self.base_url}/channels",
                        params={
                            "part": "snippet,statistics,brandingSettings",
                            "mine": "true"
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            channels = data.get("items", [])
                        else:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"API error: {response.status} - {error_text}"
                            }
            
            if channels:
                channel = channels[0]
                snippet = channel.get("snippet", {})
                statistics = channel.get("statistics", {})
                
                return {
                    "success": True,
                    "user_info": {
                        "id": channel["id"],
                        "title": snippet.get("title"),
                        "description": snippet.get("description", ""),
                        "custom_url": snippet.get("customUrl", ""),
                        "published_at": snippet.get("publishedAt"),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                        "subscriber_count": int(statistics.get("subscriberCount", 0)),
                        "video_count": int(statistics.get("videoCount", 0)),
                        "view_count": int(statistics.get("viewCount", 0)),
                        "country": snippet.get("country", "")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No YouTube channel found"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get YouTube user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get analytics for YouTube videos."""
        
        analytics = {}
        
        for video_id in post_ids:
            try:
                if self.youtube:
                    request = self.youtube.videos().list(
                        part="statistics,snippet",
                        id=video_id
                    )
                    response = await asyncio.to_thread(request.execute)
                    videos = response.get("items", [])
                else:
                    async with aiohttp.ClientSession(headers=self.headers) as session:
                        async with session.get(
                            f"{self.base_url}/videos",
                            params={
                                "part": "statistics,snippet",
                                "id": video_id
                            }
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                videos = data.get("items", [])
                            else:
                                videos = []
                
                if videos:
                    video = videos[0]
                    statistics = video.get("statistics", {})
                    
                    analytics[video_id] = {
                        "views": int(statistics.get("viewCount", 0)),
                        "likes": int(statistics.get("likeCount", 0)),
                        "comments": int(statistics.get("commentCount", 0)),
                        "favorites": int(statistics.get("favoriteCount", 0))
                    }
                else:
                    analytics[video_id] = {}
                    
            except Exception as e:
                self.logger.error(f"Failed to get analytics for {video_id}: {e}")
                analytics[video_id] = {}
        
        return {
            "success": True,
            "metrics": analytics
        }
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a YouTube video."""
        
        try:
            if self.youtube:
                request = self.youtube.videos().delete(id=post_id)
                await asyncio.to_thread(request.execute)
            else:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.delete(
                        f"{self.base_url}/videos",
                        params={"id": post_id}
                    ) as response:
                        if response.status != 204:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Failed to delete video: {response.status} - {error_text}"
                            }
            
            return {
                "success": True,
                "message": f"YouTube video {post_id} deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete YouTube video {post_id}: {e}")
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
        """Update YouTube video metadata."""
        
        try:
            update_data = {
                "id": post_id,
                "snippet": {}
            }
            
            if text:
                # Split text into title and description
                lines = text.split('\n', 1)
                title = lines[0][:100]  # YouTube title limit
                description = lines[1] if len(lines) > 1 else text
                
                update_data["snippet"]["title"] = title
                update_data["snippet"]["description"] = description
            
            if kwargs.get('title'):
                update_data["snippet"]["title"] = kwargs['title'][:100]
            
            if kwargs.get('description'):
                update_data["snippet"]["description"] = kwargs['description']
            
            if not update_data["snippet"]:
                return {
                    "success": False,
                    "error": "No metadata to update"
                }
            
            if self.youtube:
                request = self.youtube.videos().update(
                    part="snippet",
                    body=update_data
                )
                await asyncio.to_thread(request.execute)
            else:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.put(
                        f"{self.base_url}/videos",
                        params={"part": "snippet"},
                        json=update_data
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            return {
                                "success": False,
                                "error": f"Failed to update video: {response.status} - {error_text}"
                            }
            
            return {
                "success": True,
                "post_id": post_id,
                "updated_at": datetime.now(),
                "message": "Video metadata updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update YouTube video {post_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
