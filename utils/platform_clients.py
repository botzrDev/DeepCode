"""
Platform-specific API clients for social media platforms

Each client handles platform-specific authentication, rate limiting,
and API interactions while providing a unified interface.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import aiohttp
from utils.rate_limiter import RateLimiter
from utils.oauth_manager import OAuthManager

class BasePlatformClient(ABC):
    """Base class for all platform API clients"""
    
    def __init__(self, platform: str, oauth_manager: OAuthManager, user_id: str):
        self.platform = platform
        self.oauth_manager = oauth_manager
        self.user_id = user_id
        self.logger = logging.getLogger(f"{__name__}.{platform}")
        self.rate_limiter = RateLimiter(platform)
        
        # Platform-specific configurations
        self.api_base_url = self._get_api_base_url()
        self.rate_limits = self._get_rate_limits()
    
    @abstractmethod
    def _get_api_base_url(self) -> str:
        """Get the base API URL for the platform"""
        pass
    
    @abstractmethod
    def _get_rate_limits(self) -> Dict[str, Any]:
        """Get rate limit configurations for the platform"""
        pass
    
    async def _get_authenticated_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        
        tokens = await self.oauth_manager.get_valid_tokens(self.platform, self.user_id)
        
        if not tokens:
            raise ValueError(f"No valid tokens found for {self.platform}:{self.user_id}")
        
        return {
            "Authorization": f"Bearer {tokens['access_token']}",
            "Content-Type": "application/json"
        }
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        await self.rate_limiter.wait_if_needed()
        
        url = f"{self.api_base_url}{endpoint}"
        headers = await self._get_authenticated_headers()
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers, params=params) as response:
                        return await self._handle_response(response)
                
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data, params=params) as response:
                        return await self._handle_response(response)
                
                elif method.upper() == "PUT":
                    async with session.put(url, headers=headers, json=data, params=params) as response:
                        return await self._handle_response(response)
                
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=headers, params=params) as response:
                        return await self._handle_response(response)
                
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
        
        except Exception as e:
            self.logger.error(f"API request failed for {self.platform}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response with error checking"""
        
        # Record rate limit usage
        self.rate_limiter.record_request(response.status == 200)
        
        if response.status == 200:
            try:
                data = await response.json()
                return {
                    "success": True,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse response: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
        
        elif response.status == 429:  # Rate limited
            # Extract rate limit reset time if available
            reset_header = response.headers.get("x-rate-limit-reset")
            if reset_header:
                reset_time = int(reset_header)
                wait_time = max(0, reset_time - datetime.now().timestamp())
                
                self.logger.warning(f"Rate limited by {self.platform}, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
            
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "retry_after": wait_time if reset_header else 60,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            error_text = await response.text()
            self.logger.error(f"API error {response.status} for {self.platform}: {error_text}")
            
            return {
                "success": False,
                "error": f"HTTP {response.status}: {error_text}",
                "status_code": response.status,
                "timestamp": datetime.now().isoformat()
            }
    
    # Abstract methods that each platform client must implement
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the platform"""
        pass
    
    @abstractmethod
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile information"""
        pass
    
    @abstractmethod
    async def post_content(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def get_analytics(self, post_id: str = None) -> Dict[str, Any]:
        """Get analytics for posts or account"""
        pass
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get connection status and health check"""
        
        try:
            # Test connection
            test_result = await self.test_connection()
            
            # Get rate limit status
            rate_status = self.rate_limiter.get_rate_limit_status()
            
            # Check token validity
            tokens = await self.oauth_manager.get_valid_tokens(self.platform, self.user_id)
            token_valid = tokens is not None
            
            return {
                "platform": self.platform,
                "connected": test_result.get("success", False),
                "token_valid": token_valid,
                "rate_limit_status": rate_status,
                "last_check": datetime.now().isoformat(),
                "api_base_url": self.api_base_url
            }
            
        except Exception as e:
            self.logger.error(f"Error checking connection status for {self.platform}: {str(e)}")
            return {
                "platform": self.platform,
                "connected": False,
                "token_valid": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }