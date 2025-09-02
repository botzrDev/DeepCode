# ZENALTO Integration Assignment #4: Platform Authentication & API Integration

## Objective
Implement secure OAuth 2.0 authentication flows and API integration for all major social media platforms (Twitter/X, LinkedIn, Instagram, Facebook, YouTube) while maintaining security best practices and seamless user experience.

## Background
ZENALTO requires secure connections to multiple social media platforms to post content, retrieve analytics, and manage campaigns. Each platform has different OAuth 2.0 implementations, rate limits, and API requirements that must be handled correctly.

## Key Requirements

### 1. Security & Compliance
- **OAuth 2.0 with PKCE**: Implement secure authentication flows
- **Token Management**: Secure storage, refresh, and rotation of access tokens
- **Data Encryption**: Encrypt all stored credentials and sensitive data
- **Compliance**: GDPR/privacy compliance for data handling
- **Rate Limiting**: Respect all platform API rate limits

### 2. Platform Coverage
- **Twitter/X API v2.0**: Complete integration with posting and analytics
- **LinkedIn API v2.0**: Professional content posting and company pages
- **Instagram Basic Display + Graph API**: Personal and business accounts
- **Facebook Graph API**: Page management and posting
- **YouTube Data API v3.0**: Video uploads and community posts

### 3. User Experience
- **Seamless Connection Flow**: One-click platform connections
- **Status Monitoring**: Real-time connection health monitoring
- **Error Recovery**: Automatic token refresh and error handling
- **Multi-Account Support**: Support for multiple accounts per platform

## Implementation Architecture

### 1. OAuth Manager Implementation

**File**: `utils/oauth_manager.py` (New)

```python
"""
OAuth 2.0 Manager for Social Media Platform Authentication

Handles secure OAuth flows, token management, and API client initialization
for all supported social media platforms.
"""

import os
import json
import asyncio
import logging
import secrets
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, parse_qs

import aiohttp
from cryptography.fernet import Fernet
from mcp_agent.storage import SecureStorage

class OAuthManager:
    def __init__(self, config_path: str = "mcp_agent.config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.secure_storage = SecureStorage()
        
        # Load platform configurations
        self.platform_configs = self._load_platform_configs(config_path)
        
        # Initialize encryption for token storage
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # OAuth state storage (in-memory for demo, use Redis in production)
        self.oauth_states = {}
    
    def _load_platform_configs(self, config_path: str) -> Dict[str, Any]:
        """Load OAuth configurations for all platforms"""
        
        return {
            "twitter": {
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "revoke_url": "https://api.twitter.com/2/oauth2/revoke",
                "scopes": ["tweet.read", "tweet.write", "users.read", "offline.access"],
                "client_id": os.getenv("TWITTER_CLIENT_ID"),
                "client_secret": os.getenv("TWITTER_CLIENT_SECRET"),
                "redirect_uri": os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8501/oauth/twitter"),
                "use_pkce": True
            },
            "linkedin": {
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "scopes": ["w_member_social", "r_liteprofile", "r_emailaddress"],
                "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
                "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
                "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8501/oauth/linkedin"),
                "use_pkce": False
            },
            "instagram": {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "scopes": ["user_profile", "user_media"],
                "client_id": os.getenv("INSTAGRAM_CLIENT_ID"),
                "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET"),
                "redirect_uri": os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8501/oauth/instagram"),
                "use_pkce": False
            },
            "facebook": {
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "scopes": ["pages_manage_posts", "pages_read_engagement", "pages_show_list"],
                "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
                "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
                "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8501/oauth/facebook"),
                "use_pkce": False
            },
            "youtube": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "revoke_url": "https://oauth2.googleapis.com/revoke",
                "scopes": ["https://www.googleapis.com/auth/youtube.upload", 
                          "https://www.googleapis.com/auth/youtube.readonly"],
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/oauth/youtube"),
                "use_pkce": True
            }
        }
    
    async def initiate_oauth_flow(
        self, 
        platform: str, 
        user_id: str,
        additional_scopes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate OAuth 2.0 authorization flow for a platform
        
        Args:
            platform: Platform identifier (twitter, linkedin, etc.)
            user_id: User identifier for state management
            additional_scopes: Additional OAuth scopes if needed
            
        Returns:
            Authorization URL and state information
        """
        
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.platform_configs[platform]
        
        # Generate secure state and PKCE parameters
        state = self._generate_secure_state()
        code_verifier = None
        code_challenge = None
        
        if config.get("use_pkce", False):
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
        
        # Store OAuth state
        oauth_state = {
            "platform": platform,
            "user_id": user_id,
            "state": state,
            "code_verifier": code_verifier,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        self.oauth_states[state] = oauth_state
        
        # Build authorization URL
        scopes = config["scopes"] + (additional_scopes or [])
        
        auth_params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": " ".join(scopes),
            "response_type": "code",
            "state": state
        }
        
        # Add PKCE parameters if required
        if code_challenge:
            auth_params["code_challenge"] = code_challenge
            auth_params["code_challenge_method"] = "S256"
        
        # Platform-specific parameters
        if platform == "linkedin":
            auth_params["response_type"] = "code"
        elif platform == "youtube":
            auth_params["access_type"] = "offline"
            auth_params["prompt"] = "consent"
        
        auth_url = f"{config['auth_url']}?{urlencode(auth_params)}"
        
        self.logger.info(f"Generated OAuth URL for {platform}: {auth_url[:100]}...")
        
        return {
            "auth_url": auth_url,
            "state": state,
            "expires_in": 600,  # 10 minutes
            "platform": platform
        }
    
    async def handle_oauth_callback(
        self,
        platform: str,
        authorization_code: str,
        state: str,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange authorization code for tokens
        
        Args:
            platform: Platform identifier
            authorization_code: Authorization code from callback
            state: State parameter for verification
            error: Error parameter if authorization failed
            
        Returns:
            Token exchange result with access/refresh tokens
        """
        
        if error:
            self.logger.error(f"OAuth authorization error for {platform}: {error}")
            return {
                "success": False,
                "error": f"Authorization failed: {error}",
                "platform": platform
            }
        
        # Verify state parameter
        if state not in self.oauth_states:
            self.logger.error(f"Invalid OAuth state: {state}")
            return {
                "success": False,
                "error": "Invalid or expired authorization request",
                "platform": platform
            }
        
        oauth_state = self.oauth_states[state]
        
        # Check if state has expired
        if datetime.now() > datetime.fromisoformat(oauth_state["expires_at"]):
            del self.oauth_states[state]
            return {
                "success": False,
                "error": "Authorization request expired",
                "platform": platform
            }
        
        try:
            # Exchange authorization code for tokens
            token_result = await self._exchange_code_for_tokens(
                platform,
                authorization_code,
                oauth_state.get("code_verifier")
            )
            
            if token_result["success"]:
                # Store encrypted tokens
                await self._store_encrypted_tokens(
                    platform,
                    oauth_state["user_id"],
                    token_result["tokens"]
                )
                
                # Clean up OAuth state
                del self.oauth_states[state]
                
                # Initialize platform client for testing
                client = await self._create_platform_client(platform, oauth_state["user_id"])
                
                # Test connection
                test_result = await self._test_platform_connection(platform, client)
                
                return {
                    "success": True,
                    "platform": platform,
                    "user_id": oauth_state["user_id"],
                    "connection_test": test_result,
                    "connected_at": datetime.now().isoformat()
                }
            else:
                return token_result
                
        except Exception as e:
            self.logger.error(f"Error handling OAuth callback for {platform}: {str(e)}")
            return {
                "success": False,
                "error": f"Token exchange failed: {str(e)}",
                "platform": platform
            }
        
        finally:
            # Clean up OAuth state
            if state in self.oauth_states:
                del self.oauth_states[state]
    
    async def _exchange_code_for_tokens(
        self,
        platform: str,
        authorization_code: str,
        code_verifier: str = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        
        config = self.platform_configs[platform]
        
        # Prepare token request data
        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": config["redirect_uri"]
        }
        
        # Add PKCE code verifier if used
        if code_verifier and config.get("use_pkce", False):
            token_data["code_verifier"] = code_verifier
            # Remove client_secret for PKCE flow
            if platform in ["twitter", "youtube"]:
                del token_data["client_secret"]
        
        # Platform-specific token request handling
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        if platform == "linkedin":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif platform == "instagram":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif platform == "twitter":
            # Twitter uses Basic Auth for client credentials
            import base64
            auth_string = f"{config['client_id']}:{config['client_secret']}"
            b64_auth = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {b64_auth}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config["token_url"],
                    data=token_data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        token_response = await response.json()
                        
                        return {
                            "success": True,
                            "tokens": {
                                "access_token": token_response.get("access_token"),
                                "refresh_token": token_response.get("refresh_token"),
                                "expires_in": token_response.get("expires_in", 3600),
                                "token_type": token_response.get("token_type", "Bearer"),
                                "scope": token_response.get("scope", ""),
                                "created_at": datetime.now().isoformat()
                            }
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Token exchange failed for {platform}: {error_text}")
                        
                        return {
                            "success": False,
                            "error": f"Token exchange failed: {response.status} - {error_text}",
                            "status_code": response.status
                        }
        
        except Exception as e:
            self.logger.error(f"Error during token exchange for {platform}: {str(e)}")
            return {
                "success": False,
                "error": f"Network error during token exchange: {str(e)}"
            }
    
    async def _store_encrypted_tokens(
        self,
        platform: str,
        user_id: str,
        tokens: Dict[str, Any]
    ) -> None:
        """Store encrypted tokens in secure storage"""
        
        # Encrypt tokens
        encrypted_tokens = self.cipher_suite.encrypt(json.dumps(tokens).encode())
        
        # Store in secure storage with expiration
        storage_key = f"oauth_tokens:{user_id}:{platform}"
        
        await self.secure_storage.store(
            key=storage_key,
            data={
                "encrypted_tokens": encrypted_tokens.decode(),
                "platform": platform,
                "user_id": user_id,
                "stored_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))).isoformat()
            },
            ttl=tokens.get("expires_in", 3600)
        )
        
        self.logger.info(f"Stored encrypted tokens for {platform}:{user_id}")
    
    async def get_valid_tokens(self, platform: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve valid tokens, refreshing if necessary"""
        
        storage_key = f"oauth_tokens:{user_id}:{platform}"
        
        try:
            stored_data = await self.secure_storage.retrieve(storage_key)
            
            if not stored_data:
                self.logger.info(f"No stored tokens found for {platform}:{user_id}")
                return None
            
            # Decrypt tokens
            encrypted_tokens = stored_data["encrypted_tokens"].encode()
            decrypted_data = self.cipher_suite.decrypt(encrypted_tokens)
            tokens = json.loads(decrypted_data.decode())
            
            # Check if tokens need refresh
            created_at = datetime.fromisoformat(tokens["created_at"])
            expires_in = tokens.get("expires_in", 3600)
            expires_at = created_at + timedelta(seconds=expires_in)
            
            # If tokens expire in less than 5 minutes, refresh them
            if datetime.now() + timedelta(minutes=5) > expires_at:
                if tokens.get("refresh_token"):
                    refreshed_tokens = await self._refresh_access_token(platform, tokens["refresh_token"])
                    
                    if refreshed_tokens["success"]:
                        # Store refreshed tokens
                        await self._store_encrypted_tokens(platform, user_id, refreshed_tokens["tokens"])
                        return refreshed_tokens["tokens"]
                    else:
                        self.logger.warning(f"Token refresh failed for {platform}:{user_id}")
                        return None
                else:
                    self.logger.warning(f"Tokens expired and no refresh token available for {platform}:{user_id}")
                    return None
            
            return tokens
            
        except Exception as e:
            self.logger.error(f"Error retrieving tokens for {platform}:{user_id}: {str(e)}")
            return None
    
    async def _refresh_access_token(self, platform: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        
        config = self.platform_configs[platform]
        
        # Not all platforms support refresh tokens
        if platform in ["instagram"]:  # Instagram doesn't support refresh tokens
            return {
                "success": False,
                "error": f"Platform {platform} doesn't support token refresh"
            }
        
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config["token_url"],
                    data=refresh_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    
                    if response.status == 200:
                        token_response = await response.json()
                        
                        refreshed_tokens = {
                            "access_token": token_response.get("access_token"),
                            "refresh_token": token_response.get("refresh_token", refresh_token),
                            "expires_in": token_response.get("expires_in", 3600),
                            "token_type": token_response.get("token_type", "Bearer"),
                            "scope": token_response.get("scope", ""),
                            "created_at": datetime.now().isoformat()
                        }
                        
                        return {
                            "success": True,
                            "tokens": refreshed_tokens
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Token refresh failed: {response.status} - {error_text}"
                        }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Network error during token refresh: {str(e)}"
            }
    
    async def revoke_platform_access(self, platform: str, user_id: str) -> Dict[str, Any]:
        """Revoke platform access and clean up stored tokens"""
        
        try:
            # Get current tokens
            tokens = await self.get_valid_tokens(platform, user_id)
            
            if tokens and tokens.get("access_token"):
                config = self.platform_configs[platform]
                
                # Revoke tokens if platform supports it
                if config.get("revoke_url"):
                    await self._revoke_tokens(platform, tokens["access_token"])
            
            # Remove stored tokens
            storage_key = f"oauth_tokens:{user_id}:{platform}"
            await self.secure_storage.delete(storage_key)
            
            self.logger.info(f"Revoked access for {platform}:{user_id}")
            
            return {
                "success": True,
                "platform": platform,
                "message": f"Successfully disconnected from {platform}"
            }
            
        except Exception as e:
            self.logger.error(f"Error revoking access for {platform}:{user_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to revoke access: {str(e)}"
            }
    
    async def _revoke_tokens(self, platform: str, access_token: str) -> None:
        """Revoke access token with platform"""
        
        config = self.platform_configs[platform]
        revoke_url = config.get("revoke_url")
        
        if not revoke_url:
            return  # Platform doesn't support token revocation
        
        try:
            revoke_data = {"token": access_token}
            
            if platform == "twitter":
                revoke_data["client_id"] = config["client_id"]
            
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
    
    def _generate_secure_state(self) -> str:
        """Generate cryptographically secure state parameter"""
        return secrets.token_urlsafe(32)
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return secrets.token_urlsafe(64)
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_challenge
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for token storage"""
        
        key_file = ".zenalto_encryption_key"
        
        try:
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                # Store key securely (in production, use proper key management)
                with open(key_file, "wb") as f:
                    f.write(key)
                
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                
                return key
        
        except Exception as e:
            self.logger.error(f"Error managing encryption key: {str(e)}")
            # Fallback to environment variable
            env_key = os.getenv("ZENALTO_ENCRYPTION_KEY")
            if env_key:
                return base64.b64decode(env_key)
            else:
                raise ValueError("Could not initialize encryption key for token storage")
```

