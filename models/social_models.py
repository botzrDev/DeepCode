"""
Data models for social media platform integration

Defines data structures for platform connections, posts, analytics, and media assets.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PlatformType(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"


class ConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    EXPIRED = "expired"


class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


@dataclass
class PlatformConnection:
    """Represents a connection to a social media platform"""
    
    platform: PlatformType
    user_id: str
    platform_user_id: Optional[str] = None
    platform_username: Optional[str] = None
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    connected_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """Check if connection is active and valid"""
        return (
            self.status == ConnectionStatus.CONNECTED and
            (self.token_expires_at is None or self.token_expires_at > datetime.now())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "platform": self.platform.value,
            "user_id": self.user_id,
            "platform_user_id": self.platform_user_id,
            "platform_username": self.platform_username,
            "status": self.status.value,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "scopes": self.scopes,
            "metadata": self.metadata
        }


@dataclass
class MediaAsset:
    """Represents a media asset (image, video, etc.)"""
    
    asset_id: str
    media_type: MediaType
    file_path: Optional[str] = None
    url: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None  # For video/audio in seconds
    alt_text: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "asset_id": self.asset_id,
            "media_type": self.media_type.value,
            "file_path": self.file_path,
            "url": self.url,
            "filename": self.filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "alt_text": self.alt_text,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class SocialPost:
    """Represents a social media post"""
    
    post_id: str
    user_id: str
    platform: PlatformType
    content: str
    status: PostStatus = PostStatus.DRAFT
    platform_post_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    published_at: Optional[datetime] = None
    media_assets: List[MediaAsset] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_media(self, media_asset: MediaAsset) -> None:
        """Add a media asset to the post"""
        self.media_assets.append(media_asset)
        self.updated_at = datetime.now()
    
    def is_published(self) -> bool:
        """Check if post is published"""
        return self.status == PostStatus.PUBLISHED and self.platform_post_id is not None
    
    def is_scheduled(self) -> bool:
        """Check if post is scheduled"""
        return (
            self.status == PostStatus.SCHEDULED and 
            self.scheduled_time is not None and
            self.scheduled_time > datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "platform": self.platform.value,
            "content": self.content,
            "status": self.status.value,
            "platform_post_id": self.platform_post_id,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "media_assets": [asset.to_dict() for asset in self.media_assets],
            "hashtags": self.hashtags,
            "mentions": self.mentions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class PostAnalytics:
    """Represents analytics data for a social media post"""
    
    post_id: str
    platform_post_id: str
    platform: PlatformType
    
    # Engagement metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    clicks: int = 0
    saves: int = 0
    
    # Reach metrics
    impressions: int = 0
    reach: int = 0
    
    # Calculated metrics
    engagement_rate: Optional[float] = None
    click_through_rate: Optional[float] = None
    
    # Time-based data
    collected_at: datetime = field(default_factory=datetime.now)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    
    # Platform-specific data
    platform_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate as a percentage"""
        if self.impressions == 0:
            return 0.0
        
        total_engagements = self.likes + self.shares + self.comments + self.saves
        self.engagement_rate = (total_engagements / self.impressions) * 100
        return self.engagement_rate
    
    def calculate_ctr(self) -> float:
        """Calculate click-through rate as a percentage"""
        if self.impressions == 0:
            return 0.0
        
        self.click_through_rate = (self.clicks / self.impressions) * 100
        return self.click_through_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "post_id": self.post_id,
            "platform_post_id": self.platform_post_id,
            "platform": self.platform.value,
            "views": self.views,
            "likes": self.likes,
            "shares": self.shares,
            "comments": self.comments,
            "clicks": self.clicks,
            "saves": self.saves,
            "impressions": self.impressions,
            "reach": self.reach,
            "engagement_rate": self.engagement_rate,
            "click_through_rate": self.click_through_rate,
            "collected_at": self.collected_at.isoformat(),
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "platform_metrics": self.platform_metrics
        }


@dataclass 
class AccountAnalytics:
    """Represents analytics data for a social media account"""
    
    user_id: str
    platform: PlatformType
    period_start: datetime
    period_end: datetime
    
    # Follower metrics
    followers_count: int = 0
    following_count: int = 0
    followers_growth: int = 0
    
    # Content metrics  
    posts_count: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    total_comments: int = 0
    
    # Engagement metrics
    average_engagement_rate: Optional[float] = None
    top_performing_post_id: Optional[str] = None
    
    # Time period
    collected_at: datetime = field(default_factory=datetime.now)
    
    # Platform-specific data
    platform_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "user_id": self.user_id,
            "platform": self.platform.value,
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "followers_growth": self.followers_growth,
            "posts_count": self.posts_count,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_shares": self.total_shares,
            "total_comments": self.total_comments,
            "average_engagement_rate": self.average_engagement_rate,
            "top_performing_post_id": self.top_performing_post_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "collected_at": self.collected_at.isoformat(),
            "platform_metrics": self.platform_metrics
        }