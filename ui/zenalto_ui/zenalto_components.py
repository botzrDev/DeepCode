"""
ZENALTO UI Components for Social Media Management

This module provides specialized UI components for ZENALTO social media management features,
including platform connections, content creation, scheduling, analytics, and campaign management.
"""

import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ZenAltoComponents:
    """Collection of UI components for ZENALTO social media management features."""
    
    @staticmethod
    def render_platform_connection_card(platform_id: str, config: Dict[str, Any]) -> None:
        """
        Render individual platform connection card with status and management options.
        
        Args:
            platform_id: Platform identifier (twitter, linkedin, etc.)
            config: Platform configuration with name, icon, features
        """
        is_connected = st.session_state.platform_connections.get(platform_id, {}).get('connected', False)
        
        with st.container():
            # Platform header with status
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"<div style='font-size: 2rem; text-align: center;'>{config['icon']}</div>", 
                           unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{config['name']}**")
                if is_connected:
                    st.success("Connected ✅")
                    # Show connection details
                    connection_data = st.session_state.platform_connections[platform_id]
                    if connection_data.get('connected_at'):
                        st.caption(f"Connected: {connection_data['connected_at'][:10]}")
                else:
                    st.error("Not Connected ❌")
            
            with col3:
                if is_connected:
                    if st.button("Disconnect", key=f"disconnect_{platform_id}"):
                        ZenAltoComponents._disconnect_platform(platform_id)
                else:
                    if st.button("Connect", key=f"connect_{platform_id}"):
                        ZenAltoComponents._connect_platform(platform_id)
            
            # Platform features and stats (only when connected)
            if is_connected:
                connection_data = st.session_state.platform_connections[platform_id]
                
                st.markdown("**Platform Features:**")
                feature_cols = st.columns(len(config.get('features', [])))
                for i, feature in enumerate(config.get('features', [])):
                    with feature_cols[i]:
                        st.caption(f"• {feature}")
                
                # Platform stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Posts This Month", connection_data.get('posts_this_month', 0))
                with col2:
                    st.metric("Avg. Engagement", f"{connection_data.get('avg_engagement', 0):.1%}")
                with col3:
                    last_post = connection_data.get('last_post_date', 'Never')
                    if last_post != 'Never' and len(last_post) > 10:
                        last_post = last_post[:10]  # Show only date part
                    st.metric("Last Post", last_post)
    
    @staticmethod
    def render_content_preview_card(content: Dict[str, Any], platform: str) -> None:
        """
        Render content preview with platform-specific formatting and actions.
        
        Args:
            content: Content data with text, hashtags, media
            platform: Target platform identifier
        """
        with st.container():
            st.markdown(f"### 📱 {platform.title()} Post Preview")
            
            # Content preview box
            content_text = content.get('text', '')
            
            # Create a styled preview box
            st.markdown(
                f"""
                <div style="
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
                ">
                    <div style="margin-bottom: 10px;">{content_text}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Hashtags
            hashtags = content.get('hashtags', [])
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                st.markdown(f"**Hashtags:** {hashtag_text}")
            
            # Platform-specific metrics
            platform_specific = content.get('platform_specific', {})
            col1, col2, col3 = st.columns(3)
            
            with col1:
                char_count = platform_specific.get('character_count', len(content_text))
                char_limit = platform_specific.get('character_limit', 280)
                # color = "normal" if char_count <= char_limit else "inverse"  # Unused
                st.metric("Characters", f"{char_count}/{char_limit}", delta=None)
            
            with col2:
                engagement = platform_specific.get('estimated_engagement', {})
                est_rate = engagement.get('estimated_rate', 0)
                st.metric("Est. Engagement", f"{est_rate:.1%}")
            
            with col3:
                posting_score = platform_specific.get('posting_score', 0)
                st.metric("Content Score", f"{posting_score:.1f}/10")
            
            # Posting tips
            posting_tips = platform_specific.get('posting_tips', [])
            if posting_tips:
                st.info(f"💡 **Tip:** {posting_tips[0]}")
            
            # Action buttons
            st.markdown("**Actions:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📤 Post Now", key=f"post_now_{platform}_{hash(content_text)}", type="primary"):
                    ZenAltoComponents._post_immediately(platform, content)
            
            with col2:
                if st.button("📅 Schedule", key=f"schedule_{platform}_{hash(content_text)}"):
                    st.session_state[f'show_scheduler_{platform}'] = True
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{platform}_{hash(content_text)}"):
                    st.session_state[f'edit_content_{platform}'] = content
            
            with col4:
                if st.button("💾 Save Draft", key=f"save_{platform}_{hash(content_text)}"):
                    ZenAltoComponents._save_as_draft(platform, content)
            
            # Show scheduler if requested
            if st.session_state.get(f'show_scheduler_{platform}'):
                ZenAltoComponents._render_content_scheduler(platform, content)
    
    @staticmethod
    def _render_content_scheduler(platform: str, content: Dict[str, Any]) -> None:
        """
        Render inline content scheduler for specific platform and content.
        
        Args:
            platform: Platform identifier
            content: Content to schedule
        """
        with st.expander("📅 Schedule This Post", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_date = st.date_input(
                    f"Date for {platform.title()}", 
                    value=datetime.now().date() + timedelta(days=1),
                    key=f"schedule_date_{platform}"
                )
            
            with col2:
                schedule_time = st.time_input(
                    f"Time for {platform.title()}", 
                    value=datetime.now().time(),
                    key=f"schedule_time_{platform}"
                )
            
            # Combine date and time
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            
            # Show optimal posting times suggestion
            st.info(f"💡 **Optimal times for {platform.title()}:** 9:00 AM, 1:00 PM, 3:00 PM")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Schedule Post", key=f"confirm_schedule_{platform}"):
                    ZenAltoComponents._schedule_content(platform, content, schedule_datetime)
                    st.session_state[f'show_scheduler_{platform}'] = False
                    st.success(f"Post scheduled for {platform.title()} on {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", key=f"cancel_schedule_{platform}"):
                    st.session_state[f'show_scheduler_{platform}'] = False
                    st.rerun()
    
    @staticmethod
    def render_analytics_chart(data: Dict[str, Any], chart_type: str = "line") -> None:
        """
        Render analytics chart with Plotly for interactive visualization.
        
        Args:
            data: Chart data with dates, values, labels
            chart_type: Chart type (line, bar, pie)
        """
        if not data or not data.get('values'):
            st.warning("No data available for chart")
            return
        
        try:
            if chart_type == "line":
                fig = px.line(
                    x=data.get('dates', list(range(len(data['values'])))),
                    y=data.get('values', []),
                    title=data.get('title', 'Analytics Chart'),
                    labels={'x': 'Date', 'y': data.get('metric', 'Value')}
                )
                fig.update_traces(mode='lines+markers')
            
            elif chart_type == "bar":
                fig = px.bar(
                    x=data.get('categories', list(range(len(data['values'])))),
                    y=data.get('values', []),
                    title=data.get('title', 'Analytics Chart'),
                    labels={'x': 'Category', 'y': data.get('metric', 'Value')}
                )
            
            elif chart_type == "pie":
                fig = px.pie(
                    values=data.get('values', []),
                    names=data.get('labels', [f"Item {i+1}" for i in range(len(data['values']))]),
                    title=data.get('title', 'Analytics Chart')
                )
            
            else:
                st.error(f"Unsupported chart type: {chart_type}")
                return
            
            # Customize appearance
            fig.update_layout(
                template="plotly_white",
                height=400,
                title_x=0.5,
                font=dict(size=12),
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            # Add hover data
            if chart_type in ["line", "bar"]:
                fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>")
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering chart: {str(e)}")
    
    @staticmethod
    def render_campaign_card(campaign: Dict[str, Any]) -> None:
        """
        Render campaign management card with status, metrics, and actions.
        
        Args:
            campaign: Campaign data with name, status, metrics
        """
        with st.container():
            # Campaign header
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {campaign.get('name', 'Untitled Campaign')}")
                description = campaign.get('description', 'No description available')
                if len(description) > 100:
                    description = description[:100] + "..."
                st.caption(description)
            
            with col2:
                status = campaign.get('status', 'draft')
                status_colors = {
                    'active': ('🟢', 'success'),
                    'scheduled': ('🟡', 'info'),
                    'completed': ('✅', 'success'),
                    'paused': ('⏸️', 'warning'),
                    'draft': ('📝', 'warning')
                }
                icon, color = status_colors.get(status, ('❓', 'error'))
                
                if color == 'success':
                    st.success(f"{icon} {status.title()}")
                elif color == 'info':
                    st.info(f"{icon} {status.title()}")
                elif color == 'warning':
                    st.warning(f"{icon} {status.title()}")
                else:
                    st.error(f"{icon} {status.title()}")
            
            with col3:
                if st.button("⚙️ Manage", key=f"manage_campaign_{campaign.get('id', 'unknown')}"):
                    st.session_state['selected_campaign'] = campaign
            
            # Campaign metrics
            if campaign.get('metrics'):
                metrics = campaign['metrics']
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Posts", metrics.get('total_posts', 0))
                with col2:
                    reach = metrics.get('total_reach', 0)
                    st.metric("Reach", f"{reach:,}" if reach >= 1000 else str(reach))
                with col3:
                    engagement_rate = metrics.get('engagement_rate', 0)
                    st.metric("Engagement", f"{engagement_rate:.1%}")
                with col4:
                    budget_used = metrics.get('budget_used', 0)
                    budget_total = metrics.get('budget_total', 0)
                    if budget_total > 0:
                        st.metric("Budget", f"${budget_used:.0f}/${budget_total:.0f}")
                    else:
                        st.metric("Budget", f"${budget_used:.0f}")
            
            # Campaign timeline (if available)
            if campaign.get('start_date') or campaign.get('end_date'):
                timeline_info = []
                if campaign.get('start_date'):
                    timeline_info.append(f"Started: {campaign['start_date']}")
                if campaign.get('end_date'):
                    timeline_info.append(f"Ends: {campaign['end_date']}")
                st.caption(" | ".join(timeline_info))
    
    @staticmethod
    def render_content_calendar(posts: List[Dict[str, Any]], date_range: tuple) -> None:
        """
        Render interactive content calendar view with scheduled posts.
        
        Args:
            posts: List of scheduled posts
            date_range: Date range tuple (start_date, end_date)
        """
        if not posts:
            st.info("📅 No scheduled posts in the selected date range")
            return
        
        start_date, end_date = date_range
        
        # Calendar header
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous Week", key="cal_prev_week"):
                # Update date range (this would be handled by parent component)
                pass
        
        with col2:
            st.markdown(f"<h4 style='text-align: center;'>{start_date.strftime('%B %Y')}</h4>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Next Week →", key="cal_next_week"):
                # Update date range (this would be handled by parent component)
                pass
        
        # Calendar grid
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Generate week days
        current_date = start_date
        week_days = []
        for i in range(7):
            week_days.append(current_date + timedelta(days=i))
        
        # Create calendar columns
        day_columns = st.columns(7)
        
        for i, (day_name, day_date) in enumerate(zip(days, week_days)):
            with day_columns[i]:
                # Day header
                is_today = day_date == datetime.now().date()
                day_style = "background-color: #e3f2fd;" if is_today else ""
                
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 5px; {day_style} border-radius: 5px;">
                        <strong>{day_name[:3]}</strong><br>
                        <span style="font-size: 1.2em;">{day_date.day}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Posts for this day
                day_posts = [
                    post for post in posts 
                    if post.get('scheduled_date', '').startswith(str(day_date))
                ]
                
                if day_posts:
                    for post in day_posts:
                        with st.container():
                            platform = post.get('platform', 'Unknown')
                            platform_icons = {
                                'twitter': '🐦', 'linkedin': '💼', 'instagram': '📸',
                                'facebook': '👥', 'youtube': '📺'
                            }
                            icon = platform_icons.get(platform.lower(), '📱')
                            
                            time_str = post.get('scheduled_time', '').split(' ')[-1][:5] if post.get('scheduled_time') else ''
                            
                            st.markdown(
                                f"""
                                <div style="
                                    background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
                                    border-radius: 8px;
                                    padding: 8px;
                                    margin: 4px 0;
                                    border-left: 3px solid #ff9800;
                                    font-size: 0.85em;
                                ">
                                    <div><strong>{icon} {platform.title()}</strong></div>
                                    <div>{time_str}</div>
                                    <div style="color: #666;">{post.get('title', 'Post')[:20]}...</div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                            
                            if st.button("👁️ View", key=f"view_post_{post.get('id', i)}", help="View post details"):
                                st.session_state['selected_post'] = post
                else:
                    st.markdown(
                        """
                        <div style="
                            height: 60px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #ccc;
                            font-style: italic;
                        ">
                            No posts
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
    
    @staticmethod
    def _connect_platform(platform_id: str) -> None:
        """
        Mock platform connection (in production, this would redirect to OAuth flow).
        
        Args:
            platform_id: Platform identifier to connect
        """
        st.info(f"🔗 Initiating connection to {platform_id.title()}...")
        
        # Mock successful connection
        if platform_id not in st.session_state.platform_connections:
            st.session_state.platform_connections[platform_id] = {
                'connected': True,
                'connected_at': datetime.now().isoformat(),
                'posts_this_month': 0,
                'avg_engagement': 0.035,  # 3.5% default engagement rate
                'last_post_date': 'Never',
                'access_token': f'mock_token_{platform_id}',
                'user_id': f'mock_user_{platform_id}'
            }
        
        st.success(f"✅ Successfully connected to {platform_id.title()}!")
        st.rerun()
    
    @staticmethod
    def _disconnect_platform(platform_id: str) -> None:
        """
        Disconnect from a social media platform.
        
        Args:
            platform_id: Platform identifier to disconnect
        """
        if platform_id in st.session_state.platform_connections:
            del st.session_state.platform_connections[platform_id]
        
        st.success(f"🔓 Disconnected from {platform_id.title()}")
        st.rerun()
    
    @staticmethod
    def _post_immediately(platform: str, content: Dict[str, Any]) -> None:
        """
        Mock immediate posting to platform (in production, would use social media APIs).
        
        Args:
            platform: Platform identifier
            content: Content to post
        """
        # Mock posting delay
        with st.spinner(f"Posting to {platform.title()}..."):
            import time
            time.sleep(1)  # Simulate API call delay
        
        st.success(f"🚀 Posted to {platform.title()}!")
        
        # Update platform stats
        if platform in st.session_state.platform_connections:
            st.session_state.platform_connections[platform]['posts_this_month'] += 1
            st.session_state.platform_connections[platform]['last_post_date'] = datetime.now().isoformat()
        
        # Add to content history
        if 'content_history' not in st.session_state:
            st.session_state.content_history = []
        
        st.session_state.content_history.append({
            'platform': platform,
            'content': content,
            'posted_at': datetime.now().isoformat(),
            'status': 'posted'
        })
    
    @staticmethod
    def _schedule_content(platform: str, content: Dict[str, Any], schedule_datetime: datetime) -> None:
        """
        Schedule content for later posting.
        
        Args:
            platform: Platform identifier
            content: Content to schedule
            schedule_datetime: When to post the content
        """
        if 'scheduled_posts' not in st.session_state:
            st.session_state.scheduled_posts = []
        
        scheduled_post = {
            'id': f"scheduled_{platform}_{int(schedule_datetime.timestamp())}",
            'platform': platform,
            'content': content,
            'scheduled_date': schedule_datetime.date().isoformat(),
            'scheduled_time': schedule_datetime.time().isoformat(),
            'scheduled_datetime': schedule_datetime.isoformat(),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        st.session_state.scheduled_posts.append(scheduled_post)
        
        # Sort scheduled posts by datetime
        st.session_state.scheduled_posts.sort(key=lambda x: x['scheduled_datetime'])
    
    @staticmethod
    def _save_as_draft(platform: str, content: Dict[str, Any]) -> None:
        """
        Save content as draft for later editing and posting.
        
        Args:
            platform: Platform identifier
            content: Content to save as draft
        """
        if 'content_drafts' not in st.session_state:
            st.session_state.content_drafts = []
        
        draft = {
            'id': f"draft_{platform}_{int(datetime.now().timestamp())}",
            'platform': platform,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        st.session_state.content_drafts.append(draft)
        st.success(f"💾 Content saved as draft for {platform.title()}")