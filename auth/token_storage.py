import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import logging


class TokenStorage:
    """
    Secure token storage with encryption.
    
    Features:
    - Encrypted token storage
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
        
        # Use existing secure storage from utils
        try:
            from utils.secure_storage import SecureStorage
            self._storage = SecureStorage()
        except ImportError:
            self.logger.warning("Secure storage not available, using in-memory storage")
            self._storage = {}
    
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
            
            # Store using secure storage
            key = f"auth_tokens:{user_id}:{platform}"
            
            if hasattr(self._storage, 'store'):
                # Using utils.secure_storage
                await self._storage.store(
                    key,
                    {"encrypted_tokens": encrypted_data},
                    tokens.get("expires_in", 3600)
                )
            else:
                # Using in-memory fallback
                self._storage[key] = {
                    "encrypted_tokens": encrypted_data,
                    "stored_at": datetime.now(),
                    "expires_at": datetime.now() + timedelta(seconds=tokens.get("expires_in", 3600))
                }
            
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
            key = f"auth_tokens:{user_id}:{platform}"
            
            # Retrieve from storage
            data = None
            if hasattr(self._storage, 'retrieve'):
                # Using utils.secure_storage
                data = await self._storage.retrieve(key)
            else:
                # Using in-memory fallback
                stored_item = self._storage.get(key)
                if stored_item and datetime.now() < stored_item["expires_at"]:
                    data = stored_item
                elif stored_item:
                    # Expired, remove it
                    del self._storage[key]
            
            if not data or "encrypted_tokens" not in data:
                return None
            
            # Decrypt and return
            token_data = self._decrypt_data(data["encrypted_tokens"])
            
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
            key = f"auth_tokens:{user_id}:{platform}"
            
            # Delete from storage
            if hasattr(self._storage, 'delete'):
                # Using utils.secure_storage
                await self._storage.delete(key)
            else:
                # Using in-memory fallback
                if key in self._storage:
                    del self._storage[key]
            
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