### 2. Platform API Clients

**File**: `utils/platform_clients.py` (New)

```python
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
            reset_time = response.headers.get("x-rate-limit-reset", "unknown")
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "rate_limit_reset": reset_time,
                "retry_after": response.headers.get("retry-after", "60"),
                "timestamp": datetime.now().isoformat()
            }
        
        elif response.status in [401, 403]:  # Authentication/Authorization error
            error_text = await response.text()
            return {
                "success": False,
                "error": f"Authentication error: {error_text}",
                "requires_reauth": True,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            error_text = await response.text()
            return {
                "success": False,
                "error": f"API error {response.status}: {error_text}",
                "status_code": response.status,
                "timestamp": datetime.now().isoformat()
            }

class TwitterClient(BasePlatformClient):
    """Twitter/X API v2.0 client"""
    
    def _get_api_base_url(self) -> str:
        return "https://api.twitter.com/2"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        return {
            "tweets": {"limit": 300, "window": 900},  # 300 per 15 minutes
            "users": {"limit": 75, "window": 900},    # 75 per 15 minutes
            "media_upload": {"limit": 300, "window": 900}
        }
    
    async def post_tweet(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post a tweet"""
        
        tweet_data = {
            "text": content["text"]
        }
        
        # Add media if provided
        if content.get("media_urls"):
            # First, upload media
            media_ids = []
            for media_url in content["media_urls"]:
                media_result = await self._upload_media(media_url)
                if media_result["success"]:
                    media_ids.append(media_result["media_id"])
            
            if media_ids:
                tweet_data["media"] = {"media_ids": media_ids}
        
        result = await self._make_api_request("POST", "/tweets", data=tweet_data)
        
        if result["success"]:
            tweet_id = result["data"]["data"]["id"]
            result["post_url"] = f"https://twitter.com/i/status/{tweet_id}"
            result["post_id"] = tweet_id
        
        return result
    
    async def get_tweet_analytics(self, tweet_id: str) -> Dict[str, Any]:
        """Get analytics for a specific tweet"""
        
        params = {
            "tweet.fields": "public_metrics,created_at,author_id"
        }
        
        result = await self._make_api_request("GET", f"/tweets/{tweet_id}", params=params)
        
        if result["success"]:
            tweet_data = result["data"]["data"]
            metrics = tweet_data.get("public_metrics", {})
            
            result["analytics"] = {
                "impressions": metrics.get("impression_count", 0),
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "created_at": tweet_data.get("created_at")
            }
        
        return result

class LinkedInClient(BasePlatformClient):
    """LinkedIn API v2.0 client"""
    
    def _get_api_base_url(self) -> str:
        return "https://api.linkedin.com/v2"
    
    def _get_rate_limits(self) -> Dict[str, Any]:
        return {
            "posts": {"limit": 100, "window": 86400},  # 100 per day
            "profile": {"limit": 500, "window": 86400}  # 500 per day
        }
    
    async def post_to_linkedin(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to LinkedIn"""
        
        # First, get user profile information
        profile_result = await self._make_api_request("GET", "/people/~")
        
        if not profile_result["success"]:
            return profile_result
        
        author_urn = profile_result["data"]["id"]
        
        # Prepare post data
        post_data = {
            "author": f"urn:li:person:{author_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content["text"]
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add media if provided
        if content.get("media_urls"):
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            
            # Upload and register media
            media_urns = []
            for media_url in content["media_urls"]:
                media_result = await self._register_linkedin_media(media_url, author_urn)
                if media_result["success"]:
                    media_urns.append(media_result["media_urn"])
            
            if media_urns:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "media": urn
                    } for urn in media_urns
                ]
        
        result = await self._make_api_request("POST", "/ugcPosts", data=post_data)
        
        if result["success"]:
            post_id = result["data"]["id"]
            result["post_url"] = f"https://www.linkedin.com/feed/update/{post_id}/"
            result["post_id"] = post_id
        
        return result
```

