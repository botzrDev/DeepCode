"""
Analytics Agent for ZENALTO Social Media Management

This agent handles performance tracking, analytics collection, and insights
generation for social media content and campaigns.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class AnalyticsAgent:
    """
    Analytics Agent for tracking social media performance and generating insights.

    Responsibilities:
    - Collect and analyze engagement metrics
    - Track content performance across platforms
    - Generate insights and recommendations
    - Monitor audience growth and demographics
    - Provide performance reporting
    """

    def __init__(self, mcp_agent, logger: Optional[logging.Logger] = None):
        """
        Initialize the Analytics Agent.

        Args:
            mcp_agent: MCP agent instance for tool calls
            logger: Optional logger instance
        """
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)

    async def analyze_performance(
        self, content_history: List[Dict[str, Any]], time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Analyze content performance across platforms.

        Args:
            content_history: List of previously posted content with metrics
            time_range: Analysis time range (7d, 30d, 90d)

        Returns:
            Dict containing performance analysis
        """
        try:
            self.logger.info(f"Analyzing performance for {time_range} time range")

            analysis = {
                "analysis_id": self._generate_analysis_id(),
                "created_at": datetime.now().isoformat(),
                "time_range": time_range,
                "total_posts": len(content_history),
                "platform_performance": {},
                "top_performing_content": [],
                "content_type_analysis": {},
                "engagement_trends": {},
                "audience_insights": {},
                "recommendations": [],
            }

            if not content_history:
                analysis["recommendations"].append(
                    "No historical data available for analysis"
                )
                return analysis

            # Analyze by platform
            platforms = set()
            for content in content_history:
                platform = content.get("platform", "unknown")
                platforms.add(platform)

            for platform in platforms:
                platform_data = [
                    c for c in content_history if c.get("platform") == platform
                ]
                analysis["platform_performance"][platform] = (
                    self._analyze_platform_performance(platform_data)
                )

            # Find top performing content
            analysis["top_performing_content"] = self._identify_top_content(
                content_history
            )

            # Analyze content types
            analysis["content_type_analysis"] = self._analyze_content_types(
                content_history
            )

            # Track engagement trends
            analysis["engagement_trends"] = self._analyze_engagement_trends(
                content_history
            )

            # Generate recommendations
            analysis["recommendations"] = self._generate_analytics_recommendations(
                analysis
            )

            self.logger.info(f"Analysis completed for {len(platforms)} platforms")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing performance: {str(e)}")
            return self._get_default_analysis()

    def _analyze_platform_performance(
        self, platform_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze performance for a specific platform.

        Args:
            platform_data: Content data for a specific platform

        Returns:
            Dict containing platform performance metrics
        """
        if not platform_data:
            return {"total_posts": 0, "avg_engagement": 0}

        total_likes = sum(c.get("metrics", {}).get("likes", 0) for c in platform_data)
        total_comments = sum(
            c.get("metrics", {}).get("comments", 0) for c in platform_data
        )
        total_shares = sum(c.get("metrics", {}).get("shares", 0) for c in platform_data)
        total_views = sum(c.get("metrics", {}).get("views", 0) for c in platform_data)

        avg_engagement = (
            (total_likes + total_comments + total_shares) / len(platform_data)
            if platform_data
            else 0
        )

        return {
            "total_posts": len(platform_data),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_views": total_views,
            "avg_engagement": round(avg_engagement, 2),
            "engagement_rate": self._calculate_engagement_rate(
                total_likes + total_comments + total_shares, total_views
            ),
            "best_posting_time": self._find_best_posting_time(platform_data),
            "top_hashtags": self._find_top_hashtags(platform_data),
        }

    def _calculate_engagement_rate(
        self, total_engagement: int, total_views: int
    ) -> float:
        """Calculate engagement rate percentage."""
        if total_views == 0:
            return 0.0
        return round((total_engagement / total_views) * 100, 2)

    def _find_best_posting_time(self, platform_data: List[Dict[str, Any]]) -> str:
        """
        Find the best posting time based on historical performance.

        Args:
            platform_data: Content data for analysis

        Returns:
            String describing the best posting time
        """
        if not platform_data:
            return "Not enough data"

        # Simple analysis based on mock data
        time_performance = {}
        for content in platform_data:
            posted_at = content.get("posted_at", "")
            if posted_at:
                try:
                    dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
                    hour = dt.hour
                    engagement = content.get("metrics", {}).get(
                        "likes", 0
                    ) + content.get("metrics", {}).get("comments", 0)

                    if hour not in time_performance:
                        time_performance[hour] = []
                    time_performance[hour].append(engagement)
                except (ValueError, AttributeError):
                    continue

        if not time_performance:
            return "Not enough data"

        # Find hour with highest average engagement
        best_hour = max(
            time_performance.keys(),
            key=lambda h: sum(time_performance[h]) / len(time_performance[h]),
        )

        return f"{best_hour:02d}:00 - {(best_hour + 1) % 24:02d}:00"

    def _find_top_hashtags(self, platform_data: List[Dict[str, Any]]) -> List[str]:
        """
        Find top performing hashtags.

        Args:
            platform_data: Content data for analysis

        Returns:
            List of top hashtags
        """
        hashtag_performance = {}

        for content in platform_data:
            hashtags = content.get("hashtags", [])
            engagement = content.get("metrics", {}).get("likes", 0) + content.get(
                "metrics", {}
            ).get("comments", 0)

            for hashtag in hashtags:
                if hashtag not in hashtag_performance:
                    hashtag_performance[hashtag] = []
                hashtag_performance[hashtag].append(engagement)

        # Sort hashtags by average engagement
        sorted_hashtags = sorted(
            hashtag_performance.keys(),
            key=lambda h: sum(hashtag_performance[h]) / len(hashtag_performance[h]),
            reverse=True,
        )

        return sorted_hashtags[:5]  # Top 5 hashtags

    def _identify_top_content(
        self, content_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify top performing content.

        Args:
            content_history: All content history

        Returns:
            List of top performing content items
        """
        if not content_history:
            return []

        # Sort by total engagement (likes + comments + shares)
        scored_content = []
        for content in content_history:
            metrics = content.get("metrics", {})
            engagement_score = (
                metrics.get("likes", 0)
                + metrics.get("comments", 0)
                + metrics.get("shares", 0)
            )

            scored_content.append(
                {
                    "content": content,
                    "engagement_score": engagement_score,
                    "platform": content.get("platform", "unknown"),
                    "content_type": content.get("content_type", "post"),
                    "posted_at": content.get("posted_at", ""),
                }
            )

        # Sort by engagement score and return top 5
        scored_content.sort(key=lambda x: x["engagement_score"], reverse=True)
        return scored_content[:5]

    def _analyze_content_types(
        self, content_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze performance by content type.

        Args:
            content_history: All content history

        Returns:
            Dict of content type performance
        """
        type_performance = {}

        for content in content_history:
            content_type = content.get("content_type", "post")
            metrics = content.get("metrics", {})
            engagement = (
                metrics.get("likes", 0)
                + metrics.get("comments", 0)
                + metrics.get("shares", 0)
            )

            if content_type not in type_performance:
                type_performance[content_type] = {"count": 0, "total_engagement": 0}

            type_performance[content_type]["count"] += 1
            type_performance[content_type]["total_engagement"] += engagement

        # Calculate averages
        for content_type in type_performance:
            data = type_performance[content_type]
            data["avg_engagement"] = (
                data["total_engagement"] / data["count"] if data["count"] > 0 else 0
            )

        return type_performance

    def _analyze_engagement_trends(
        self, content_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze engagement trends over time.

        Args:
            content_history: All content history

        Returns:
            Dict of engagement trends
        """
        if not content_history:
            return {"trend": "no_data", "change": 0}

        # Sort by date
        dated_content = []
        for content in content_history:
            posted_at = content.get("posted_at", "")
            if posted_at:
                try:
                    dt = datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
                    metrics = content.get("metrics", {})
                    engagement = (
                        metrics.get("likes", 0)
                        + metrics.get("comments", 0)
                        + metrics.get("shares", 0)
                    )
                    dated_content.append({"date": dt, "engagement": engagement})
                except (ValueError, AttributeError):
                    continue

        if len(dated_content) < 2:
            return {"trend": "insufficient_data", "change": 0}

        dated_content.sort(key=lambda x: x["date"])

        # Simple trend analysis - compare first half vs second half
        mid_point = len(dated_content) // 2
        first_half_avg = (
            sum(c["engagement"] for c in dated_content[:mid_point]) / mid_point
        )
        second_half_avg = sum(c["engagement"] for c in dated_content[mid_point:]) / (
            len(dated_content) - mid_point
        )

        change = (
            ((second_half_avg - first_half_avg) / first_half_avg * 100)
            if first_half_avg > 0
            else 0
        )

        if change > 10:
            trend = "improving"
        elif change < -10:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change": round(change, 2),
            "first_period_avg": round(first_half_avg, 2),
            "second_period_avg": round(second_half_avg, 2),
        }

    def _generate_analytics_recommendations(
        self, analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on analytics.

        Args:
            analysis: Performance analysis results

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # Platform-specific recommendations
        for platform, perf in analysis.get("platform_performance", {}).items():
            engagement_rate = perf.get("engagement_rate", 0)

            if engagement_rate < 2:
                recommendations.append(
                    f"Improve {platform} engagement rate (currently {engagement_rate}%)"
                )
            elif engagement_rate > 5:
                recommendations.append(
                    f"Excellent {platform} performance! Consider increasing posting frequency"
                )

        # Content type recommendations
        content_analysis = analysis.get("content_type_analysis", {})
        if content_analysis:
            best_type = max(
                content_analysis.keys(),
                key=lambda t: content_analysis[t].get("avg_engagement", 0),
            )
            recommendations.append(
                f"Focus more on '{best_type}' content (highest engagement)"
            )

        # Trend recommendations
        trends = analysis.get("engagement_trends", {})
        if trends.get("trend") == "declining":
            recommendations.append(
                "Engagement is declining - consider refreshing content strategy"
            )
        elif trends.get("trend") == "improving":
            recommendations.append(
                "Engagement is improving - maintain current content approach"
            )

        # General recommendations
        if analysis.get("total_posts", 0) < 10:
            recommendations.append(
                "Increase posting consistency for better analytics insights"
            )

        return recommendations

    async def generate_report(
        self, analysis: Dict[str, Any], format_type: str = "summary"
    ) -> str:
        """
        Generate a formatted analytics report.

        Args:
            analysis: Performance analysis data
            format_type: Type of report (summary, detailed, executive)

        Returns:
            Formatted report string
        """
        try:
            if format_type == "summary":
                return self._generate_summary_report(analysis)
            elif format_type == "detailed":
                return self._generate_detailed_report(analysis)
            elif format_type == "executive":
                return self._generate_executive_report(analysis)
            else:
                return self._generate_summary_report(analysis)

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return f"Report generation error: {str(e)}"

    def _generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary analytics report."""
        report = f"""
SOCIAL MEDIA PERFORMANCE SUMMARY
===============================
Analysis Period: {analysis.get('time_range', 'N/A')}
Generated: {analysis.get('created_at', 'N/A')}

OVERVIEW
--------
Total Posts: {analysis.get('total_posts', 0)}
Platforms: {len(analysis.get('platform_performance', {}))}

PLATFORM PERFORMANCE
-------------------
"""

        for platform, perf in analysis.get("platform_performance", {}).items():
            report += f"{platform.upper()}: {perf.get('total_posts', 0)} posts, "
            report += f"{perf.get('engagement_rate', 0)}% engagement rate\n"

        report += "\nTOP RECOMMENDATIONS\n-------------------\n"
        for i, rec in enumerate(analysis.get("recommendations", [])[:3], 1):
            report += f"{i}. {rec}\n"

        return report

    def _generate_detailed_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a detailed analytics report."""
        # More comprehensive report format
        return self._generate_summary_report(analysis)  # Simplified for now

    def _generate_executive_report(self, analysis: Dict[str, Any]) -> str:
        """Generate an executive summary report."""
        # High-level executive summary format
        return self._generate_summary_report(analysis)  # Simplified for now

    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID."""
        return f"analysis_{int(datetime.now().timestamp())}"

    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        Provide default analysis when generation fails.

        Returns:
            Default analysis structure
        """
        return {
            "analysis_id": self._generate_analysis_id(),
            "created_at": datetime.now().isoformat(),
            "time_range": "30d",
            "total_posts": 0,
            "platform_performance": {},
            "top_performing_content": [],
            "content_type_analysis": {},
            "engagement_trends": {"trend": "no_data", "change": 0},
            "audience_insights": {},
            "recommendations": [
                "No data available for analysis - start posting content to track performance"
            ],
        }


class SchedulingAgent:
    """
    Scheduling Agent for managing social media posting schedules.

    Responsibilities:
    - Schedule content across multiple platforms
    - Manage posting queues and timing
    - Handle rate limits and conflicts
    - Optimize posting times based on audience data
    """

    def __init__(self, mcp_agent, logger: Optional[logging.Logger] = None):
        """
        Initialize the Scheduling Agent.

        Args:
            mcp_agent: MCP agent instance for tool calls
            logger: Optional logger instance
        """
        self.mcp_agent = mcp_agent
        self.logger = logger or logging.getLogger(__name__)

        # Platform rate limits (posts per day)
        self.rate_limits = {
            "twitter": 300,
            "instagram": 10,
            "linkedin": 5,
            "facebook": 25,
            "youtube": 2,
        }

    async def schedule_content(
        self,
        content: Dict[str, Any],
        schedule_time: str = None,
        platform_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Schedule content for posting across platforms.

        Args:
            content: Generated content to schedule
            schedule_time: Preferred scheduling time (ISO format)
            platform_preferences: Platform-specific preferences

        Returns:
            Dict containing scheduling results
        """
        try:
            self.logger.info("Scheduling content for posting...")

            platforms = content.get("platforms", [])
            platform_content = content.get("platform_content", {})

            scheduling_result = {
                "scheduling_id": self._generate_scheduling_id(),
                "created_at": datetime.now().isoformat(),
                "content_id": content.get("generation_id", "unknown"),
                "platforms": platforms,
                "scheduled_posts": [],
                "rate_limit_warnings": [],
                "conflicts": [],
                "recommendations": [],
            }

            for platform in platforms:
                if platform in platform_content:
                    post_schedule = await self._schedule_platform_post(
                        platform,
                        platform_content[platform],
                        schedule_time,
                        platform_preferences,
                    )
                    scheduling_result["scheduled_posts"].append(post_schedule)

                    # Check rate limits
                    if self._check_rate_limit_warning(platform):
                        scheduling_result["rate_limit_warnings"].append(
                            f"{platform}: Approaching rate limit"
                        )

            # Generate scheduling recommendations
            scheduling_result["recommendations"] = (
                self._generate_scheduling_recommendations(scheduling_result, platforms)
            )

            self.logger.info(f"Content scheduled for {len(platforms)} platforms")
            return scheduling_result

        except Exception as e:
            self.logger.error(f"Error scheduling content: {str(e)}")
            return self._get_default_scheduling_result(content)

    async def _schedule_platform_post(
        self,
        platform: str,
        platform_content: Dict[str, Any],
        schedule_time: str = None,
        preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific platform.

        Args:
            platform: Target platform
            platform_content: Platform-specific content
            schedule_time: Preferred scheduling time
            preferences: Platform preferences

        Returns:
            Dict containing post scheduling details
        """
        # Determine optimal posting time
        if schedule_time:
            try:
                scheduled_time = datetime.fromisoformat(
                    schedule_time.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                scheduled_time = self._get_optimal_time(platform)
        else:
            scheduled_time = self._get_optimal_time(platform)

        # Generate backup time (1 hour later)
        backup_time = scheduled_time + timedelta(hours=1)

        return {
            "platform": platform,
            "content": platform_content,
            "scheduled_time": scheduled_time.isoformat(),
            "backup_time": backup_time.isoformat(),
            "status": "scheduled",
            "reasoning": self._get_scheduling_reasoning(platform, scheduled_time),
        }

    def _get_optimal_time(self, platform: str) -> datetime:
        """
        Get optimal posting time for a platform.

        Args:
            platform: Target platform

        Returns:
            Optimal datetime for posting
        """
        # Platform-specific optimal times (simplified)
        optimal_times = {
            "twitter": {"hour": 14, "minute": 30},  # 2:30 PM
            "instagram": {"hour": 18, "minute": 0},  # 6:00 PM
            "linkedin": {"hour": 9, "minute": 0},  # 9:00 AM
            "facebook": {"hour": 15, "minute": 0},  # 3:00 PM
            "youtube": {"hour": 16, "minute": 0},  # 4:00 PM
        }

        now = datetime.now()
        optimal = optimal_times.get(platform, {"hour": 12, "minute": 0})

        # Schedule for today if the time hasn't passed, otherwise tomorrow
        scheduled_time = now.replace(
            hour=optimal["hour"], minute=optimal["minute"], second=0, microsecond=0
        )

        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)

        return scheduled_time

    def _get_scheduling_reasoning(self, platform: str, scheduled_time: datetime) -> str:
        """
        Generate reasoning for scheduling decision.

        Args:
            platform: Target platform
            scheduled_time: Scheduled posting time

        Returns:
            String explaining the scheduling decision
        """
        hour = scheduled_time.hour

        reasoning_templates = {
            "twitter": f"Optimal engagement time for Twitter ({hour}:00)",
            "instagram": f"Peak Instagram activity period ({hour}:00)",
            "linkedin": f"Professional hours for maximum visibility ({hour}:00)",
            "facebook": f"High Facebook engagement window ({hour}:00)",
            "youtube": f"Optimal YouTube posting time ({hour}:00)",
        }

        return reasoning_templates.get(
            platform, f"Scheduled for {hour}:00 based on general best practices"
        )

    def _check_rate_limit_warning(self, platform: str) -> bool:
        """
        Check if approaching rate limits for platform.

        Args:
            platform: Platform to check

        Returns:
            True if approaching rate limit
        """
        # Simplified check - in real implementation, would track actual posting history
        return False

    def _generate_scheduling_recommendations(
        self, scheduling_result: Dict[str, Any], platforms: List[str]
    ) -> List[str]:
        """
        Generate scheduling recommendations.

        Args:
            scheduling_result: Current scheduling results
            platforms: Target platforms

        Returns:
            List of scheduling recommendations
        """
        recommendations = [
            "Monitor posting performance and adjust times based on engagement",
            "Consider time zone differences if audience is global",
            "Use backup posting times if conflicts arise",
        ]

        if len(platforms) > 3:
            recommendations.append(
                "Consider staggering posts across platforms to manage workflow"
            )

        if scheduling_result.get("rate_limit_warnings"):
            recommendations.append(
                "Monitor rate limits and spread content across time periods"
            )

        return recommendations

    def _generate_scheduling_id(self) -> str:
        """Generate unique scheduling ID."""
        return f"schedule_{int(datetime.now().timestamp())}"

    def _get_default_scheduling_result(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide default scheduling result when scheduling fails.

        Args:
            content: Original content

        Returns:
            Default scheduling structure
        """
        return {
            "scheduling_id": self._generate_scheduling_id(),
            "created_at": datetime.now().isoformat(),
            "content_id": content.get("generation_id", "unknown"),
            "platforms": content.get("platforms", []),
            "scheduled_posts": [],
            "rate_limit_warnings": [],
            "conflicts": [],
            "recommendations": ["Manual scheduling required due to system error"],
        }
