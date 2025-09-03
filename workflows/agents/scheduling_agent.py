"""
Scheduling Agent for ZenAlto Social Media Management

Manages optimal content scheduling and posting queues.

Responsibilities:
- Optimal timing calculation
- Queue management
- Conflict resolution
- Bulk scheduling
- Calendar integration
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta
import uuid
import pytz
from dateutil import parser


class SchedulingAgent:
    """
    Manages optimal content scheduling and posting queues.
    
    Responsibilities:
    - Optimal timing calculation
    - Queue management
    - Conflict resolution
    - Bulk scheduling
    - Calendar integration
    """

    def __init__(
        self,
        mcp_agent,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        self.timezone_handler = self._init_timezone_handler()
        
        # Initialize agent-specific components
        self._initialize()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "model": "claude-3.5-sonnet",
            "max_tokens": 2000,
            "temperature": 0.7,
            "default_timezone": "UTC",
            "rate_limits": {
                "twitter": 300,
                "instagram": 10,
                "linkedin": 5,
                "facebook": 25,
                "youtube": 2
            },
            "optimal_times": {
                "twitter": ["09:00", "13:00", "17:00"],
                "instagram": ["11:00", "18:00"],
                "linkedin": ["09:00", "14:00"],
                "facebook": ["15:00", "19:00"],
                "youtube": ["16:00", "20:00"]
            }
        }
    
    def _initialize(self):
        """Initialize agent-specific resources."""
        self.posting_queue = {}
        self.scheduled_posts = {}
        self.rate_limit_trackers = {}
        self.timezone = pytz.timezone(self.config.get("default_timezone", "UTC"))
    
    def _init_timezone_handler(self):
        """Initialize timezone handling components."""
        return {
            "default_timezone": self.config.get("default_timezone", "UTC"),
            "supported_timezones": [
                "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
                "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo",
                "Asia/Shanghai", "Australia/Sydney"
            ]
        }

    async def schedule(
        self,
        content: Dict[str, Any],
        schedule_time: Optional[str] = None,
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule content for posting.
        
        Returns:
        {
            "scheduled_posts": [
                {
                    "post_id": "uuid",
                    "platform": "twitter",
                    "scheduled_time": "2024-01-15T09:00:00Z",
                    "status": "queued",
                    "queue_position": 3
                }
            ],
            "conflicts_resolved": [],
            "optimization_applied": true,
            "estimated_reach": {
                "total": 25000,
                "by_platform": {...}
            }
        }
        """
        try:
            self.logger.info("Scheduling content for posting")
            
            # Determine target platforms
            target_platforms = platforms or content.get("platforms", ["twitter"])
            
            # Parse schedule time
            if schedule_time:
                try:
                    scheduled_dt = parser.parse(schedule_time)
                except ValueError:
                    scheduled_dt = None
                    self.logger.warning(f"Invalid schedule time format: {schedule_time}")
            else:
                scheduled_dt = None
            
            scheduled_posts = []
            conflicts_resolved = []
            
            for platform in target_platforms:
                # Get platform-specific content
                platform_content = content.get("platform_content", {}).get(platform, content)
                
                # Determine optimal time if not specified
                if not scheduled_dt:
                    optimal_time = await self._find_optimal_time_for_platform(
                        platform, 
                        content.get("content_type", "post"),
                        content.get("target_audience")
                    )
                    scheduled_dt = optimal_time
                
                # Check for conflicts
                conflicts = await self._check_scheduling_conflicts(platform, scheduled_dt)
                if conflicts:
                    resolved_time = await self._resolve_conflict(platform, scheduled_dt, conflicts)
                    conflicts_resolved.append({
                        "platform": platform,
                        "original_time": scheduled_dt.isoformat(),
                        "resolved_time": resolved_time.isoformat(),
                        "conflict_type": "time_slot_occupied"
                    })
                    scheduled_dt = resolved_time
                
                # Create scheduled post entry
                post_id = str(uuid.uuid4())
                scheduled_post = {
                    "post_id": post_id,
                    "platform": platform,
                    "content": platform_content,
                    "scheduled_time": scheduled_dt.isoformat(),
                    "status": "queued",
                    "queue_position": await self._get_queue_position(platform, scheduled_dt),
                    "created_at": datetime.now().isoformat()
                }
                
                # Add to queue
                await self._add_to_queue(platform, scheduled_post)
                scheduled_posts.append(scheduled_post)
                
                # Use MCP tool to schedule
                try:
                    await self._call_mcp_tool("social_media_schedule_post", {
                        "platform": platform,
                        "content": platform_content,
                        "scheduled_time": scheduled_dt.isoformat(),
                        "post_id": post_id
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to schedule on {platform}: {e}")
                    scheduled_post["status"] = "failed"
                    scheduled_post["error"] = str(e)
            
            # Calculate estimated reach
            estimated_reach = await self._calculate_estimated_reach(scheduled_posts)
            
            result = {
                "scheduled_posts": scheduled_posts,
                "conflicts_resolved": conflicts_resolved,
                "optimization_applied": len(conflicts_resolved) > 0 or not schedule_time,
                "estimated_reach": estimated_reach,
                "success": True
            }
            
            self.logger.info(f"Successfully scheduled {len(scheduled_posts)} posts")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scheduling content: {e}")
            return self._get_error_response("schedule", str(e))

    async def find_optimal_times(
        self,
        platforms: List[str],
        content_type: str,
        target_audience: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """Find optimal posting times for each platform."""
        try:
            self.logger.info(f"Finding optimal times for {len(platforms)} platforms")
            
            optimal_times = {}
            
            for platform in platforms:
                platform_times = await self._find_optimal_time_for_platform(
                    platform, content_type, target_audience, return_multiple=True
                )
                optimal_times[platform] = [time.strftime("%H:%M") for time in platform_times]
            
            self.logger.info("Optimal times calculated successfully")
            return optimal_times
            
        except Exception as e:
            self.logger.error(f"Error finding optimal times: {e}")
            return {}

    async def manage_queue(
        self,
        action: str = "view"  # view, reorder, pause, resume
    ) -> Dict[str, Any]:
        """Manage the posting queue."""
        try:
            self.logger.info(f"Managing queue with action: {action}")
            
            if action == "view":
                return await self._view_queue()
            elif action == "reorder":
                return await self._reorder_queue()
            elif action == "pause":
                return await self._pause_queue()
            elif action == "resume":
                return await self._resume_queue()
            else:
                raise ValueError(f"Unsupported queue action: {action}")
                
        except Exception as e:
            self.logger.error(f"Error managing queue: {e}")
            return self._get_error_response("manage_queue", str(e))

    async def bulk_schedule(
        self,
        posts: List[Dict],
        distribution: str = "even"  # even, optimal, manual
    ) -> List[Dict[str, Any]]:
        """Schedule multiple posts with smart distribution."""
        try:
            self.logger.info(f"Bulk scheduling {len(posts)} posts with {distribution} distribution")
            
            scheduled_results = []
            
            if distribution == "even":
                results = await self._schedule_evenly(posts)
            elif distribution == "optimal":
                results = await self._schedule_optimally(posts)
            elif distribution == "manual":
                results = await self._schedule_manually(posts)
            else:
                raise ValueError(f"Unsupported distribution method: {distribution}")
            
            for result in results:
                scheduled_results.append(result)
            
            self.logger.info(f"Bulk scheduling completed: {len(scheduled_results)} posts processed")
            return scheduled_results
            
        except Exception as e:
            self.logger.error(f"Error in bulk scheduling: {e}")
            return [self._get_error_response("bulk_schedule", str(e))]

    async def handle_conflicts(
        self,
        new_post: Dict,
        existing_schedule: List[Dict]
    ) -> Dict[str, Any]:
        """Resolve scheduling conflicts."""
        try:
            self.logger.info("Handling scheduling conflicts")
            
            platform = new_post.get("platform")
            proposed_time = parser.parse(new_post.get("scheduled_time"))
            
            conflicts = []
            for existing_post in existing_schedule:
                if existing_post.get("platform") == platform:
                    existing_time = parser.parse(existing_post.get("scheduled_time"))
                    time_diff = abs((proposed_time - existing_time).total_seconds())
                    
                    # Check if posts are too close (within 30 minutes)
                    if time_diff < 1800:  # 30 minutes
                        conflicts.append({
                            "existing_post_id": existing_post.get("post_id"),
                            "existing_time": existing_time.isoformat(),
                            "time_difference_minutes": time_diff / 60
                        })
            
            if not conflicts:
                return {
                    "conflicts_found": False,
                    "resolution": "none_needed",
                    "recommended_time": proposed_time.isoformat()
                }
            
            # Resolve conflicts by finding alternative time
            alternative_time = await self._find_alternative_time(
                platform, proposed_time, existing_schedule
            )
            
            return {
                "conflicts_found": True,
                "conflicts": conflicts,
                "resolution": "time_adjusted",
                "original_time": proposed_time.isoformat(),
                "recommended_time": alternative_time.isoformat(),
                "adjustment_reason": "Avoid posting conflicts"
            }
            
        except Exception as e:
            self.logger.error(f"Error handling conflicts: {e}")
            return self._get_error_response("handle_conflicts", str(e))

    async def _call_mcp_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Any:
        """Wrapper for MCP tool calls."""
        try:
            result = await self.mcp_agent.call_tool(tool_name, params)
            return result
        except Exception as e:
            self.logger.error(f"MCP tool call failed: {e}")
            raise

    async def _find_optimal_time_for_platform(
        self,
        platform: str,
        content_type: str,
        target_audience: Optional[Dict] = None,
        return_multiple: bool = False
    ) -> datetime:
        """Find optimal posting time for a specific platform."""
        # Get platform's optimal times from config
        platform_times = self.config.get("optimal_times", {}).get(platform, ["12:00"])
        
        # Consider target audience timezone if provided
        audience_timezone = "UTC"
        if target_audience and target_audience.get("timezone"):
            audience_timezone = target_audience["timezone"]
        
        target_tz = pytz.timezone(audience_timezone)
        now = datetime.now(target_tz)
        
        # Find next optimal time
        optimal_times = []
        for time_str in platform_times:
            hour, minute = map(int, time_str.split(":"))
            optimal_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if optimal_time <= now:
                optimal_time += timedelta(days=1)
            
            optimal_times.append(optimal_time)
        
        if return_multiple:
            return optimal_times
        else:
            return min(optimal_times)  # Return earliest time

    async def _check_scheduling_conflicts(self, platform: str, scheduled_time: datetime) -> List[Dict]:
        """Check for scheduling conflicts on a platform."""
        conflicts = []
        
        if platform in self.posting_queue:
            for post in self.posting_queue[platform]:
                post_time = parser.parse(post["scheduled_time"])
                time_diff = abs((scheduled_time - post_time).total_seconds())
                
                # Conflict if within 30 minutes
                if time_diff < 1800:
                    conflicts.append({
                        "post_id": post["post_id"],
                        "scheduled_time": post["scheduled_time"],
                        "time_difference": time_diff
                    })
        
        return conflicts

    async def _resolve_conflict(self, platform: str, original_time: datetime, conflicts: List[Dict]) -> datetime:
        """Resolve scheduling conflict by finding alternative time."""
        # Try times 1 hour after the original time
        alternative_time = original_time + timedelta(hours=1)
        
        # Check if this time also has conflicts
        new_conflicts = await self._check_scheduling_conflicts(platform, alternative_time)
        
        if new_conflicts:
            # Keep incrementing by 30 minutes until we find a free slot
            for i in range(24):  # Try for 12 hours
                alternative_time = original_time + timedelta(minutes=30 * (i + 1))
                new_conflicts = await self._check_scheduling_conflicts(platform, alternative_time)
                if not new_conflicts:
                    break
        
        return alternative_time

    async def _get_queue_position(self, platform: str, scheduled_time: datetime) -> int:
        """Get position in queue for the scheduled time."""
        if platform not in self.posting_queue:
            return 1
        
        position = 1
        for post in self.posting_queue[platform]:
            post_time = parser.parse(post["scheduled_time"])
            if post_time < scheduled_time:
                position += 1
        
        return position

    async def _add_to_queue(self, platform: str, scheduled_post: Dict):
        """Add post to the platform queue."""
        if platform not in self.posting_queue:
            self.posting_queue[platform] = []
        
        self.posting_queue[platform].append(scheduled_post)
        
        # Sort by scheduled time
        self.posting_queue[platform].sort(key=lambda p: p["scheduled_time"])

    async def _calculate_estimated_reach(self, scheduled_posts: List[Dict]) -> Dict[str, Any]:
        """Calculate estimated reach for scheduled posts."""
        total_reach = 0
        platform_reach = {}
        
        # Base reach estimates by platform
        platform_base_reach = {
            "twitter": 5000,
            "instagram": 3000,
            "linkedin": 2000,
            "facebook": 4000,
            "youtube": 8000
        }
        
        for post in scheduled_posts:
            platform = post["platform"]
            base_reach = platform_base_reach.get(platform, 1000)
            
            # Adjust based on optimal timing
            scheduled_time = parser.parse(post["scheduled_time"])
            hour = scheduled_time.hour
            
            # Peak hours get higher reach
            if 9 <= hour <= 11 or 14 <= hour <= 16:
                base_reach *= 1.3
            elif 18 <= hour <= 20:
                base_reach *= 1.2
            
            platform_reach[platform] = platform_reach.get(platform, 0) + base_reach
            total_reach += base_reach
        
        return {
            "total": int(total_reach),
            "by_platform": {k: int(v) for k, v in platform_reach.items()}
        }

    async def _view_queue(self) -> Dict[str, Any]:
        """View current posting queue."""
        queue_info = {
            "total_posts": 0,
            "by_platform": {},
            "next_posts": []
        }
        
        all_posts = []
        for platform, posts in self.posting_queue.items():
            queue_info["by_platform"][platform] = {
                "count": len(posts),
                "next_post": posts[0]["scheduled_time"] if posts else None
            }
            queue_info["total_posts"] += len(posts)
            all_posts.extend(posts)
        
        # Sort all posts by time and get next 5
        all_posts.sort(key=lambda p: p["scheduled_time"])
        queue_info["next_posts"] = all_posts[:5]
        
        return queue_info

    async def _reorder_queue(self) -> Dict[str, Any]:
        """Reorder posts in queue based on optimal timing."""
        reordered_count = 0
        
        for platform in self.posting_queue:
            posts = self.posting_queue[platform]
            
            # Re-optimize timing for all posts
            for i, post in enumerate(posts):
                optimal_time = await self._find_optimal_time_for_platform(
                    platform, 
                    post.get("content_type", "post"),
                    post.get("target_audience")
                )
                
                if optimal_time.isoformat() != post["scheduled_time"]:
                    post["scheduled_time"] = optimal_time.isoformat()
                    reordered_count += 1
            
            # Re-sort by time
            posts.sort(key=lambda p: p["scheduled_time"])
        
        return {
            "reordered": True,
            "posts_affected": reordered_count,
            "message": f"Reordered {reordered_count} posts for optimal timing"
        }

    async def _pause_queue(self) -> Dict[str, Any]:
        """Pause the posting queue."""
        paused_count = 0
        
        for platform in self.posting_queue:
            for post in self.posting_queue[platform]:
                if post["status"] == "queued":
                    post["status"] = "paused"
                    paused_count += 1
        
        return {
            "paused": True,
            "posts_paused": paused_count,
            "message": f"Paused {paused_count} posts"
        }

    async def _resume_queue(self) -> Dict[str, Any]:
        """Resume the posting queue."""
        resumed_count = 0
        
        for platform in self.posting_queue:
            for post in self.posting_queue[platform]:
                if post["status"] == "paused":
                    post["status"] = "queued"
                    resumed_count += 1
        
        return {
            "resumed": True,
            "posts_resumed": resumed_count,
            "message": f"Resumed {resumed_count} posts"
        }

    async def _schedule_evenly(self, posts: List[Dict]) -> List[Dict]:
        """Schedule posts with even distribution."""
        results = []
        
        if not posts:
            return results
        
        # Calculate time intervals
        start_time = datetime.now() + timedelta(hours=1)
        interval_hours = 24 // len(posts) if len(posts) < 24 else 1
        
        for i, post in enumerate(posts):
            scheduled_time = start_time + timedelta(hours=i * interval_hours)
            post["scheduled_time"] = scheduled_time.isoformat()
            
            result = await self.schedule(
                post,
                scheduled_time.isoformat(),
                post.get("platforms", ["twitter"])
            )
            results.append(result)
        
        return results

    async def _schedule_optimally(self, posts: List[Dict]) -> List[Dict]:
        """Schedule posts at optimal times."""
        results = []
        
        for post in posts:
            platforms = post.get("platforms", ["twitter"])
            
            # Find optimal time for primary platform
            primary_platform = platforms[0]
            optimal_time = await self._find_optimal_time_for_platform(
                primary_platform,
                post.get("content_type", "post"),
                post.get("target_audience")
            )
            
            result = await self.schedule(
                post,
                optimal_time.isoformat(),
                platforms
            )
            results.append(result)
        
        return results

    async def _schedule_manually(self, posts: List[Dict]) -> List[Dict]:
        """Schedule posts using manually specified times."""
        results = []
        
        for post in posts:
            manual_time = post.get("scheduled_time")
            if not manual_time:
                # Default to 1 hour from now if no time specified
                manual_time = (datetime.now() + timedelta(hours=1)).isoformat()
            
            result = await self.schedule(
                post,
                manual_time,
                post.get("platforms", ["twitter"])
            )
            results.append(result)
        
        return results

    async def _find_alternative_time(
        self,
        platform: str,
        preferred_time: datetime,
        existing_schedule: List[Dict]
    ) -> datetime:
        """Find alternative time that doesn't conflict with existing schedule."""
        
        # Get all scheduled times for this platform
        scheduled_times = []
        for post in existing_schedule:
            if post.get("platform") == platform:
                scheduled_times.append(parser.parse(post["scheduled_time"]))
        
        # Try times in 30-minute increments
        for offset_minutes in range(30, 24 * 60, 30):  # Up to 24 hours
            candidate_time = preferred_time + timedelta(minutes=offset_minutes)
            
            # Check if this time conflicts with any existing posts
            has_conflict = False
            for scheduled_time in scheduled_times:
                if abs((candidate_time - scheduled_time).total_seconds()) < 1800:  # 30 minutes
                    has_conflict = True
                    break
            
            if not has_conflict:
                return candidate_time
        
        # If no good time found, just add 2 hours
        return preferred_time + timedelta(hours=2)

    def _get_error_response(self, operation: str, error_message: str) -> Dict[str, Any]:
        """Get standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }