"""
LinkedIn API v2.0 Client

Implements LinkedIn-specific API integration with OAuth 2.0 authentication,
professional content posting, and profile management.
"""

from datetime import datetime
from typing import Dict, Any, List

from utils.platform_clients import BasePlatformClient
from models.social_models import PostAnalytics, PlatformType


class LinkedInClient(BasePlatformClient):
    """LinkedIn API v2.0 client"""
    
    def _get_api_base_url(self) -> str:
        """Get LinkedIn API base URL"""
        return "https://api.linkedin.com/v2"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get LinkedIn-specific rate limits"""
        return {
            "profile_read": {"requests": 100, "window": 3600},      # 100 per hour
            "shares_create": {"requests": 100, "window": 86400},    # 100 per day
            "ugc_posts": {"requests": 100, "window": 86400},        # 100 per day
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test LinkedIn API connection"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/people/~",
                params={
                    "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"
                }
            )
            
            if result["success"]:
                profile_data = result["data"]
                first_name = profile_data.get("firstName", {}).get("localized", {})
                last_name = profile_data.get("lastName", {}).get("localized", {})
                
                # Get the first available name (LinkedIn returns localized names)
                display_name = ""
                if first_name:
                    display_name = list(first_name.values())[0]
                if last_name:
                    display_name += " " + list(last_name.values())[0]
                
                return {
                    "success": True,
                    "platform": "linkedin",
                    "user_id": profile_data.get("id"),
                    "display_name": display_name.strip(),
                    "message": "Successfully connected to LinkedIn API"
                }
            else:
                return {
                    "success": False,
                    "platform": "linkedin",
                    "error": result.get("error", "Connection test failed")
                }
        
        except Exception as e:
            self.logger.error(f"LinkedIn connection test failed: {str(e)}")
            return {
                "success": False,
                "platform": "linkedin",
                "error": f"Connection test failed: {str(e)}"
            }
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's LinkedIn profile"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/people/~",
                params={
                    "projection": "(id,firstName,lastName,headline,summary,profilePicture(displayImage~:playableStreams),positions,industry,location)"
                }
            )
            
            if result["success"]:
                profile_data = result["data"]
                
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
                    "profile": {
                        "platform_user_id": profile_data.get("id"),
                        "display_name": display_name.strip(),
                        "headline": profile_data.get("headline", ""),
                        "summary": profile_data.get("summary", ""),
                        "industry": profile_data.get("industry", ""),
                        "location": profile_data.get("location", {}).get("name", ""),
                        "profile_image_url": profile_pic_url
                    }
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get LinkedIn profile: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get profile: {str(e)}"
            }
    
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        
        try:
            # Get user profile first to get the person URN
            profile_result = await self.get_user_profile()
            if not profile_result["success"]:
                return profile_result
            
            person_id = profile_result["profile"]["platform_user_id"]
            person_urn = f"urn:li:person:{person_id}"
            
            # Prepare the post data using UGC Posts API
            post_data = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Handle media attachments (if any)
            if media_urls:
                # For LinkedIn, we'd need to upload media first
                # This is a simplified version
                self.logger.warning("Media upload not yet fully implemented for LinkedIn")
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            
            result = await self._make_api_request(
                method="POST",
                endpoint="/ugcPosts",
                data=post_data
            )
            
            if result["success"]:
                post_id = result["data"].get("id", "")
                return {
                    "success": True,
                    "platform": "linkedin",
                    "platform_post_id": post_id,
                    "content": content,
                    "published_at": datetime.now().isoformat(),
                    "url": f"https://www.linkedin.com/feed/update/{post_id}/"
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to post to LinkedIn: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to post to LinkedIn: {str(e)}"
            }
    
    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Get analytics for a specific LinkedIn post or account"""
        
        try:
            if post_id:
                # Get UGC post analytics
                result = await self._make_api_request(
                    method="GET",
                    endpoint=f"/socialActions/{post_id}",
                    params={
                        "projection": "(likesSummary,commentsSummary,sharesSummary,clicksSummary,impressionsSummary)"
                    }
                )
                
                if result["success"]:
                    data = result["data"]
                    
                    analytics = PostAnalytics(
                        post_id=post_id,
                        platform_post_id=post_id,
                        platform=PlatformType.LINKEDIN,
                        likes=data.get("likesSummary", {}).get("totalLikes", 0),
                        shares=data.get("sharesSummary", {}).get("totalShares", 0),
                        comments=data.get("commentsSummary", {}).get("totalComments", 0),
                        clicks=data.get("clicksSummary", {}).get("totalClicks", 0),
                        impressions=data.get("impressionsSummary", {}).get("totalImpressions", 0),
                        platform_metrics=data
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
            else:
                # Get account-level analytics (simplified)
                profile_result = await self.get_user_profile()
                
                if profile_result["success"]:
                    return {
                        "success": True,
                        "account_analytics": {
                            "profile_data": profile_result["profile"],
                            "collected_at": datetime.now().isoformat()
                        }
                    }
                else:
                    return profile_result
        
        except Exception as e:
            self.logger.error(f"Failed to get LinkedIn analytics: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get analytics: {str(e)}"
            }
    
    async def get_company_pages(self) -> Dict[str, Any]:
        """Get company pages the user can manage"""
        
        try:
            result = await self._make_api_request(
                method="GET",
                endpoint="/people/~/roleAssignments",
                params={
                    "projection": "(elements*(*,organization~(id,name,localizedName)))",
                    "role": "ADMINISTRATOR"
                }
            )
            
            if result["success"]:
                elements = result["data"].get("elements", [])
                company_pages = []
                
                for element in elements:
                    org_data = element.get("organization~", {})
                    if org_data:
                        company_pages.append({
                            "company_id": org_data.get("id"),
                            "name": org_data.get("localizedName", org_data.get("name", "")),
                            "role": element.get("role", "")
                        })
                
                return {
                    "success": True,
                    "company_pages": company_pages
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to get LinkedIn company pages: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get company pages: {str(e)}"
            }
    
    async def post_to_company_page(self, company_id: str, content: str) -> Dict[str, Any]:
        """Post content to a LinkedIn company page"""
        
        try:
            company_urn = f"urn:li:organization:{company_id}"
            
            post_data = {
                "author": company_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            result = await self._make_api_request(
                method="POST",
                endpoint="/ugcPosts",
                data=post_data
            )
            
            if result["success"]:
                post_id = result["data"].get("id", "")
                return {
                    "success": True,
                    "platform": "linkedin",
                    "platform_post_id": post_id,
                    "content": content,
                    "company_id": company_id,
                    "published_at": datetime.now().isoformat()
                }
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Failed to post to LinkedIn company page: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to post to company page: {str(e)}"
            }