## Testing Requirements

### 1. OAuth Flow Testing
```python
@pytest.mark.asyncio
async def test_oauth_flow():
    oauth_manager = OAuthManager()
    
    # Test OAuth initiation
    auth_result = await oauth_manager.initiate_oauth_flow("twitter", "test_user")
    assert auth_result["auth_url"].startswith("https://twitter.com")
    assert "state" in auth_result
    
    # Test callback handling (mock)
    callback_result = await oauth_manager.handle_oauth_callback(
        "twitter", "mock_code", auth_result["state"]
    )
    # Would test actual callback in integration tests

@pytest.mark.asyncio
async def test_token_management():
    oauth_manager = OAuthManager()
    
    # Test token storage and retrieval
    mock_tokens = {
        "access_token": "test_token",
        "refresh_token": "test_refresh",
        "expires_in": 3600
    }
    
    await oauth_manager._store_encrypted_tokens("twitter", "test_user", mock_tokens)
    
    retrieved_tokens = await oauth_manager.get_valid_tokens("twitter", "test_user")
    assert retrieved_tokens["access_token"] == "test_token"

@pytest.mark.asyncio
async def test_platform_clients():
    twitter_client = TwitterClient(OAuthManager(), "test_user")
    
    # Mock API response
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": {"id": "12345"}})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await twitter_client.post_tweet({"text": "Test tweet"})
        assert result["success"] == True
        assert "post_id" in result
```

