"""
Analytics Dashboard Widget for ZenAlto

Analytics and performance tracking dashboard with interactive charts.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List


class AnalyticsDashboard:
    """Analytics and performance tracking dashboard."""
    
    def render(self):
        """Render analytics dashboard."""
        
        # Time range selector
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last 7 days", "Last 30 days", "Last 3 months", "Custom"],
                key="analytics_time_range"
            )
        
        with col2:
            platforms = st.multiselect(
                "Platforms",
                ["All", "Twitter", "LinkedIn", "Instagram"],
                default=["All"],
                key="analytics_platforms"
            )
        
        # Key metrics
        self._render_key_metrics()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_engagement_chart()
        
        with col2:
            self._render_growth_chart()
        
        # Performance table
        self._render_performance_table()
        
        # AI Insights
        self._render_ai_insights()
    
    def _render_key_metrics(self):
        """Render key performance metrics."""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Reach",
                "125.3K",
                "↑ 12.5%",
                help="Total unique users who saw your content"
            )
        
        with col2:
            st.metric(
                "Engagement Rate",
                "4.8%",
                "↑ 0.3%",
                help="Average engagement across all posts"
            )
        
        with col3:
            st.metric(
                "New Followers",
                "842",
                "↑ 125",
                help="Net new followers this period"
            )
        
        with col4:
            st.metric(
                "Posts Published",
                "47",
                "↑ 8",
                help="Total posts published this period"
            )
    
    def _render_engagement_chart(self):
        """Render engagement over time chart."""
        
        st.subheader("Engagement Trend")
        
        # Sample data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        engagement = np.random.randn(30).cumsum() + 5
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=engagement,
            mode='lines+markers',
            name='Engagement Rate',
            line=dict(color='#1DA1F2', width=2),
            fill='tozeroy',
            fillcolor='rgba(29, 161, 242, 0.1)'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Date",
            yaxis_title="Engagement Rate (%)",
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_growth_chart(self):
        """Render follower growth chart."""
        
        st.subheader("Follower Growth")
        
        # Sample data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        followers = np.random.randint(10, 50, 30).cumsum() + 1000
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=followers,
            mode='lines+markers',
            name='Followers',
            line=dict(color='#0077B5', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 119, 181, 0.1)'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Date",
            yaxis_title="Total Followers",
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_table(self):
        """Render performance table with top posts."""
        
        st.subheader("Top Performing Posts")
        
        # Sample data
        posts_data = {
            'Platform': ['Twitter', 'LinkedIn', 'Instagram', 'Twitter', 'LinkedIn'],
            'Content': [
                '🚀 AI breakthrough announced...',
                'Sharing insights on automation...',
                '📸 Behind the scenes development...',
                '💡 New features coming soon...',
                '🔬 Research paper published...'
            ],
            'Reach': [12500, 8900, 15600, 9200, 11800],
            'Engagement': [540, 312, 890, 420, 385],
            'Engagement Rate': ['4.3%', '3.5%', '5.7%', '4.6%', '3.3%']
        }
        
        df = pd.DataFrame(posts_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Reach": st.column_config.NumberColumn(
                    "Reach",
                    format="%d"
                ),
                "Engagement": st.column_config.NumberColumn(
                    "Engagement", 
                    format="%d"
                )
            }
        )
    
    def _render_ai_insights(self):
        """Render AI-powered insights and recommendations."""
        
        st.subheader("🤖 AI Insights & Recommendations")
        
        insights = [
            {
                'type': 'success',
                'title': '🎯 Best Posting Time',
                'message': 'Your audience is most active between 2-4 PM. Schedule more posts during this time.'
            },
            {
                'type': 'info',
                'title': '📈 Trending Topics',
                'message': 'AI and automation topics are performing 35% better than average.'
            },
            {
                'type': 'warning',
                'title': '🔄 Engagement Drop',
                'message': 'LinkedIn engagement decreased by 15% this week. Consider more professional content.'
            },
            {
                'type': 'info',
                'title': '🏷️ Hashtag Performance',
                'message': '#Innovation and #TechTrends are your top performing hashtags.'
            }
        ]
        
        for insight in insights:
            if insight['type'] == 'success':
                st.success(f"**{insight['title']}**\n{insight['message']}")
            elif insight['type'] == 'info':
                st.info(f"**{insight['title']}**\n{insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"**{insight['title']}**\n{insight['message']}")
    
    def render_platform_analytics(self, platform: str):
        """Render analytics for a specific platform."""
        
        st.subheader(f"📊 {platform.title()} Analytics")
        
        # Platform-specific metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Platform Reach", "45.2K", "↑ 8.1%")
        with col2:
            st.metric("Platform Engagement", "3.8%", "↓ 0.2%")
        with col3:
            st.metric("Platform Followers", "2.1K", "↑ 67")
        
        # Platform-specific chart
        self._render_platform_specific_chart(platform)
    
    def _render_platform_specific_chart(self, platform: str):
        """Render platform-specific analytics chart."""
        
        # Sample data based on platform
        dates = pd.date_range(end=datetime.now(), periods=14, freq='D')
        
        if platform.lower() == 'twitter':
            metric_name = 'Tweets'
            values = np.random.poisson(5, 14)  # Tweet frequency
        elif platform.lower() == 'linkedin':
            metric_name = 'Posts'
            values = np.random.poisson(2, 14)  # LinkedIn posts
        else:
            metric_name = 'Posts'
            values = np.random.poisson(3, 14)  # Generic posts
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates,
            y=values,
            name=metric_name,
            marker_color='#1DA1F2'
        ))
        
        fig.update_layout(
            title=f"Daily {metric_name} - {platform.title()}",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_analytics_dashboard():
    """Convenience function to render analytics dashboard."""
    dashboard = AnalyticsDashboard()
    dashboard.render()