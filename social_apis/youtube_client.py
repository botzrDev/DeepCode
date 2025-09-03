"""
YouTube Data API v3.0 Client

Implements YouTube-specific API integration with OAuth 2.0 authentication,
video uploads, channel management, and analytics.
"""

from datetime import datetime
from typing import Dict, Any, List

from utils.platform_clients import BasePlatformClient
from models.social_models import PostAnalytics, PlatformType


class YouTubeClient(BasePlatformClient):
    """YouTube Data API v3.0 client"""
    
    def _get_api_base_url(self) -> str:
        """Get YouTube API base URL"""
        return "https://www.googleapis.com/youtube/v3"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get YouTube-specific rate limits"""
        return {
            "videos_insert": {"requests": 6, "window": 86400},      # 6 uploads per day
            "search": {"requests": 100, "window": 86400},           # 100 searches per day
            "channels": {"requests": 10000, "window": 86400},       # 10,000 units per day
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test YouTube API connection"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/channels",
                params={
                    "part": "snippet,statistics",
                    "mine": "true"
                }
            )
            
            if result["success"]:
                channels = result["data"].get("items", [])
                
                if channels:
                    channel = channels[0]
                    snippet = channel.get("snippet", {})
                    statistics = channel.get("statistics", {})
                    
                    return {
                        "success": True,
                        "platform": "youtube",
                        "channel_id": channel["id"],
                        "channel_title": snippet.get("title"),
                        "subscriber_count": statistics.get("subscriberCount", 0),
                        "video_count": statistics.get("videoCount", 0),
                        "message": "Successfully connected to YouTube API"
                    }
                else:
                    return {
                        "success": False,
                        "platform": "youtube",
                        "error": "No YouTube channel found for authenticated user"
                    }
            else:
                return {
                    "success": False,
                    "platform": "youtube",
                    "error": result.get("error", "Connection test failed")
                }
        
        except Exception as e:
            self.logger.error(f"YouTube connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "youtube",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's YouTube channel information"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/channels",
                params={
                    "part": "snippet,statistics,brandingSettings",
                    "mine": "true"
                }
            )
            
            if result["success"]:
                channels = result["data"].get("items", [])
                
                if channels:
                    channel = channels[0]
                    snippet = channel.get("snippet", {})
                    statistics = channel.get("statistics", {})
                    branding = channel.get("brandingSettings", {}).get("channel", {})
                    
                    return {
                        "success": True,
                        "profile": {
                            "platform_user_id": channel["id"],
                            "channel_title": snippet.get("title"),
                            "description": snippet.get("description", ""),
                            "custom_url": snippet.get("customUrl", ""),
                            "published_at": snippet.get("publishedAt"),
                            "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                            "subscriber_count": int(statistics.get("subscriberCount", 0)),
                            "video_count": int(statistics.get("videoCount", 0)),
                            "view_count": int(statistics.get("viewCount", 0)),
                            "keywords": branding.get("keywords", ""),
                            "country": snippet.get("country", "")
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": "No YouTube channel found"
                    }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get YouTube profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Upload video to YouTube (simplified version)"""
        
        try:
            # YouTube video upload requires multipart form data and video file
            # This is a simplified placeholder - full implementation would handle:
            # 1. Video file upload to resumable upload endpoint
            # 2. Video metadata setting
            # 3. Thumbnail upload
            # 4. Privacy settings, etc.
            
            if not media_urls or len(media_urls) == 0:
                return {
                    "success": False,
                    "error": "Video URL is required for YouTube upload",
                    "platform": "youtube"
                }
            
            # This would be the actual video upload implementation
            return {
                "success": False,
                "error": "YouTube video upload not fully implemented - requires multipart upload handling",
                "platform": "youtube",
                "note": "Full implementation requires handling resumable uploads and video processing"
            }
        
        except Exception as e:
            self.logger.error(f"Failed to upload to YouTube: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to upload video: {str(e)}"
            }
    
    async def create_community_post(self, content: str) -> Dict[str, Any]:
        """Create a YouTube community post"""
        
        try:
            # YouTube community posts are created via the YouTube Studio API
            # This is not available in the public YouTube Data API v3
            return {
                "success": False,
                "error": "Community posts require YouTube Studio API (not publicly available)",
                "platform": "youtube"
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create YouTube community post: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create community post: {str(e)}"
            }
    
    async def get_analytics(self, video_id: str = None) -> Dict[str, Any]:
        """Get analytics for a YouTube video or channel"""
        
        try:
            if video_id:
                # Get video statistics
                result = await self._make_api_request(
                    method="GET",
                    endpoint="/videos",
                    params={
                        "part": "statistics,snippet",
                        "id": video_id
                    }
                )
                
                if result["success"]:
                    videos = result["data"].get("items", [])
                    
                    if videos:
                        video = videos[0]
                        statistics = video.get("statistics", {})
                        snippet = video.get("snippet", {})
                        
                        analytics = PostAnalytics(
                            post_id=video_id,
                            platform_post_id=video_id,
                            platform=PlatformType.YOUTUBE,
                            views=int(statistics.get("viewCount", 0)),
                            likes=int(statistics.get("likeCount", 0)),
                            comments=int(statistics.get("commentCount", 0)),
                            platform_metrics={
                                "view_count": statistics.get("viewCount", 0),
                                "like_count": statistics.get("likeCount", 0),
                                "dislike_count": statistics.get("dislikeCount", 0),
                                "comment_count": statistics.get("commentCount", 0),
                                "favorite_count": statistics.get("favoriteCount", 0),
                                "published_at": snippet.get("publishedAt"),
                                "title": snippet.get("title"),
                                "duration": snippet.get("duration")
                            }
                        )
                        
                        return {
                            "success": True,
                            "analytics": analytics.to_dict()
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Video {video_id} not found"
                        }
                else:
                    return result
            else:
                # Get channel analytics
                channel_result = await self.get_user_profile()
                
                if channel_result["success"]:
                    profile = channel_result["profile"]
                    
                    return {
                        "success": True,
                        "channel_analytics": {
                            "subscriber_count": profile["subscriber_count"],
                            "video_count": profile["video_count"],
                            "total_view_count": profile["view_count"],
                            "collected_at": datetime.now().isoformat()
                        }
                    }
                else:
                    return channel_result
        
        except Exception as e:
            self.logger.error(f"Failed to get YouTube analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    async def get_channel_videos(self, max_results: int = 25) -> Dict[str, Any]:
        """Get recent videos from the authenticated user's channel"""
        
        try:
            # First get channel ID
            profile_result = await self.get_user_profile()
            if not profile_result["success"]:
                return profile_result
            
            channel_id = profile_result["profile"]["platform_user_id"]
            
            # Search for videos from this channel
            result = await self._make_api_request(
                method="GET",
                endpoint="/search",
                params={
                    "part": "snippet",
                    "channelId": channel_id,
                    "type": "video",
                    "order": "date",
                    "maxResults": max_results
                }
            )
            
            if result["success"]:
                videos = result["data"].get("items", [])
                
                video_list = []
                for video in videos:
                    snippet = video.get("snippet", {})
                    video_list.append({
                        "video_id": video["id"]["videoId"],
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "published_at": snippet.get("publishedAt"),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("default", {}).get("url", "")
                    })
                
                return {
                    "success": True,
                    "videos": video_list
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get YouTube channel videos: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get channel videos: {str(e)}"
            }
    
    async def update_video_metadata(self, video_id: str, title: str = None, description: str = None) -> Dict[str, Any]:
        """Update video metadata"""
        
        try:
            update_data = {
                "id": video_id,
                "snippet": {}
            }
            
            if title:
                update_data["snippet"]["title"] = title
            
            if description:
                update_data["snippet"]["description"] = description
            
            if not update_data["snippet"]:
                return {
                    "success": False,
                    "error": "No metadata to update"
                }
            
            result = await self._make_api_request(
                method="PUT",
                endpoint="/videos",
                params={"part": "snippet"},
                data=update_data
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Video {video_id} metadata updated successfully"
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to update YouTube video metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update video metadata: {str(e)}"
            }