"""
Social Media API Integration Server for ZenAlto

This MCP server provides integration with various social media platforms:
- Twitter/X API v2.0
- Instagram Basic Display API  
- LinkedIn API v2.0
- Facebook Graph API
- YouTube Data API v3.0

Handles OAuth authentication, content posting, analytics, and media management.
"""

import os
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime, timedelta

# MCP Server imports
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# Social Media API clients and OAuth manager
from utils.oauth_manager import OAuthManager
from social_apis.twitter_client import TwitterClient
from social_apis.instagram_client import InstagramClient
from social_apis.linkedin_client import LinkedInClient
from social_apis.facebook_client import FacebookClient
from social_apis.youtube_client import YouTubeClient

# Database models for social media data
from models.social_models import (
    PlatformConnection,
    SocialPost,
    PostAnalytics,
    MediaAsset,
    PlatformType,
    ConnectionStatus
)


class SocialMediaServer:
    """
    MCP Server for Social Media Platform Integration

    Provides tools for:
    - OAuth 2.0 authentication and connection management
    - Content posting across multiple platforms
    - Analytics and engagement tracking
    - Media upload and management
    - Connection health monitoring
    """

    def __init__(self):
        self.server = Server("social-media-server")
        self.logger = logging.getLogger(__name__)

        # Initialize OAuth manager
        self.oauth_manager = OAuthManager()
        
        # Platform clients cache
        self.platform_clients = {}

    # Tool methods that will be registered externally

    async def _get_platform_client(self, platform: str, user_id: str):
        """Get or create platform client for user"""
        
        client_key = f"{platform}:{user_id}"
        
        if client_key not in self.platform_clients:
            # Create new client based on platform
            if platform == "twitter":
                client = TwitterClient(platform, self.oauth_manager, user_id)
            elif platform == "instagram":
                client = InstagramClient(platform, self.oauth_manager, user_id)
            elif platform == "linkedin":
                client = LinkedInClient(platform, self.oauth_manager, user_id)
            elif platform == "facebook":
                client = FacebookClient(platform, self.oauth_manager, user_id)
            elif platform == "youtube":
                client = YouTubeClient(platform, self.oauth_manager, user_id)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            self.platform_clients[client_key] = client
        
        return self.platform_clients[client_key]

    async def get_platform_connections(self, user_id: str) -> Dict[str, Any]:
        """Get status of all platform connections for user"""
        
        try:
            connections = {}
            supported_platforms = ["twitter", "linkedin", "instagram", "facebook", "youtube"]
            
            for platform in supported_platforms:
                try:
                    # Check if we have valid tokens
                    tokens = await self.oauth_manager.get_valid_tokens(platform, user_id)
                    
                    if tokens:
                        # Create client and test connection
                        client = await self._get_platform_client(platform, user_id)
                        status = await client.get_connection_status()
                        connections[platform] = status
                    else:
                        connections[platform] = {
                            "platform": platform,
                            "connected": False,
                            "token_valid": False,
                            "last_check": datetime.now().isoformat(),
                            "message": "No valid authentication tokens"
                        }
                
                except Exception as e:
                    self.logger.error(f"Error checking {platform} connection: {str(e)}")
                    connections[platform] = {
                        "platform": platform,
                        "connected": False,
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
            
            return {
                "success": True,
                "user_id": user_id,
                "connections": connections,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error getting platform connections: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def post_content(
        self,
        platform: str,
        user_id: str,
        content: str,
        media_urls: List[str] = None
    ) -> Dict[str, Any]:
        """Post content to specified social media platform"""
        
        try:
            # Get platform client
            client = await self._get_platform_client(platform, user_id)
            
            # Check if connected
            tokens = await self.oauth_manager.get_valid_tokens(platform, user_id)
            if not tokens:
                return {
                    "success": False,
                    "platform": platform,
                    "error": "Platform not connected or tokens expired",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Post content
            result = await client.post_content(content, media_urls or [])
            
            return {
                "success": result.get("success", False),
                "platform": platform,
                "user_id": user_id,
                **result,  # Include all result data
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error posting to {platform}: {str(e)}")
            return {
                "success": False,
                "platform": platform,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_analytics(
        self,
        platform: str,
        user_id: str,
        post_id: str = None
    ) -> Dict[str, Any]:
        """Get analytics for platform or specific post"""
        
        try:
            # Get platform client
            client = await self._get_platform_client(platform, user_id)
            
            # Check if connected
            tokens = await self.oauth_manager.get_valid_tokens(platform, user_id)
            if not tokens:
                return {
                    "success": False,
                    "platform": platform,
                    "error": "Platform not connected or tokens expired",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get analytics
            result = await client.get_analytics(post_id)
            
            return {
                "success": result.get("success", False),
                "platform": platform,
                "user_id": user_id,
                "post_id": post_id,
                **result,  # Include all result data
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error getting {platform} analytics: {str(e)}")
            return {
                "success": False,
                "platform": platform,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def get_user_profile(self, platform: str, user_id: str) -> Dict[str, Any]:
        """Get user profile information from platform"""
        
        try:
            # Get platform client
            client = await self._get_platform_client(platform, user_id)
            
            # Check if connected
            tokens = await self.oauth_manager.get_valid_tokens(platform, user_id)
            if not tokens:
                return {
                    "success": False,
                    "platform": platform,
                    "error": "Platform not connected or tokens expired",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get profile
            result = await client.get_user_profile()
            
            return {
                "success": result.get("success", False),
                "platform": platform,
                "user_id": user_id,
                **result,  # Include all result data
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error getting {platform} profile: {str(e)}")
            return {
                "success": False,
                "platform": platform,
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# MCP Server startup
async def main():
    """Main function to run the social media MCP server"""
    logging.basicConfig(level=logging.INFO)
    
    server = SocialMediaServer()
    
    # Run the MCP server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    
    print("🚀 Starting ZenAlto Social Media MCP Server...")
    print("Provides OAuth 2.0 authentication and API integration for social media platforms")
    
    asyncio.run(main())
