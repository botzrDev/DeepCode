"""
Enhanced Streamlit Layout Module for DeepCode/ZENALTO Unified Interface

Contains main page layout and flow control for both research-to-code (DeepCode) 
and social media management (ZENALTO) workflows with intelligent mode detection.
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# DeepCode components (existing - from the main components.py file)
from .components import (
    display_header,
    display_features,
    sidebar_control_panel,
    input_method_selector,
    results_display_component,
    footer_component,
)
from .handlers_simple import (
    initialize_session_state,
    handle_start_processing_button,
    handle_error_display,
)
from .styles import get_main_styles

# ZENALTO components (new - from the zenalto_ui subfolder)
from ui.zenalto_ui.zenalto_components import ZenAltoComponents


def setup_page_config():
    """Setup enhanced page configuration for DeepCode/ZENALTO"""
    st.set_page_config(
        page_title="DeepCode & ZenAlto - AI Research Engine & Social Media Management",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_custom_styles():
    """Apply custom styles"""
    st.markdown(get_main_styles(), unsafe_allow_html=True)


def initialize_enhanced_session_state():
    """Initialize enhanced session state with both DeepCode and ZENALTO variables"""
    # Initialize existing DeepCode session state
    initialize_session_state()
    
    # Initialize ZENALTO session state
    if 'zenalto_initialized' not in st.session_state:
        st.session_state.zenalto_initialized = True
        st.session_state.platform_connections = {}
        st.session_state.content_history = []
        st.session_state.scheduled_posts = []
        st.session_state.analytics_data = {}
        st.session_state.chat_history = []
        st.session_state.content_drafts = []
        st.session_state.campaigns = []
    
    # Enhanced session state for mode management
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'deepcode'  # Default to existing DeepCode mode
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}


def render_enhanced_header():
    """Render enhanced header with mode selector and status indicators"""
    # Mode selector in sidebar for better UX
    with st.sidebar:
        st.markdown("### 🎯 Mode Selection")
        mode_options = {
            'deepcode': '🧬 DeepCode - Research Engine',
            'zenalto': '📱 ZenAlto - Social Media',
            'hybrid': '🔄 Hybrid - Combined Mode'
        }
        
        selected_mode = st.selectbox(
            "Choose your workflow mode:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(st.session_state.app_mode),
            help="Select the workflow type that matches your needs"
        )
        
        # Update mode if changed
        if selected_mode != st.session_state.app_mode:
            st.session_state.app_mode = selected_mode
            st.rerun()
        
        # Show platform status for ZENALTO modes
        if st.session_state.app_mode in ['zenalto', 'hybrid']:
            st.markdown("### 🔗 Platform Status")
            render_platform_status_indicator()


def render_platform_status_indicator():
    """Render quick platform connection status in sidebar"""
    platforms = ['twitter', 'linkedin', 'instagram', 'facebook']
    connected_count = sum(1 for platform in platforms 
                        if st.session_state.platform_connections.get(platform, {}).get('connected', False))
    
    if connected_count > 0:
        st.success(f"✅ {connected_count}/{len(platforms)} Connected")
        # Show connected platforms
        for platform in platforms:
            if st.session_state.platform_connections.get(platform, {}).get('connected', False):
                platform_icons = {'twitter': '🐦', 'linkedin': '💼', 'instagram': '📸', 'facebook': '👥'}
                icon = platform_icons.get(platform, '📱')
                st.caption(f"{icon} {platform.title()}")
    else:
        st.warning("⚠️ No Platforms Connected")
        if st.session_state.app_mode == 'zenalto':
            st.info("💡 Connect platforms in the main interface")


def render_mode_appropriate_header():
    """Render header appropriate for the selected mode"""
    if st.session_state.app_mode == 'zenalto':
        st.markdown(
            """
        <div class="main-header">
            <h1>📱 ZenAlto</h1>
            <h3>AI SOCIAL MEDIA MANAGEMENT PLATFORM</h3>
            <p>⚡ CREATE • SCHEDULE • ANALYZE • OPTIMIZE ⚡</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    elif st.session_state.app_mode == 'hybrid':
        st.markdown(
            """
        <div class="main-header">
            <h1>🧬 DeepCode & 📱 ZenAlto</h1>
            <h3>UNIFIED AI RESEARCH & SOCIAL MEDIA PLATFORM</h3>
            <p>⚡ RESEARCH • CODE • CREATE • SHARE ⚡</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Default DeepCode header
        display_header()


def render_main_content():
    """Enhanced main content area with mode-based rendering"""
    # Render appropriate header
    render_mode_appropriate_header()
    
    # Mode-specific content rendering
    if st.session_state.app_mode == 'zenalto':
        render_zenalto_interface()
    elif st.session_state.app_mode == 'hybrid':
        render_hybrid_interface()
    else:
        # Default DeepCode interface (preserve existing functionality)
        render_deepcode_interface()


def render_deepcode_interface():
    """Render the original DeepCode interface (preserves all existing functionality)"""
    display_features()
    st.markdown("---")

    # Display results if available
    if st.session_state.show_results and st.session_state.last_result:
        results_display_component(
            st.session_state.last_result, st.session_state.task_counter
        )
        st.markdown("---")
        return

    # Show input interface only when not displaying results
    if not st.session_state.show_results:
        render_input_interface()

    # Display error messages if any
    handle_error_display()


def render_zenalto_interface():
    """Render ZENALTO social media management interface"""
    st.markdown("### 🎯 AI-Powered Social Media Management")
    st.caption("Create engaging content, manage multiple platforms, and analyze performance - all with AI assistance")
    
    # Create tabs for different ZENALTO features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat Creation", 
        "🔗 Platforms", 
        "📅 Scheduler", 
        "📊 Analytics", 
        "🎯 Campaigns"
    ])
    
    with tab1:
        render_chat_creation_interface()
    
    with tab2:
        render_platform_management()
    
    with tab3:
        render_content_scheduler()
    
    with tab4:
        render_analytics_dashboard()
    
    with tab5:
        render_campaign_management()


def render_hybrid_interface():
    """Render hybrid interface combining DeepCode and ZENALTO features"""
    st.markdown("### 🔄 Hybrid Mode: Research-to-Social Pipeline")
    st.caption("Analyze research content and automatically create social media posts about your findings")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🧬 Research Analysis")
        st.info("Upload research papers or enter requirements to generate insights")
        # Render simplified DeepCode interface
        render_input_interface()
    
    with col2:
        st.markdown("#### 📱 Social Media Content")
        st.info("Create posts based on research findings and technical insights")
        # Render simplified ZENALTO content creation
        render_chat_creation_interface(hybrid_mode=True)


def render_chat_creation_interface(hybrid_mode: bool = False):
    """Render conversational content creation interface"""
    if not hybrid_mode:
        st.markdown("#### 💬 Create Social Media Content")
        st.caption("Tell me what kind of content you want to create, and I'll help you optimize it for your platforms!")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display recent chat history
        if st.session_state.chat_history:
            st.markdown("**Recent Conversations:**")
            for i, message in enumerate(st.session_state.chat_history[-3:]):  # Show last 3 messages
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'][:200] + "..." if len(message['content']) > 200 else message['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        if 'generated_content' in message:
                            render_generated_content_preview(message['generated_content'])
    
    # Input area
    user_input = st.chat_input("What content would you like to create?")
    
    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process request (mock implementation)
        with st.spinner("Creating your content..."):
            result = process_zenalto_request(user_input)
        
        # Add assistant response
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': result.get('summary', 'Content created successfully!'),
            'generated_content': result.get('content', {}),
            'timestamp': datetime.now().isoformat()
        })
        
        st.rerun()


def render_generated_content_preview(generated_content: Dict[str, Any]):
    """Render preview of generated content with post/schedule options"""
    st.markdown("**Generated Content:**")
    
    # Platform tabs for content preview
    platform_content = generated_content.get('platform_content', {})
    
    if platform_content:
        platform_names = list(platform_content.keys())
        platform_tabs = st.tabs([platform.title() for platform in platform_names])
        
        for i, platform in enumerate(platform_names):
            with platform_tabs[i]:
                content = platform_content[platform]
                ZenAltoComponents.render_content_preview_card(content, platform)
    else:
        st.info("No platform-specific content generated yet")


def render_platform_management():
    """Render platform connection and management interface"""
    st.markdown("#### 🔗 Platform Connections")
    
    platforms_config = {
        'twitter': {
            'name': 'Twitter/X',
            'icon': '🐦',
            'color': '#1DA1F2',
            'features': ['Posts', 'Threads', 'Polls', 'Analytics']
        },
        'linkedin': {
            'name': 'LinkedIn',
            'icon': '💼',
            'color': '#0077B5',
            'features': ['Posts', 'Articles', 'Company Updates', 'Analytics']
        },
        'instagram': {
            'name': 'Instagram',
            'icon': '📸',
            'color': '#E4405F',
            'features': ['Posts', 'Stories', 'Reels', 'Analytics']
        },
        'facebook': {
            'name': 'Facebook',
            'icon': '👥',
            'color': '#1877F2',
            'features': ['Posts', 'Stories', 'Events', 'Analytics']
        },
        'youtube': {
            'name': 'YouTube',
            'icon': '📺',
            'color': '#FF0000',
            'features': ['Videos', 'Shorts', 'Community Posts', 'Analytics']
        }
    }
    
    # Platform connection cards
    for platform_id, config in platforms_config.items():
        with st.container():
            ZenAltoComponents.render_platform_connection_card(platform_id, config)
            st.divider()


def render_content_scheduler():
    """Render content scheduling and calendar interface"""
    st.markdown("#### 📅 Content Scheduler")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_platforms = st.multiselect(
            "Filter by Platform",
            options=['twitter', 'linkedin', 'instagram', 'facebook', 'youtube'],
            default=[],
            key="scheduler_platform_filter"
        )
    
    with col2:
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now().date(), (datetime.now() + timedelta(days=7)).date()],
            help="Select date range to view scheduled posts",
            key="scheduler_date_range"
        )
    
    with col3:
        view_mode = st.radio(
            "View Mode",
            options=['Calendar', 'List'],
            horizontal=True,
            key="scheduler_view_mode"
        )
    
    # Get scheduled posts
    scheduled_posts = get_scheduled_posts(selected_platforms, date_range)
    
    if view_mode == 'Calendar' and len(date_range) == 2:
        ZenAltoComponents.render_content_calendar(scheduled_posts, tuple(date_range))
    else:
        render_scheduled_posts_list(scheduled_posts)
    
    # Quick schedule new content
    with st.expander("📝 Quick Schedule New Content"):
        render_quick_scheduler()


def render_analytics_dashboard():
    """Render analytics and performance dashboard"""
    st.markdown("#### 📊 Analytics Dashboard")
    
    # Check if any platforms are connected
    connected_platforms = [
        platform for platform, data in st.session_state.platform_connections.items() 
        if data.get('connected', False)
    ]
    
    if not connected_platforms:
        st.warning("📊 Connect platforms to view analytics data")
        return
    
    # Date range and platform selector
    col1, col2 = st.columns(2)
    
    with col1:
        date_range = st.date_input(
            "Analytics Period",
            value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
            help="Select period for analytics data",
            key="analytics_date_range"
        )
    
    with col2:
        selected_platforms = st.multiselect(
            "Platforms",
            options=connected_platforms,
            default=connected_platforms[:2] if len(connected_platforms) >= 2 else connected_platforms,
            key="analytics_platform_filter"
        )
    
    if selected_platforms:
        # Overview metrics
        render_analytics_overview(selected_platforms, date_range)
        
        # Detailed analytics tabs
        tab1, tab2, tab3 = st.tabs(["📈 Performance", "👥 Audience", "🔍 Content Analysis"])
        
        with tab1:
            render_performance_analytics(selected_platforms, date_range)
        
        with tab2:
            render_audience_analytics(selected_platforms, date_range)
        
        with tab3:
            render_content_analytics(selected_platforms, date_range)
    else:
        st.info("Select platforms to view analytics")


def render_campaign_management():
    """Render campaign management interface"""
    st.markdown("#### 🎯 Campaign Management")
    
    # Campaign creation button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.caption("Manage your social media campaigns and track their performance")
    
    with col2:
        if st.button("➕ New Campaign", key="create_new_campaign"):
            st.session_state['creating_campaign'] = True
    
    # Show campaign creation form if requested
    if st.session_state.get('creating_campaign'):
        render_campaign_creation_form()
    
    # Display existing campaigns
    campaigns = st.session_state.get('campaigns', [])
    
    if campaigns:
        st.markdown("**Active Campaigns:**")
        for campaign in campaigns:
            ZenAltoComponents.render_campaign_card(campaign)
            st.divider()
    else:
        # Show sample campaigns for demo
        render_sample_campaigns()


def render_input_interface():
    """Render input interface (preserves original DeepCode functionality)"""
    # Get input source and type
    input_source, input_type = input_method_selector(st.session_state.task_counter)

    # Processing button
    if input_source and not st.session_state.processing:
        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
            handle_start_processing_button(input_source, input_type)

    elif st.session_state.processing:
        st.info("🔄 Processing in progress... Please wait.")
        st.warning("⚠️ Do not refresh the page or close the browser during processing.")

    elif not input_source:
        st.info("👆 Please upload a file or enter a URL to start processing.")


# Helper functions for ZENALTO interface

def process_zenalto_request(user_input: str) -> Dict[str, Any]:
    """
    Mock process user request through ZENALTO workflow.
    In production, this would integrate with the AgentOrchestrationEngine.
    """
    import time
    time.sleep(2)  # Simulate processing time
    
    # Mock generated content for different platforms
    mock_content = {
        'platform_content': {
            'twitter': {
                'text': f"Just discovered something amazing! {user_input[:100]}... What do you think? 🤔",
                'hashtags': ['AI', 'Innovation', 'Tech'],
                'platform_specific': {
                    'character_count': 150,
                    'character_limit': 280,
                    'estimated_engagement': {'estimated_rate': 0.045},
                    'posting_score': 8.5,
                    'posting_tips': ['Add engaging visuals to increase engagement']
                }
            },
            'linkedin': {
                'text': f"Insights from recent research: {user_input}. This could transform how we approach innovation in our industry. Thoughts?",
                'hashtags': ['Innovation', 'Research', 'Technology'],
                'platform_specific': {
                    'character_count': 200,
                    'character_limit': 1300,
                    'estimated_engagement': {'estimated_rate': 0.032},
                    'posting_score': 9.2,
                    'posting_tips': ['Professional tone works well on LinkedIn']
                }
            }
        }
    }
    
    return {
        'summary': f"Created social media content based on: '{user_input[:50]}...'",
        'content': mock_content,
        'success': True
    }


def get_scheduled_posts(selected_platforms: List[str], date_range: tuple) -> List[Dict[str, Any]]:
    """Get scheduled posts filtered by platforms and date range"""
    all_posts = st.session_state.get('scheduled_posts', [])
    
    # Filter by platforms if specified
    if selected_platforms:
        all_posts = [post for post in all_posts if post.get('platform') in selected_platforms]
    
    # Filter by date range if specified
    if len(date_range) == 2:
        start_date, end_date = date_range
        all_posts = [
            post for post in all_posts 
            if start_date.isoformat() <= post.get('scheduled_date', '') <= end_date.isoformat()
        ]
    
    return all_posts


def render_scheduled_posts_list(scheduled_posts: List[Dict[str, Any]]):
    """Render scheduled posts in list view"""
    if not scheduled_posts:
        st.info("📋 No scheduled posts found")
        return
    
    st.markdown(f"**{len(scheduled_posts)} Scheduled Posts:**")
    
    for i, post in enumerate(scheduled_posts):
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                platform_icons = {
                    'twitter': '🐦', 'linkedin': '💼', 'instagram': '📸',
                    'facebook': '👥', 'youtube': '📺'
                }
                icon = platform_icons.get(post.get('platform', '').lower(), '📱')
                st.markdown(f"**{icon} {post.get('platform', 'Unknown').title()}**")
                content_preview = post.get('content', {}).get('text', 'No content')[:100]
                st.caption(f"{content_preview}{'...' if len(content_preview) == 100 else ''}")
            
            with col2:
                st.text(post.get('scheduled_date', 'No date'))
            
            with col3:
                st.text(post.get('scheduled_time', 'No time'))
            
            with col4:
                if st.button("Edit", key=f"edit_scheduled_{i}"):
                    st.session_state[f'editing_post_{i}'] = post
        
        st.divider()


def render_quick_scheduler():
    """Render quick content scheduling form"""
    st.markdown("**Create and Schedule New Content:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        platform = st.selectbox(
            "Platform",
            options=['twitter', 'linkedin', 'instagram', 'facebook'],
            key="quick_schedule_platform"
        )
        
        content_text = st.text_area(
            "Content",
            placeholder="Enter your content here...",
            height=100,
            key="quick_schedule_content"
        )
    
    with col2:
        schedule_date = st.date_input(
            "Schedule Date",
            value=datetime.now().date() + timedelta(days=1),
            key="quick_schedule_date"
        )
        
        schedule_time = st.time_input(
            "Schedule Time",
            value=datetime.now().time(),
            key="quick_schedule_time"
        )
    
    if st.button("📅 Schedule Post", key="quick_schedule_submit"):
        if content_text and platform:
            content = {
                'text': content_text,
                'hashtags': [],
                'platform_specific': {
                    'character_count': len(content_text),
                    'estimated_engagement': {'estimated_rate': 0.035}
                }
            }
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
            ZenAltoComponents._schedule_content(platform, content, schedule_datetime)
            st.success(f"Content scheduled for {platform.title()} on {schedule_datetime.strftime('%Y-%m-%d at %H:%M')}!")
        else:
            st.error("Please enter content and select a platform")


def render_analytics_overview(selected_platforms: List[str], date_range: tuple):
    """Render analytics overview section with key metrics"""
    st.markdown("**Overview Metrics:**")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Posts", "24", delta="3")
    
    with col2:
        st.metric("Total Reach", "12.5K", delta="1.2K")
    
    with col3:
        st.metric("Avg. Engagement", "4.2%", delta="0.8%")
    
    with col4:
        st.metric("New Followers", "89", delta="12")


def render_performance_analytics(selected_platforms: List[str], date_range: tuple):
    """Render performance analytics with charts"""
    st.markdown("**Performance Metrics:**")
    
    # Mock data for demonstration
    mock_data = {
        'dates': [f"2024-01-{i+1:02d}" for i in range(7)],
        'values': [120, 180, 150, 220, 190, 240, 200],
        'title': 'Daily Engagement Over Time',
        'metric': 'Engagement'
    }
    
    ZenAltoComponents.render_analytics_chart(mock_data, "line")
    
    # Platform breakdown
    platform_data = {
        'categories': selected_platforms,
        'values': [45, 32, 28, 15] if len(selected_platforms) >= 4 else [50, 30, 20][:len(selected_platforms)],
        'title': 'Engagement by Platform',
        'metric': 'Engagement %'
    }
    
    ZenAltoComponents.render_analytics_chart(platform_data, "bar")


def render_audience_analytics(selected_platforms: List[str], date_range: tuple):
    """Render audience analytics"""
    st.markdown("**Audience Insights:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Demographics chart
        demo_data = {
            'labels': ['18-24', '25-34', '35-44', '45-54', '55+'],
            'values': [25, 35, 20, 15, 5],
            'title': 'Audience Age Distribution'
        }
        ZenAltoComponents.render_analytics_chart(demo_data, "pie")
    
    with col2:
        # Growth metrics
        st.markdown("**Growth Metrics:**")
        st.metric("Follower Growth", "+12%", delta="2%")
        st.metric("Engagement Rate", "4.2%", delta="0.5%")
        st.metric("Reach Growth", "+18%", delta="3%")


def render_content_analytics(selected_platforms: List[str], date_range: tuple):
    """Render content analytics"""
    st.markdown("**Content Performance:**")
    
    # Best performing content
    st.markdown("**Top Performing Posts:**")
    mock_posts = [
        {"text": "AI breakthrough in research automation 🚀", "engagement": "450 likes, 67 shares"},
        {"text": "New features in our platform 💡", "engagement": "320 likes, 45 shares"},
        {"text": "Behind the scenes development 👨‍💻", "engagement": "280 likes, 38 shares"}
    ]
    
    for i, post in enumerate(mock_posts):
        st.markdown(f"**{i+1}.** {post['text']}")
        st.caption(f"📊 {post['engagement']}")
        st.divider()


def render_campaign_creation_form():
    """Render campaign creation form"""
    with st.form("create_campaign_form"):
        st.markdown("**Create New Campaign:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name")
            campaign_description = st.text_area("Description", height=100)
        
        with col2:
            start_date = st.date_input("Start Date", value=datetime.now().date())
            end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=30))
            budget = st.number_input("Budget ($)", min_value=0, value=1000)
        
        platforms = st.multiselect("Target Platforms", 
                                 options=['twitter', 'linkedin', 'instagram', 'facebook'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Create Campaign", type="primary"):
                if campaign_name and platforms:
                    new_campaign = {
                        'id': f"campaign_{int(datetime.now().timestamp())}",
                        'name': campaign_name,
                        'description': campaign_description,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'platforms': platforms,
                        'status': 'draft',
                        'metrics': {
                            'total_posts': 0,
                            'total_reach': 0,
                            'engagement_rate': 0.0,
                            'budget_used': 0,
                            'budget_total': budget
                        }
                    }
                    
                    if 'campaigns' not in st.session_state:
                        st.session_state.campaigns = []
                    
                    st.session_state.campaigns.append(new_campaign)
                    st.session_state['creating_campaign'] = False
                    st.success(f"Campaign '{campaign_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Please provide campaign name and select at least one platform")
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state['creating_campaign'] = False
                st.rerun()


def render_sample_campaigns():
    """Render sample campaigns for demonstration"""
    st.info("No campaigns created yet. Here are some examples:")
    
    sample_campaigns = [
        {
            'id': 'sample_1',
            'name': 'AI Research Showcase',
            'description': 'Highlighting latest AI research developments and breakthroughs',
            'status': 'active',
            'metrics': {
                'total_posts': 12,
                'total_reach': 8500,
                'engagement_rate': 0.045,
                'budget_used': 250,
                'budget_total': 1000
            }
        },
        {
            'id': 'sample_2',
            'name': 'Product Launch Campaign',
            'description': 'Promoting new platform features and capabilities',
            'status': 'scheduled',
            'metrics': {
                'total_posts': 8,
                'total_reach': 5200,
                'engagement_rate': 0.038,
                'budget_used': 180,
                'budget_total': 800
            }
        }
    ]
    
    for campaign in sample_campaigns:
        ZenAltoComponents.render_campaign_card(campaign)
        st.divider()


def render_sidebar():
    """Enhanced sidebar with mode-specific controls"""
    return sidebar_control_panel()


def main_layout():
    """Enhanced main layout function supporting DeepCode and ZENALTO modes"""
    # Initialize enhanced session state
    initialize_enhanced_session_state()

    # Setup page configuration
    setup_page_config()

    # Apply custom styles
    apply_custom_styles()

    # Render enhanced header with mode selector
    render_enhanced_header()

    # Render sidebar
    sidebar_info = render_sidebar()

    # Render main content based on selected mode
    render_main_content()

    # Display footer
    footer_component()

    return sidebar_info
