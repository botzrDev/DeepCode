"""
Facebook Graph API Client

Implements Facebook-specific API integration with OAuth 2.0 authentication,
page management, content posting, and analytics.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.platform_clients import BasePlatformClient
from models.social_models import PostAnalytics, PlatformType


class FacebookClient(BasePlatformClient):
    """Facebook Graph API client"""
    
    def _get_api_base_url(self) -> str:
        """Get Facebook Graph API base URL"""
        return "https://graph.facebook.com/v18.0"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get Facebook-specific rate limits"""
        return {
            "page_posts": {"requests": 25, "window": 3600},         # 25 per hour
            "page_read": {"requests": 240, "window": 3600},         # 240 per hour
            "insights": {"requests": 200, "window": 3600},          # 200 per hour
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Facebook API connection"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me",
                params={
                    "fields": "id,name,email"
                }
            )
            
            if result["success"]:
                user_data = result["data"]
                return {
                    "success": True,
                    "platform": "facebook",
                    "user_id": user_data["id"],
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "message": "Successfully connected to Facebook API"
                }
            else:
                return {
                    "success": False,
                    "platform": "facebook",
                    "error": result.get("error", "Connection test failed")
                }
        
        except Exception as e:
            self.logger.error(f"Facebook connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "facebook",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's Facebook profile"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me",
                params={
                    "fields": "id,name,email,picture.width(200).height(200)"
                }
            )
            
            if result["success"]:
                profile_data = result["data"]
                picture_url = ""
                
                if "picture" in profile_data:
                    picture_url = profile_data["picture"].get("data", {}).get("url", "")
                
                return {
                    "success": True,
                    "profile": {
                        "platform_user_id": profile_data["id"],
                        "name": profile_data.get("name"),
                        "email": profile_data.get("email"),
                        "picture_url": picture_url
                    }
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Facebook profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def get_pages(self) -> Dict[str, Any]:
        """Get Facebook pages the user can manage"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me/accounts",
                params={
                    "fields": "id,name,category,access_token,tasks"
                }
            )
            
            if result["success"]:
                pages = result["data"].get("data", [])
                
                return {
                    "success": True,
                    "pages": [
                        {
                            "page_id": page["id"],
                            "name": page["name"],
                            "category": page.get("category"),
                            "tasks": page.get("tasks", []),
                            "can_post": "MANAGE" in page.get("tasks", []) or "CREATE_CONTENT" in page.get("tasks", [])
                        }
                        for page in pages
                    ]
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Facebook pages: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get pages: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None, page_id: str = None) -> Dict[str, Any]:
        """Post content to Facebook (user timeline or page)"""
        
        try:
            endpoint = "/me/feed"  # Default to user timeline
            
            if page_id:
                # Post to a specific page
                endpoint = f"/{page_id}/feed"
            
            post_data = {
                "message": content
            }
            
            # Handle media attachments
            if media_urls:
                # For simplicity, just attach the first image URL
                # Full implementation would handle multiple media types
                if len(media_urls) > 0:
                    post_data["link"] = media_urls[0]
            
            result = await self._make_api_request(
                method="POST",
                endpoint=endpoint,
                data=post_data
            )
            
            if result["success"]:
                post_id = result["data"].get("id")
                return {
                    "success": True,
                    "platform": "facebook",
                    "platform_post_id": post_id,
                    "content": content,
                    "page_id": page_id,
                    "published_at": datetime.now().isoformat(),
                    "url": f"https://www.facebook.com/{post_id}" if post_id else None
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to post to Facebook: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to post to Facebook: {str(e)}"
            }
    
    async def get_analytics(self, post_id: str = None, page_id: str = None) -> Dict[str, Any]:
        """Get analytics for a Facebook post or page"""
        
        try:
            if post_id:
                # Get post insights
                result = await self._make_api_request(
                    method="GET",
                    endpoint=f"/{post_id}/insights",
                    params={
                        "metric": "post_impressions,post_engaged_users,post_reactions_by_type_total,post_clicks"
                    }
                )
                
                if result["success"]:
                    insights_data = result["data"].get("data", [])
                    
                    # Parse insights data
                    metrics = {}
                    for insight in insights_data:
                        metric_name = insight.get("name")
                        metric_values = insight.get("values", [])
                        if metric_values:
                            metrics[metric_name] = metric_values[0].get("value", 0)
                    
                    analytics = PostAnalytics(
                        post_id=post_id,
                        platform_post_id=post_id,
                        platform=PlatformType.FACEBOOK,
                        impressions=metrics.get("post_impressions", 0),
                        likes=metrics.get("post_reactions_by_type_total", {}).get("like", 0),
                        clicks=metrics.get("post_clicks", 0),
                        platform_metrics=metrics
                    )
                    
                    # Calculate engagement rate
                    analytics.calculate_engagement_rate()
                    analytics.calculate_ctr()
                    
                    return {
                        "success": True,
                        "analytics": analytics.to_dict()
                    }
                else:
                    return result
            
            elif page_id:
                # Get page insights
                result = await self._make_api_request(
                    method="GET",
                    endpoint=f"/{page_id}/insights",
                    params={
                        "metric": "page_fans,page_impressions,page_engaged_users",
                        "period": "day",
                        "since": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                        "until": datetime.now().strftime("%Y-%m-%d")
                    }
                )
                
                if result["success"]:
                    insights_data = result["data"].get("data", [])
                    
                    page_metrics = {}
                    for insight in insights_data:
                        metric_name = insight.get("name")
                        metric_values = insight.get("values", [])
                        if metric_values:
                            # Get latest value
                            page_metrics[metric_name] = metric_values[-1].get("value", 0)
                    
                    return {
                        "success": True,
                        "page_analytics": {
                            "page_id": page_id,
                            "followers_count": page_metrics.get("page_fans", 0),
                            "impressions": page_metrics.get("page_impressions", 0),
                            "engaged_users": page_metrics.get("page_engaged_users", 0),
                            "collected_at": datetime.now().isoformat(),
                            "platform_metrics": page_metrics
                        }
                    }
                else:
                    return result
            else:
                # Get user account info
                profile_result = await self.get_user_profile()
                return profile_result
        
        except Exception as e:
            self.logger.error(f"Failed to get Facebook analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a Facebook post"""
        
        try:
            result = await self._make_api_request(
                method="DELETE",
                endpoint=f"/{post_id}"
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Post {post_id} deleted successfully"
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to delete Facebook post {post_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to delete post: {str(e)}"
            }
    
    async def get_page_posts(self, page_id: str, limit: int = 25) -> Dict[str, Any]:
        """Get recent posts from a Facebook page"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint=f"/{page_id}/posts",
                params={
                    "fields": "id,message,created_time,permalink_url,insights.metric(post_impressions,post_engaged_users)",
                    "limit": limit
                }
            )
            
            if result["success"]:
                posts = result["data"].get("data", [])
                
                return {
                    "success": True,
                    "posts": posts
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Facebook page posts: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get page posts: {str(e)}"
            }