### 2. Security Testing
```python
def test_token_encryption():
    oauth_manager = OAuthManager()
    
    # Test encryption/decryption
    test_data = {"access_token": "sensitive_token"}
    encrypted = oauth_manager.cipher_suite.encrypt(json.dumps(test_data).encode())
    decrypted = json.loads(oauth_manager.cipher_suite.decrypt(encrypted).decode())
    
    assert decrypted["access_token"] == "sensitive_token"

def test_state_parameter_security():
    oauth_manager = OAuthManager()
    
    # Test state generation uniqueness
    states = [oauth_manager._generate_secure_state() for _ in range(100)]
    assert len(set(states)) == 100  # All unique

def test_pkce_implementation():
    oauth_manager = OAuthManager()
    
    code_verifier = oauth_manager._generate_code_verifier()
    code_challenge = oauth_manager._generate_code_challenge(code_verifier)
    
    # Verify PKCE challenge is correct
    import hashlib, base64
    expected_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    
    assert code_challenge == expected_challenge
```

## Success Criteria
- [ ] All OAuth 2.0 flows implemented securely with PKCE where supported
- [ ] Tokens encrypted and stored securely with proper expiration handling
- [ ] Automatic token refresh implemented for supported platforms
- [ ] Rate limiting prevents API quota violations
- [ ] All platform clients follow unified interface patterns
- [ ] Comprehensive error handling and recovery mechanisms
- [ ] Security audit passes with no critical vulnerabilities
- [ ] Integration tests pass with all major platforms

## Dependencies
- Secure storage system for encrypted tokens
- Rate limiting infrastructure
- Error handling and logging framework
- UI integration for OAuth callback handling

## Timeline
- **Week 1**: OAuth manager and base security infrastructure
- **Week 2**: Platform-specific API clients implementation
- **Week 3**: Token management and refresh mechanisms
- **Week 4**: Security testing and hardening

## Security Checklist
- [ ] PKCE implemented for supported platforms
- [ ] State parameters validated against CSRF
- [ ] Tokens encrypted at rest
- [ ] Secure token transmission
- [ ] Rate limiting implemented
- [ ] Token refresh handling
- [ ] Secure credential storage
- [ ] OAuth callback validation
- [ ] Error messages don't leak sensitive information
- [ ] Audit logging for authentication events