"""
OAuth 2.0 Manager for Social Media Platform Authentication

Handles secure OAuth flows, token management, and API client initialization
for all supported social media platforms.
"""

import os
import json
import logging
import secrets
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import aiohttp
from cryptography.fernet import Fernet
from utils.secure_storage import SecureStorage

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
    
    async def _create_platform_client(self, platform: str, user_id: str):
        """Create platform-specific API client (placeholder)"""
        # This will be implemented when we create the platform clients
        return {"platform": platform, "user_id": user_id, "mock": True}
    
    async def _test_platform_connection(self, platform: str, client) -> Dict[str, Any]:
        """Test platform connection (placeholder)"""
        # This will be implemented with real API calls
        return {
            "success": True,
            "platform": platform,
            "test": "mock_test_passed",
            "timestamp": datetime.now().isoformat()
        }
    
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