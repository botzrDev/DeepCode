"""
Rate Limiter for Social Media API Integration

Implements per-platform rate limiting to ensure compliance with API limits
while maintaining optimal throughput.
"""

import asyncio
import time
import logging
from typing import Dict, Any


class RateLimiter:
    """Rate limiter for social media platform APIs"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.logger = logging.getLogger(f"{__name__}.{platform}")
        
        # Platform-specific rate limit configurations
        self.rate_limits = self._get_platform_rate_limits()
        
        # Request tracking
        self.request_history = []
        self.last_request_time = 0
        
        # Rate limit state
        self.requests_made = 0
        self.window_start = time.time()
    
    def _get_platform_rate_limits(self) -> Dict[str, Any]:
        """Get rate limit configurations for the platform"""
        
        # Define rate limits based on platform documentation
        limits = {
            "twitter": {
                "requests_per_window": 300,  # 300 requests per 15 minutes
                "window_seconds": 900,       # 15 minutes
                "min_interval": 0.1          # Minimum 100ms between requests
            },
            "linkedin": {
                "requests_per_window": 100,  # Conservative limit
                "window_seconds": 3600,      # 1 hour
                "min_interval": 1.0          # 1 second between requests
            },
            "instagram": {
                "requests_per_window": 200,  # Instagram Basic Display
                "window_seconds": 3600,      # 1 hour
                "min_interval": 1.0          # 1 second between requests
            },
            "facebook": {
                "requests_per_window": 200,  # Graph API standard
                "window_seconds": 3600,      # 1 hour
                "min_interval": 0.5          # 500ms between requests
            },
            "youtube": {
                "requests_per_window": 10000, # YouTube Data API v3
                "window_seconds": 86400,      # 24 hours (daily quota)
                "min_interval": 0.1           # 100ms between requests
            }
        }
        
        return limits.get(self.platform, {
            "requests_per_window": 100,
            "window_seconds": 3600,
            "min_interval": 1.0
        })
    
    async def wait_if_needed(self) -> None:
        """Wait if rate limit requires delay before next request"""
        
        current_time = time.time()
        
        # Check if we need to reset the window
        if current_time - self.window_start >= self.rate_limits["window_seconds"]:
            self.window_start = current_time
            self.requests_made = 0
            self.request_history.clear()
        
        # Check if we've hit the rate limit
        if self.requests_made >= self.rate_limits["requests_per_window"]:
            # Calculate time until window reset
            reset_time = self.window_start + self.rate_limits["window_seconds"]
            wait_time = reset_time - current_time
            
            if wait_time > 0:
                self.logger.warning(
                    f"Rate limit reached for {self.platform}. "
                    f"Waiting {wait_time:.1f} seconds until reset."
                )
                await asyncio.sleep(wait_time)
                
                # Reset counters
                self.window_start = time.time()
                self.requests_made = 0
                self.request_history.clear()
        
        # Enforce minimum interval between requests
        time_since_last = current_time - self.last_request_time
        min_interval = self.rate_limits["min_interval"]
        
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            await asyncio.sleep(wait_time)
    
    def record_request(self, success: bool = True) -> None:
        """Record a request for rate limiting purposes"""
        
        current_time = time.time()
        self.last_request_time = current_time
        self.requests_made += 1
        
        # Keep request history for analysis
        self.request_history.append({
            "timestamp": current_time,
            "success": success
        })
        
        # Limit history size
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-500:]
        
        self.logger.debug(
            f"Recorded request for {self.platform}: "
            f"{self.requests_made}/{self.rate_limits['requests_per_window']} "
            f"in current window"
        )
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        
        current_time = time.time()
        window_remaining = self.rate_limits["window_seconds"] - (current_time - self.window_start)
        requests_remaining = self.rate_limits["requests_per_window"] - self.requests_made
        
        # Calculate success rate from recent history
        if self.request_history:
            recent_requests = [
                req for req in self.request_history
                if current_time - req["timestamp"] <= 3600  # Last hour
            ]
            success_rate = sum(1 for req in recent_requests if req["success"]) / len(recent_requests) if recent_requests else 1.0
        else:
            success_rate = 1.0
        
        return {
            "platform": self.platform,
            "requests_made": self.requests_made,
            "requests_remaining": max(0, requests_remaining),
            "window_reset_in": max(0, window_remaining),
            "success_rate": success_rate,
            "last_request_time": self.last_request_time,
            "min_interval": self.rate_limits["min_interval"]
        }
    
    def is_rate_limited(self) -> bool:
        """Check if currently rate limited"""
        
        current_time = time.time()
        
        # Check window reset
        if current_time - self.window_start >= self.rate_limits["window_seconds"]:
            return False
        
        # Check if limit reached
        return self.requests_made >= self.rate_limits["requests_per_window"]


class GlobalRateLimiter:
    """Global rate limiter managing all platform rate limiters"""
    
    def __init__(self):
        self.platform_limiters: Dict[str, RateLimiter] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_limiter(self, platform: str) -> RateLimiter:
        """Get or create rate limiter for platform"""
        
        if platform not in self.platform_limiters:
            self.platform_limiters[platform] = RateLimiter(platform)
            self.logger.info(f"Created rate limiter for {platform}")
        
        return self.platform_limiters[platform]
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get rate limit status for all platforms"""
        
        return {
            platform: limiter.get_rate_limit_status()
            for platform, limiter in self.platform_limiters.items()
        }
    
    async def wait_for_all_platforms(self, platforms: list) -> None:
        """Wait for rate limits on multiple platforms"""
        
        tasks = []
        for platform in platforms:
            limiter = self.get_limiter(platform)
            tasks.append(limiter.wait_if_needed())
        
        await asyncio.gather(*tasks)