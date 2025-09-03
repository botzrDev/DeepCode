import asyncio
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json
import aiohttp
from urllib.parse import urlencode, parse_qs
import logging

from .token_storage import TokenStorage


class OAuthManager:
    """
    Centralized OAuth 2.0 authentication manager.
    
    Features:
    - Platform-agnostic OAuth flow
    - PKCE support for enhanced security
    - Token management and refresh
    - State validation
    - Secure storage integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OAuth manager.
        
        Config includes platform OAuth configurations.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.pending_authentications = {}  # Track ongoing auth flows
        self.token_storage = TokenStorage()  # Secure token storage
    
    async def initiate_oauth_flow(
        self,
        platform: str,
        user_id: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Initiate OAuth authentication flow.
        
        Returns:
        {
            "auth_url": str,  # URL to redirect user to
            "state": str,     # State parameter for validation
            "code_verifier": str,  # PKCE verifier (if supported)
            "expires_at": datetime
        }
        """
        try:
            # Generate secure state parameter
            state = self._generate_state()
            
            # Generate PKCE parameters if supported
            code_verifier = None
            code_challenge = None
            
            if self._platform_supports_pkce(platform):
                code_verifier = self._generate_code_verifier()
                code_challenge = self._generate_code_challenge(code_verifier)
            
            # Get platform OAuth config
            platform_config = self._get_platform_config(platform)
            
            # Build authorization URL
            params = {
                "client_id": platform_config["client_id"],
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "state": state,
                "scope": " ".join(scopes or platform_config.get("default_scopes", []))
            }
            
            # Add PKCE challenge if supported
            if code_challenge:
                params["code_challenge"] = code_challenge
                params["code_challenge_method"] = "S256"
            
            # Platform-specific parameters
            if platform == "linkedin":
                params["response_type"] = "code"
            elif platform == "twitter":
                params["response_type"] = "code"
                params["code_challenge_method"] = "plain" if not code_challenge else "S256"
            
            auth_url = f"{platform_config['auth_url']}?{urlencode(params)}"
            
            # Store pending authentication
            self.pending_authentications[state] = {
                "platform": platform,
                "user_id": user_id,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=10)
            }
            
            return {
                "auth_url": auth_url,
                "state": state,
                "code_verifier": code_verifier,
                "expires_at": datetime.now() + timedelta(minutes=10)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate OAuth flow: {e}")
            raise
    
    async def handle_oauth_callback(
        self,
        platform: str,
        code: str,
        state: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.
        
        Returns:
        {
            "success": bool,
            "access_token": str,
            "refresh_token": Optional[str],
            "expires_in": int,
            "user_info": Dict,
            "error": Optional[str]
        }
        """
        try:
            # Handle error responses
            if error:
                return {
                    "success": False,
                    "error": f"OAuth error: {error}"
                }
            
            # Validate state
            if state not in self.pending_authentications:
                return {
                    "success": False,
                    "error": "Invalid state parameter"
                }
            
            pending_auth = self.pending_authentications[state]
            
            # Check expiration
            if datetime.now() > pending_auth["expires_at"]:
                del self.pending_authentications[state]
                return {
                    "success": False,
                    "error": "Authentication expired"
                }
            
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(
                platform=platform,
                code=code,
                redirect_uri=pending_auth["redirect_uri"],
                code_verifier=pending_auth.get("code_verifier")
            )
            
            if not tokens.get("access_token"):
                return {
                    "success": False,
                    "error": "Failed to obtain access token"
                }
            
            # Get user information
            user_info = await self._get_user_info(platform, tokens["access_token"])
            
            # Store tokens securely
            await self.token_storage.store_tokens(
                user_id=pending_auth["user_id"],
                platform=platform,
                tokens=tokens,
                user_info=user_info
            )
            
            # Clean up pending authentication
            del self.pending_authentications[state]
            
            return {
                "success": True,
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in", 3600),
                "user_info": user_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to handle OAuth callback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def refresh_token(
        self,
        user_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Refresh expired access token.
        
        Returns:
        {
            "success": bool,
            "access_token": str,
            "expires_in": int,
            "error": Optional[str]
        }
        """
        try:
            # Get stored refresh token
            stored_tokens = await self.token_storage.get_tokens(user_id, platform)
            
            if not stored_tokens or not stored_tokens.get("refresh_token"):
                return {
                    "success": False,
                    "error": "No refresh token available"
                }
            
            platform_config = self._get_platform_config(platform)
            
            # Request new tokens
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": stored_tokens["refresh_token"],
                    "client_id": platform_config["client_id"],
                    "client_secret": platform_config["client_secret"]
                }
                
                async with session.post(
                    platform_config["token_url"],
                    data=data
                ) as response:
                    if response.status == 200:
                        new_tokens = await response.json()
                        
                        # Update stored tokens
                        await self.token_storage.update_tokens(
                            user_id=user_id,
                            platform=platform,
                            tokens=new_tokens
                        )
                        
                        return {
                            "success": True,
                            "access_token": new_tokens["access_token"],
                            "expires_in": new_tokens.get("expires_in", 3600)
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"Token refresh failed: {error_data}"
                        }
                        
        except Exception as e:
            self.logger.error(f"Failed to refresh token: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def revoke_access(
        self,
        user_id: str,
        platform: str
    ) -> bool:
        """
        Revoke platform access and delete stored tokens.
        
        Returns:
            Success status
        """
        try:
            # Get stored tokens
            tokens = await self.token_storage.get_tokens(user_id, platform)
            
            if tokens:
                # Revoke tokens with platform
                await self._revoke_platform_tokens(platform, tokens)
            
            # Delete stored tokens
            await self.token_storage.delete_tokens(user_id, platform)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke access: {e}")
            return False
    
    # PKCE Helper Methods
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        return base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    def _generate_state(self) -> str:
        """Generate secure state parameter."""
        return secrets.token_urlsafe(32)
    
    def _platform_supports_pkce(self, platform: str) -> bool:
        """Check if platform supports PKCE."""
        return platform in ["twitter", "linkedin", "facebook"]
    
    # Platform-specific implementations
    
    async def _exchange_code_for_tokens(
        self,
        platform: str,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        
        platform_config = self._get_platform_config(platform)
        
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": platform_config["client_id"],
                "client_secret": platform_config["client_secret"]
            }
            
            # Add PKCE verifier if used
            if code_verifier:
                data["code_verifier"] = code_verifier
            
            # Platform-specific adjustments
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            if platform == "linkedin":
                headers["Accept"] = "application/json"
            
            async with session.post(
                platform_config["token_url"],
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Token exchange failed: {error_text}")
    
    async def _get_user_info(
        self,
        platform: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Get user information using access token."""
        
        platform_config = self._get_platform_config(platform)
        user_info_url = platform_config.get("user_info_url")
        
        if not user_info_url:
            return {}
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Platform-specific headers
            if platform == "linkedin":
                headers["X-Restli-Protocol-Version"] = "2.0.0"
            
            async with session.get(
                user_info_url,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_user_info(platform, data)
                else:
                    self.logger.warning(f"Failed to get user info: {response.status}")
                    return {}
    
    def _parse_user_info(self, platform: str, data: Dict) -> Dict[str, Any]:
        """Parse platform-specific user info response."""
        
        if platform == "twitter":
            return {
                "id": data.get("data", {}).get("id"),
                "username": data.get("data", {}).get("username"),
                "name": data.get("data", {}).get("name"),
                "profile_image": data.get("data", {}).get("profile_image_url")
            }
        elif platform == "linkedin":
            return {
                "id": data.get("id"),
                "name": f"{data.get('localizedFirstName', '')} {data.get('localizedLastName', '')}",
                "email": data.get("email"),
                "profile_image": data.get("profilePicture", {}).get("displayImage")
            }
        elif platform == "instagram":
            return {
                "id": data.get("id"),
                "username": data.get("username"),
                "name": data.get("name"),
                "profile_image": data.get("profile_picture")
            }
        else:
            return data
    
    def _get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific OAuth configuration."""
        
        configs = {
            "twitter": {
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "user_info_url": "https://api.twitter.com/2/users/me",
                "revoke_url": "https://api.twitter.com/2/oauth2/revoke",
                "default_scopes": ["tweet.read", "tweet.write", "users.read", "follows.read"]
            },
            "linkedin": {
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "user_info_url": "https://api.linkedin.com/v2/me",
                "default_scopes": ["r_liteprofile", "r_emailaddress", "w_member_social"]
            },
            "instagram": {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "user_info_url": "https://graph.instagram.com/me",
                "default_scopes": ["user_profile", "user_media"]
            },
            "facebook": {
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "user_info_url": "https://graph.facebook.com/me",
                "default_scopes": ["public_profile", "email", "pages_manage_posts"]
            },
            "youtube": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "default_scopes": ["https://www.googleapis.com/auth/youtube.upload"]
            }
        }
        
        platform_config = configs.get(platform, {})
        
        # Add client credentials from main config
        platform_config.update(self.config.get(platform, {}))
        
        return platform_config

    async def _revoke_platform_tokens(self, platform: str, tokens: Dict[str, Any]) -> None:
        """Revoke tokens with platform."""
        platform_config = self._get_platform_config(platform)
        revoke_url = platform_config.get("revoke_url")
        
        if not revoke_url:
            return  # Platform doesn't support token revocation
        
        try:
            revoke_data = {"token": tokens.get("access_token")}
            
            if platform == "twitter":
                revoke_data["client_id"] = platform_config["client_id"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    revoke_url,
                    data=revoke_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    if response.status in [200, 204]:
                        self.logger.info(f"Successfully revoked tokens for {platform}")
                    else:
                        self.logger.warning(f"Token revocation returned status {response.status} for {platform}")
        
        except Exception as e:
            self.logger.warning(f"Error revoking tokens for {platform}: {str(e)}")