"""
Factory for creating social media API clients.

Provides a centralized way to instantiate different social media platform clients
with consistent configuration and error handling.
"""

from typing import Dict, Any, Optional, Union
import logging

from .base_client import BaseSocialClient
from .twitter_client import TwitterClient
from .linkedin_client import LinkedInClient
from .instagram_client import InstagramClient
from .facebook_client import FacebookClient
from .youtube_client import YouTubeClient


class SocialMediaClientFactory:
    """
    Factory for creating social media API clients.
    
    Provides a centralized way to create and configure different platform clients
    while handling missing dependencies gracefully.
    """
    
    CLIENTS = {
        "twitter": TwitterClient,
        "linkedin": LinkedInClient,
        "instagram": InstagramClient,
        "facebook": FacebookClient,
        "youtube": YouTubeClient
    }
    
    SUPPORTED_PLATFORMS = list(CLIENTS.keys())
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @classmethod
    def create_client(
        cls,
        platform: str,
        config: Dict[str, Any]
    ) -> Optional[BaseSocialClient]:
        """
        Create a social media client for the specified platform.
        
        Args:
            platform: Platform name (twitter, linkedin, instagram, facebook, youtube)
            config: Configuration dictionary with API credentials and settings
            
        Returns:
            BaseSocialClient instance or None if creation failed
            
        Raises:
            ValueError: If platform is not supported
            ImportError: If required dependencies are missing
        """
        if platform not in cls.CLIENTS:
            raise ValueError(f"Unsupported platform: {platform}. Supported platforms: {cls.SUPPORTED_PLATFORMS}")
        
        try:
            client_class = cls.CLIENTS[platform]
            return client_class(config)
            
        except ImportError as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Missing dependencies for {platform}: {e}")
            raise ImportError(f"Required dependencies not installed for {platform}: {e}")
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create {platform} client: {e}")
            raise
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platform names."""
        return cls.SUPPORTED_PLATFORMS.copy()
    
    @classmethod
    def is_platform_supported(cls, platform: str) -> bool:
        """Check if a platform is supported."""
        return platform in cls.SUPPORTED_PLATFORMS
    
    @classmethod
    def get_required_config_keys(cls, platform: str) -> Dict[str, list]:
        """
        Get required configuration keys for each platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict with 'required' and 'optional' keys listing configuration parameters
        """
        config_requirements = {
            "twitter": {
                "required": ["api_key", "api_secret", "access_token", "access_token_secret"],
                "optional": ["bearer_token"]
            },
            "linkedin": {
                "required": ["access_token"],
                "optional": ["organization_id"]
            },
            "instagram": {
                "required": ["username", "password"],
                "optional": ["access_token"]
            },
            "facebook": {
                "required": ["access_token"],
                "optional": ["page_id"]
            },
            "youtube": {
                "required": ["access_token", "refresh_token", "client_id", "client_secret"],
                "optional": []
            }
        }
        
        if platform not in config_requirements:
            raise ValueError(f"Unknown platform: {platform}")
            
        return config_requirements[platform]
    
    @classmethod
    def validate_config(cls, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration for a platform.
        
        Args:
            platform: Platform name
            config: Configuration dictionary
            
        Returns:
            Dict with validation results:
            {
                "valid": bool,
                "missing_keys": list,
                "errors": list
            }
        """
        try:
            requirements = cls.get_required_config_keys(platform)
            required_keys = requirements["required"]
            
            missing_keys = []
            errors = []
            
            # Check required keys
            for key in required_keys:
                if key not in config or not config[key]:
                    missing_keys.append(key)
            
            # Additional validation rules
            if platform == "twitter":
                if config.get("api_key") and len(config["api_key"]) < 10:
                    errors.append("Twitter API key appears to be too short")
                    
            elif platform == "instagram":
                if not config.get("username") and not config.get("access_token"):
                    errors.append("Instagram requires either username/password or access_token")
                    
            elif platform == "youtube":
                if config.get("access_token") and not config.get("refresh_token"):
                    errors.append("YouTube requires refresh_token for token renewal")
            
            return {
                "valid": len(missing_keys) == 0 and len(errors) == 0,
                "missing_keys": missing_keys,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "missing_keys": [],
                "errors": [f"Validation error: {str(e)}"]
            }
    
    @classmethod
    def create_multiple_clients(
        cls,
        configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Union[BaseSocialClient, Exception]]:
        """
        Create multiple clients from a configuration dictionary.
        
        Args:
            configs: Dict mapping platform names to their configurations
            
        Returns:
            Dict mapping platform names to either client instances or exceptions
        """
        clients = {}
        logger = logging.getLogger(__name__)
        
        for platform, config in configs.items():
            try:
                if cls.is_platform_supported(platform):
                    clients[platform] = cls.create_client(platform, config)
                else:
                    clients[platform] = ValueError(f"Unsupported platform: {platform}")
                    
            except Exception as e:
                logger.error(f"Failed to create {platform} client: {e}")
                clients[platform] = e
        
        return clients


# Convenience functions
def create_twitter_client(config: Dict[str, Any]) -> TwitterClient:
    """Create a Twitter client."""
    return SocialMediaClientFactory.create_client("twitter", config)

def create_linkedin_client(config: Dict[str, Any]) -> LinkedInClient:
    """Create a LinkedIn client.""" 
    return SocialMediaClientFactory.create_client("linkedin", config)

def create_instagram_client(config: Dict[str, Any]) -> InstagramClient:
    """Create an Instagram client."""
    return SocialMediaClientFactory.create_client("instagram", config)

def create_facebook_client(config: Dict[str, Any]) -> FacebookClient:
    """Create a Facebook client."""
    return SocialMediaClientFactory.create_client("facebook", config)

def create_youtube_client(config: Dict[str, Any]) -> YouTubeClient:
    """Create a YouTube client."""
    return SocialMediaClientFactory.create_client("youtube", config)