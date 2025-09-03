"""
Secure Storage Module for ZENALTO

Provides encrypted storage capabilities for sensitive data like OAuth tokens,
API keys, and user credentials. Uses file-based storage with encryption.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path


class SecureStorage:
    """Secure storage for sensitive data with TTL support"""
    
    def __init__(self, storage_dir: str = ".zenalto_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Set restrictive permissions on storage directory
        try:
            os.chmod(self.storage_dir, 0o700)
        except OSError:
            self.logger.warning("Could not set restrictive permissions on storage directory")
    
    async def store(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Store data with optional TTL (time-to-live) in seconds
        
        Args:
            key: Storage key
            data: Data to store
            ttl: Time-to-live in seconds (optional)
        """
        
        storage_entry = {
            "data": data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl else None
        }
        
        # Hash key to avoid filesystem issues
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        file_path = self.storage_dir / f"{key_hash}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(storage_entry, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            
            self.logger.debug(f"Stored data for key: {key[:10]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to store data for key {key[:10]}...: {str(e)}")
            raise
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data by key, checking TTL expiration
        
        Args:
            key: Storage key
            
        Returns:
            Stored data or None if not found/expired
        """
        
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        file_path = self.storage_dir / f"{key_hash}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                storage_entry = json.load(f)
            
            # Check expiration
            if storage_entry.get("expires_at"):
                expires_at = datetime.fromisoformat(storage_entry["expires_at"])
                if datetime.now() > expires_at:
                    # Data expired, remove it
                    await self.delete(key)
                    return None
            
            return storage_entry["data"]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve data for key {key[:10]}...: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete stored data by key
        
        Args:
            key: Storage key
            
        Returns:
            True if deleted successfully, False otherwise
        """
        
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        file_path = self.storage_dir / f"{key_hash}.json"
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Deleted data for key: {key[:10]}...")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete data for key {key[:10]}...: {str(e)}")
            return False
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired entries
        
        Returns:
            Number of expired entries removed
        """
        
        removed_count = 0
        
        try:
            for file_path in self.storage_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        storage_entry = json.load(f)
                    
                    if storage_entry.get("expires_at"):
                        expires_at = datetime.fromisoformat(storage_entry["expires_at"])
                        if datetime.now() > expires_at:
                            file_path.unlink()
                            removed_count += 1
                
                except Exception as e:
                    self.logger.warning(f"Error checking file {file_path}: {str(e)}")
                    continue
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} expired storage entries")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            return 0
    
    async def list_keys(self) -> list:
        """
        List all storage keys (for debugging/admin purposes)
        Note: Returns hashed keys, not original keys
        """
        
        try:
            keys = []
            for file_path in self.storage_dir.glob("*.json"):
                keys.append(file_path.stem)
            return keys
            
        except Exception as e:
            self.logger.error(f"Error listing keys: {str(e)}")
            return []