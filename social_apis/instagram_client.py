"""
Instagram Basic Display API Client

Implements Instagram-specific API integration with OAuth 2.0 authentication,
media posting, and basic analytics.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.platform_clients import BasePlatformClient
from models.social_models import PostAnalytics, PlatformType


class InstagramClient(BasePlatformClient):
    """Instagram Basic Display API client"""
    
    def _get_api_base_url(self) -> str:
        """Get Instagram API base URL"""
        return "https://graph.instagram.com"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get Instagram-specific rate limits"""
        return {
            "media_read": {"requests": 200, "window": 3600},        # 200 per hour
            "media_create": {"requests": 25, "window": 3600},       # 25 per hour
            "user_info": {"requests": 240, "window": 3600},         # 240 per hour
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Instagram API connection"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me",
                params={
                    "fields": "id,username,media_count"
                }
            )
            
            if result["success"]:
                user_data = result["data"]
                return {
                    "success": True,
                    "platform": "instagram",
                    "user_id": user_data["id"],
                    "username": user_data.get("username"),
                    "media_count": user_data.get("media_count", 0),
                    "message": "Successfully connected to Instagram API"
                }
            else:
                return {
                    "success": False,
                    "platform": "instagram",
                    "error": result.get("error", "Connection test failed")
                }
        
        except Exception as e:
            self.logger.error(f"Instagram connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "instagram",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's Instagram profile"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me",
                params={
                    "fields": "id,username,account_type,media_count"
                }
            )
            
            if result["success"]:
                profile_data = result["data"]
                
                return {
                    "success": True,
                    "profile": {
                        "platform_user_id": profile_data["id"],
                        "username": profile_data.get("username"),
                        "account_type": profile_data.get("account_type", "PERSONAL"),
                        "media_count": profile_data.get("media_count", 0)
                    }
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Instagram profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Post content to Instagram (Note: Basic Display API is read-only)"""
        
        # Instagram Basic Display API doesn't support posting
        # For posting, you'd need Instagram Graph API (business accounts)
        return {
            "success": False,
            "error": "Instagram Basic Display API doesn't support posting. Use Instagram Graph API for business accounts.",
            "platform": "instagram"
        }
    
    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Get analytics for Instagram media or account"""
        
        try:
            if post_id:
                # Get specific media item analytics
                result = await self._make_api_request(
                    method="GET",
                    endpoint=f"/{post_id}",
                    params={
                        "fields": "id,media_type,media_url,permalink,timestamp,caption"
                    }
                )
                
                if result["success"]:
                    media_data = result["data"]
                    
                    # Instagram Basic Display API has limited analytics
                    analytics = PostAnalytics(
                        post_id=post_id,
                        platform_post_id=media_data["id"],
                        platform=PlatformType.INSTAGRAM,
                        platform_metrics=media_data
                    )
                    
                    return {
                        "success": True,
                        "analytics": analytics.to_dict()
                    }
                else:
                    return result
            else:
                # Get user media for account analytics
                result = await self._make_api_request(
                    method="GET",
                    endpoint="/me/media",
                    params={
                        "fields": "id,media_type,timestamp,caption",
                        "limit": 25
                    }
                )
                
                if result["success"]:
                    media_list = result["data"].get("data", [])
                    
                    return {
                        "success": True,
                        "account_analytics": {
                            "total_media": len(media_list),
                            "recent_media": media_list,
                            "collected_at": datetime.now().isoformat()
                        }
                    }
                else:
                    return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Instagram analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    async def get_media_list(self, limit: int = 25) -> Dict[str, Any]:
        """Get user's recent media"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/me/media",
                params={
                    "fields": "id,media_type,media_url,permalink,timestamp,caption",
                    "limit": limit
                }
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "media": result["data"].get("data", [])
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get Instagram media list: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get media list: {str(e)}"
            }


class InstagramGraphClient(BasePlatformClient):
    """Instagram Graph API client for business accounts"""
    
    def _get_api_base_url(self) -> str:
        """Get Instagram Graph API base URL"""
        return "https://graph.facebook.com/v18.0"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get Instagram Graph API rate limits"""
        return {
            "media_publish": {"requests": 25, "window": 3600},      # 25 per hour
            "media_read": {"requests": 240, "window": 3600},        # 240 per hour
            "insights": {"requests": 200, "window": 3600},          # 200 per hour
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Instagram Graph API connection"""
        
        try:
            # Get Instagram Business Account ID first
            result = await self._make_api_request(
                method="GET",
                endpoint="/me/accounts",
                params={
                    "fields": "instagram_business_account"
                }
            )
            
            if result["success"]:
                pages = result["data"].get("data", [])
                instagram_accounts = []
                
                for page in pages:
                    if "instagram_business_account" in page:
                        instagram_accounts.append(page["instagram_business_account"])
                
                if instagram_accounts:
                    ig_account = instagram_accounts[0]  # Use first available account
                    
                    # Test with account info
                    account_result = await self._make_api_request(
                        method="GET",
                        endpoint=f"/{ig_account['id']}",
                        params={
                            "fields": "id,username,name,biography,followers_count,media_count"
                        }
                    )
                    
                    if account_result["success"]:
                        account_data = account_result["data"]
                        return {
                            "success": True,
                            "platform": "instagram_business",
                            "user_id": account_data["id"],
                            "username": account_data.get("username"),
                            "name": account_data.get("name"),
                            "followers_count": account_data.get("followers_count", 0),
                            "message": "Successfully connected to Instagram Graph API"
                        }
                    else:
                        return account_result
                else:
                    return {
                        "success": False,
                        "platform": "instagram_business",
                        "error": "No Instagram Business Account found"
                    }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Instagram Graph API connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "instagram_business",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get Instagram business account profile"""
        
        try:
            # This would require getting the Instagram Business Account ID
            # Implementation would be similar to test_connection method
            return await self.test_connection()
        
        except Exception as e:
            self.logger.error(f"Failed to get Instagram business profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Post content to Instagram business account"""
        
        try:
            # This would implement the Instagram Graph API posting flow:
            # 1. Upload media to Instagram
            # 2. Create media container
            # 3. Publish media container
            
            return {
                "success": False,
                "error": "Instagram Graph API posting not fully implemented yet",
                "platform": "instagram_business"
            }
        
        except Exception as e:
            self.logger.error(f"Failed to post to Instagram business: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to post: {str(e)}"
            }
    
    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Get Instagram business analytics"""
        
        try:
            # Instagram Graph API provides rich analytics for business accounts
            return {
                "success": False,
                "error": "Instagram Graph API analytics not fully implemented yet",
                "platform": "instagram_business"
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get Instagram business analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }