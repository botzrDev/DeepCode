# Development Assignment #10: OAuth Authentication Implementation

## Priority: 🟡 MEDIUM - Week 4

## Objective
Implement secure OAuth 2.0 authentication flows for all social media platforms, enabling users to connect their accounts safely without storing passwords.

## Background
OAuth authentication is critical for secure platform connections. Each platform has specific OAuth requirements and flows that must be implemented correctly.

## Deliverables

### 1. OAuth Manager
**File**: `auth/oauth_manager.py`

```python
import asyncio
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import jwt
import aiohttp
from urllib.parse import urlencode, parse_qs
import logging

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
```

### 2. Token Storage
**File**: `auth/token_storage.py`

```python
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import aioredis
import logging

class TokenStorage:
    """
    Secure token storage with encryption.
    
    Features:
    - Encrypted token storage
    - Redis caching for performance
    - Automatic expiration handling
    - Token refresh tracking
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize token storage.
        
        Args:
            encryption_key: Fernet encryption key
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate new key (should be stored securely)
            self.cipher = Fernet(Fernet.generate_key())
        
        self.redis = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection for caching."""
        try:
            self.redis = aioredis.from_url(
                "redis://localhost",
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}")
    
    async def store_tokens(
        self,
        user_id: str,
        platform: str,
        tokens: Dict[str, Any],
        user_info: Optional[Dict] = None
    ) -> bool:
        """
        Store tokens securely.
        
        Args:
            user_id: User identifier
            platform: Social media platform
            tokens: Token data (access_token, refresh_token, etc.)
            user_info: Optional user information
        
        Returns:
            Success status
        """
        try:
            # Prepare token data
            token_data = {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_at": (
                    datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
                ).isoformat(),
                "token_type": tokens.get("token_type", "Bearer"),
                "scope": tokens.get("scope"),
                "user_info": user_info,
                "stored_at": datetime.now().isoformat()
            }
            
            # Encrypt sensitive data
            encrypted_data = self._encrypt_data(token_data)
            
            # Store in database (implement your database storage)
            key = f"tokens:{user_id}:{platform}"
            
            # Cache in Redis if available
            if self.redis:
                await self.redis.setex(
                    key,
                    tokens.get("expires_in", 3600),
                    encrypted_data
                )
            
            # Also store in persistent database
            await self._store_in_database(user_id, platform, encrypted_data)
            
            self.logger.info(f"Tokens stored for user {user_id} on {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store tokens: {e}")
            return False
    
    async def get_tokens(
        self,
        user_id: str,
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored tokens.
        
        Returns:
            Decrypted token data or None
        """
        try:
            key = f"tokens:{user_id}:{platform}"
            
            # Try Redis cache first
            encrypted_data = None
            if self.redis:
                encrypted_data = await self.redis.get(key)
            
            # Fall back to database
            if not encrypted_data:
                encrypted_data = await self._get_from_database(user_id, platform)
                
                # Re-cache if found
                if encrypted_data and self.redis:
                    await self.redis.setex(key, 3600, encrypted_data)
            
            if not encrypted_data:
                return None
            
            # Decrypt and return
            token_data = self._decrypt_data(encrypted_data)
            
            # Check expiration
            expires_at = datetime.fromisoformat(token_data.get("expires_at"))
            if datetime.now() > expires_at:
                self.logger.info(f"Token expired for user {user_id} on {platform}")
                # Token expired, might need refresh
                token_data["expired"] = True
            
            return token_data
            
        except Exception as e:
            self.logger.error(f"Failed to get tokens: {e}")
            return None
    
    async def update_tokens(
        self,
        user_id: str,
        platform: str,
        tokens: Dict[str, Any]
    ) -> bool:
        """
        Update existing tokens (e.g., after refresh).
        
        Returns:
            Success status
        """
        try:
            # Get existing data
            existing_data = await self.get_tokens(user_id, platform)
            
            if existing_data:
                # Preserve user info and merge with new tokens
                user_info = existing_data.get("user_info")
                return await self.store_tokens(user_id, platform, tokens, user_info)
            else:
                # No existing data, just store new
                return await self.store_tokens(user_id, platform, tokens)
                
        except Exception as e:
            self.logger.error(f"Failed to update tokens: {e}")
            return False
    
    async def delete_tokens(
        self,
        user_id: str,
        platform: str
    ) -> bool:
        """
        Delete stored tokens.
        
        Returns:
            Success status
        """
        try:
            key = f"tokens:{user_id}:{platform}"
            
            # Delete from Redis
            if self.redis:
                await self.redis.delete(key)
            
            # Delete from database
            await self._delete_from_database(user_id, platform)
            
            self.logger.info(f"Tokens deleted for user {user_id} on {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete tokens: {e}")
            return False
    
    def _encrypt_data(self, data: Dict) -> str:
        """Encrypt token data."""
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted.decode()
    
    def _decrypt_data(self, encrypted_data: str) -> Dict:
        """Decrypt token data."""
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
    
    # Database methods (implement based on your database)
    
    async def _store_in_database(
        self,
        user_id: str,
        platform: str,
        encrypted_data: str
    ):
        """Store encrypted tokens in database."""
        # Implement based on your database (PostgreSQL, MongoDB, etc.)
        pass
    
    async def _get_from_database(
        self,
        user_id: str,
        platform: str
    ) -> Optional[str]:
        """Get encrypted tokens from database."""
        # Implement based on your database
        pass
    
    async def _delete_from_database(
        self,
        user_id: str,
        platform: str
    ):
        """Delete tokens from database."""
        # Implement based on your database
        pass
```

### 3. Streamlit OAuth Integration
**File**: `ui/components/oauth_handler.py`

```python
import streamlit as st
from typing import Dict, Any, Optional
import asyncio
from auth.oauth_manager import OAuthManager

class StreamlitOAuthHandler:
    """
    OAuth handler for Streamlit UI.
    """
    
    def __init__(self):
        self.oauth_manager = OAuthManager(st.secrets.get("oauth", {}))
    
    def render_connection_flow(self, platform: str):
        """Render OAuth connection flow in Streamlit."""
        
        # Check if we're handling a callback
        query_params = st.experimental_get_query_params()
        
        if "code" in query_params and "state" in query_params:
            # Handle OAuth callback
            self._handle_callback(platform, query_params)
        else:
            # Initiate OAuth flow
            self._initiate_flow(platform)
    
    def _initiate_flow(self, platform: str):
        """Initiate OAuth authentication flow."""
        
        st.info(f"Connect your {platform.title()} account")
        
        if st.button(f"Connect {platform.title()}", key=f"oauth_init_{platform}"):
            # Get redirect URI
            redirect_uri = self._get_redirect_uri()
            
            # Initiate OAuth flow
            result = asyncio.run(
                self.oauth_manager.initiate_oauth_flow(
                    platform=platform,
                    user_id=st.session_state.get("user_id", "default"),
                    redirect_uri=redirect_uri
                )
            )
            
            if result.get("auth_url"):
                # Store state in session
                st.session_state[f"oauth_state_{platform}"] = result["state"]
                
                # Redirect to OAuth provider
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={result["auth_url"]}">',
                    unsafe_allow_html=True
                )
            else:
                st.error("Failed to initiate authentication")
    
    def _handle_callback(self, platform: str, params: Dict):
        """Handle OAuth callback."""
        
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]
        
        # Validate state
        stored_state = st.session_state.get(f"oauth_state_{platform}")
        
        if state != stored_state:
            st.error("Invalid authentication state")
            return
        
        # Exchange code for tokens
        result = asyncio.run(
            self.oauth_manager.handle_oauth_callback(
                platform=platform,
                code=code,
                state=state,
                error=error
            )
        )
        
        if result.get("success"):
            st.success(f"Successfully connected to {platform.title()}!")
            
            # Store connection status
            if "connected_platforms" not in st.session_state:
                st.session_state.connected_platforms = {}
            
            st.session_state.connected_platforms[platform] = {
                "connected": True,
                "user_info": result.get("user_info", {}),
                "connected_at": datetime.now()
            }
            
            # Clear OAuth state
            del st.session_state[f"oauth_state_{platform}"]
            
            # Clear query params
            st.experimental_set_query_params()
            
            # Rerun to update UI
            st.rerun()
        else:
            st.error(f"Failed to connect: {result.get('error')}")
    
    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI."""
        # Get current URL
        # In production, this should be your configured redirect URI
        return "http://localhost:8501/callback"
```

## Security Requirements

### 1. PKCE Implementation
- Mandatory for public clients
- Use S256 challenge method when supported
- Fallback to plain for platforms that don't support S256

### 2. State Validation
- Generate cryptographically secure state parameters
- Validate state on callback
- Expire states after 10 minutes

### 3. Token Security
- Encrypt tokens at rest
- Use secure key management
- Implement token rotation
- Clear tokens on logout

### 4. HTTPS Requirements
- All OAuth flows must use HTTPS in production
- Redirect URIs must be HTTPS (except localhost for development)

## Testing

### 1. Unit Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_oauth_flow_initiation():
    """Test OAuth flow initiation."""
    manager = OAuthManager(test_config)
    
    result = await manager.initiate_oauth_flow(
        platform="twitter",
        user_id="test_user",
        redirect_uri="http://localhost/callback"
    )
    
    assert "auth_url" in result
    assert "state" in result
    assert result["state"] in manager.pending_authentications

@pytest.mark.asyncio
async def test_state_validation():
    """Test state parameter validation."""
    manager = OAuthManager(test_config)
    
    # Invalid state should fail
    result = await manager.handle_oauth_callback(
        platform="twitter",
        code="test_code",
        state="invalid_state"
    )
    
    assert result["success"] == False
    assert "Invalid state" in result["error"]

@pytest.mark.asyncio
async def test_token_encryption():
    """Test token encryption and decryption."""
    storage = TokenStorage()
    
    test_data = {"access_token": "secret_token"}
    encrypted = storage._encrypt_data(test_data)
    decrypted = storage._decrypt_data(encrypted)
    
    assert decrypted == test_data
    assert encrypted != str(test_data)
```

## Success Criteria

- [ ] OAuth flows working for all platforms
- [ ] PKCE implemented where supported
- [ ] Token storage encrypted
- [ ] Token refresh working
- [ ] State validation implemented
- [ ] Streamlit integration functional
- [ ] Security best practices followed
- [ ] All tests passing

## Delivery Checklist

- [ ] OAuth manager implementation
- [ ] Token storage with encryption
- [ ] Streamlit OAuth handler
- [ ] Platform-specific configurations
- [ ] Security documentation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error handling comprehensive