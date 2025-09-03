"""
Abstract base class for social media API clients.

All platform clients should inherit from this class to ensure
consistent interface and behavior across different social media platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseSocialClient(ABC):
    """
    Abstract base class for social media API clients.
    
    All platform clients should inherit from this class.
    """
    
    @abstractmethod
    async def post_content(
        self,
        text: str,
        media: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Post content to the platform.
        
        Args:
            text: Content text to post
            media: Optional list of media file paths or URLs
            **kwargs: Platform-specific parameters
            
        Returns:
            Dict containing:
            {
                "success": bool,
                "post_id": str,
                "url": str,
                "platform": str,
                "published_at": datetime,
                "error": Optional[str]
            }
        """
        pass
    
    @abstractmethod
    async def get_analytics(
        self,
        post_ids: List[str],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for posts.
        
        Args:
            post_ids: List of post IDs to get analytics for
            metrics: Optional list of specific metrics to retrieve
            
        Returns:
            Dict containing:
            {
                "success": bool,
                "metrics": Dict[str, Dict[str, Any]],
                "error": Optional[str]
            }
        """
        pass
    
    @abstractmethod
    async def get_user_info(self) -> Dict[str, Any]:
        """
        Get authenticated user information.
        
        Returns:
            Dict containing:
            {
                "success": bool,
                "user_info": Dict[str, Any],
                "error": Optional[str]
            }
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a post.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            Dict containing:
            {
                "success": bool,
                "message": str,
                "error": Optional[str]
            }
        """
        pass
    
    @abstractmethod
    async def update_post(
        self,
        post_id: str,
        text: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing post.
        
        Args:
            post_id: ID of the post to update
            text: New text content
            **kwargs: Platform-specific parameters
            
        Returns:
            Dict containing:
            {
                "success": bool,
                "post_id": str,
                "updated_at": datetime,
                "error": Optional[str]
            }
        """
        pass

    # Optional methods with default implementations
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the platform.
        
        Default implementation tries to get user info.
        
        Returns:
            Dict containing connection status
        """
        try:
            user_info_result = await self.get_user_info()
            return {
                "success": user_info_result.get("success", False),
                "connected": user_info_result.get("success", False),
                "message": "Connection test completed",
                "error": user_info_result.get("error")
            }
        except Exception as e:
            return {
                "success": False,
                "connected": False,
                "message": "Connection test failed",
                "error": str(e)
            }
    
    def get_platform_name(self) -> str:
        """
        Get the platform name.
        
        Returns platform name based on class name by default.
        """
        return self.__class__.__name__.replace("Client", "").lower()