# ZENALTO Integration Assignment #3: UI Enhancement

## Objective
Enhance the existing Streamlit UI to support ZENALTO social media management features while preserving all existing DeepCode functionality and maintaining a unified user experience.

## Background
The current Streamlit UI in `ui/streamlit_app.py` is designed for research-to-code workflows. We need to extend it to support social media content creation, platform management, and analytics while keeping the interface intuitive and not overwhelming existing users.

## Key Requirements

### 1. Preserve Existing UI
- **Critical**: All existing DeepCode functionality must remain accessible
- Current research paper upload and code generation flows unchanged
- Maintain existing navigation and user experience patterns
- No breaking changes to existing user workflows

### 2. Add ZENALTO Features
- Chat-driven social media content creation interface
- Multi-platform connection management
- Content scheduling and calendar view
- Real-time analytics dashboard
- Campaign management tools

### 3. Unified Experience
- Seamless mode switching between DeepCode and ZENALTO
- Consistent design language and styling
- Shared components and utilities where possible
- Intelligent workflow detection and guidance

## UI Component Implementation

### 1. Enhanced Main Layout

**File**: `ui/layout.py` (Enhanced)

```python
"""
Enhanced Layout for DeepCode/ZENALTO Unified Interface

Supports both research-to-code (DeepCode) and social media management (ZENALTO) workflows
with intelligent mode detection and seamless switching.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from ui.components import (
    render_mode_selector,
    render_deepcode_interface,
    render_zenalto_interface,
    render_platform_status,
    render_analytics_summary
)
from utils.session_manager import SessionManager
from workflows.agent_orchestration_engine import AgentOrchestrationEngine

class EnhancedLayout:
    def __init__(self):
        self.session_manager = SessionManager()
        self.orchestration_engine = AgentOrchestrationEngine()
        
    def render_main_layout(self):
        """Enhanced main layout with mode detection and switching"""
        
        # Initialize session state
        self._initialize_session_state()
        
        # Render header with mode selector
        self._render_header()
        
        # Render main content based on selected mode
        if st.session_state.get('app_mode') == 'zenalto':
            self._render_zenalto_mode()
        elif st.session_state.get('app_mode') == 'deepcode':
            self._render_deepcode_mode()
        elif st.session_state.get('app_mode') == 'hybrid':
            self._render_hybrid_mode()
        else:
            # Auto-detect based on user input
            self._render_auto_detect_mode()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state with both DeepCode and ZENALTO variables"""
        
        # Existing DeepCode session state
        if 'deepcode_initialized' not in st.session_state:
            st.session_state.deepcode_initialized = True
            st.session_state.research_papers = []
            st.session_state.generated_code = {}
            st.session_state.implementation_history = []
        
        # New ZENALTO session state
        if 'zenalto_initialized' not in st.session_state:
            st.session_state.zenalto_initialized = True
            st.session_state.platform_connections = {}
            st.session_state.content_history = []
            st.session_state.scheduled_posts = []
            st.session_state.analytics_data = {}
            st.session_state.chat_history = []
        
        # Shared session state
        if 'app_mode' not in st.session_state:
            st.session_state.app_mode = 'auto'  # auto, deepcode, zenalto, hybrid
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {}
    
    def _render_header(self):
        """Render enhanced header with mode selector and status indicators"""
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("🧬 DeepCode & 📱 ZenAlto")
            st.caption("AI Research Engine & Social Media Management Platform")
        
        with col2:
            # Mode selector
            mode = st.selectbox(
                "Mode",
                options=['auto', 'deepcode', 'zenalto', 'hybrid'],
                index=['auto', 'deepcode', 'zenalto', 'hybrid'].index(st.session_state.app_mode),
                help="Choose your workflow mode or let AI auto-detect"
            )
            st.session_state.app_mode = mode
        
        with col3:
            # Status indicators
            if st.session_state.app_mode in ['zenalto', 'hybrid', 'auto']:
                self._render_platform_status_indicator()
    
    def _render_platform_status_indicator(self):
        """Render quick platform connection status"""
        
        platforms = ['twitter', 'linkedin', 'instagram']
        connected_count = sum(1 for platform in platforms 
                            if st.session_state.platform_connections.get(platform, {}).get('connected', False))
        
        if connected_count > 0:
            st.success(f"🔗 {connected_count}/{len(platforms)} Connected")
        else:
            st.warning("🔗 No Platforms Connected")
    
    def _render_zenalto_mode(self):
        """Render ZENALTO social media management interface"""
        
        st.header("📱 ZenAlto - Social Media Management")
        
        # Create tabs for different ZENALTO features
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Chat Creation", 
            "🔗 Platforms", 
            "📅 Scheduler", 
            "📊 Analytics", 
            "🎯 Campaigns"
        ])
        
        with tab1:
            self._render_chat_creation_interface()
        
        with tab2:
            self._render_platform_management()
        
        with tab3:
            self._render_content_scheduler()
        
        with tab4:
            self._render_analytics_dashboard()
        
        with tab5:
            self._render_campaign_management()
    
    def _render_chat_creation_interface(self):
        """Render conversational content creation interface"""
        
        st.subheader("💬 Create Social Media Content")
        st.caption("Tell me what kind of content you want to create, and I'll help you optimize it for your platforms!")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            if st.session_state.chat_history:
                for i, message in enumerate(st.session_state.chat_history[-10:]):  # Show last 10 messages
                    if message['role'] == 'user':
                        with st.chat_message("user"):
                            st.write(message['content'])
                    else:
                        with st.chat_message("assistant"):
                            st.write(message['content'])
                            if 'generated_content' in message:
                                self._render_generated_content_preview(message['generated_content'])
        
        # Input area
        user_input = st.chat_input("What content would you like to create?")
        
        if user_input:
            # Add user message to chat
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Process request through ZENALTO workflow
            with st.spinner("Creating your content..."):
                result = self._process_zenalto_request(user_input)
            
            # Add assistant response
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result.get('summary', 'Content created successfully!'),
                'generated_content': result.get('content', {}),
                'timestamp': datetime.now().isoformat()
            })
            
            st.rerun()
    
    def _render_generated_content_preview(self, generated_content: Dict[str, Any]):
        """Render preview of generated content with post/schedule options"""
        
        st.write("**Generated Content:**")
        
        # Platform tabs for content preview
        platform_content = generated_content.get('platform_content', {})
        
        if platform_content:
            platform_tabs = st.tabs([platform.title() for platform in platform_content.keys()])
            
            for i, (platform, content) in enumerate(platform_content.items()):
                with platform_tabs[i]:
                    st.write(f"**{platform.title()} Post:**")
                    st.write(content.get('text', ''))
                    
                    if content.get('hashtags'):
                        st.write(f"**Hashtags:** {' '.join(content['hashtags'])}")
                    
                    # Platform-specific metrics
                    platform_specific = content.get('platform_specific', {})
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Character Count", 
                            platform_specific.get('character_count', 0)
                        )
                    
                    with col2:
                        engagement = platform_specific.get('estimated_engagement', {})
                        st.metric(
                            "Est. Engagement", 
                            f"{engagement.get('estimated_rate', 0):.1%}"
                        )
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📤 Post Now", key=f"post_{platform}_{i}"):
                            self._post_content_immediately(platform, content)
                    
                    with col2:
                        if st.button(f"📅 Schedule", key=f"schedule_{platform}_{i}"):
                            st.session_state[f'scheduling_{platform}'] = True
                    
                    with col3:
                        if st.button(f"✏️ Edit", key=f"edit_{platform}_{i}"):
                            st.session_state[f'editing_{platform}'] = content
                    
                    # Scheduling interface (if triggered)
                    if st.session_state.get(f'scheduling_{platform}'):
                        with st.expander("📅 Schedule Post", expanded=True):
                            schedule_date = st.date_input(f"Date for {platform}")
                            schedule_time = st.time_input(f"Time for {platform}")
                            
                            if st.button(f"Confirm Schedule for {platform}"):
                                self._schedule_content(platform, content, schedule_date, schedule_time)
                                st.session_state[f'scheduling_{platform}'] = False
                                st.success(f"Post scheduled for {platform}!")
                                st.rerun()
    
    def _render_platform_management(self):
        """Render platform connection and management interface"""
        
        st.subheader("🔗 Platform Connections")
        
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
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                
                with col1:
                    st.write(f"## {config['icon']}")
                
                with col2:
                    st.write(f"**{config['name']}**")
                    
                    # Connection status
                    is_connected = st.session_state.platform_connections.get(platform_id, {}).get('connected', False)
                    if is_connected:
                        st.success("✅ Connected")
                        # Show last activity
                        last_post = st.session_state.platform_connections[platform_id].get('last_post_time')
                        if last_post:
                            st.caption(f"Last post: {last_post}")
                    else:
                        st.error("❌ Not Connected")
                
                with col3:
                    st.write("**Features:**")
                    st.write(" • ".join(config['features']))
                
                with col4:
                    if is_connected:
                        if st.button("⚙️ Manage", key=f"manage_{platform_id}"):
                            self._show_platform_settings(platform_id)
                        
                        if st.button("🔓 Disconnect", key=f"disconnect_{platform_id}"):
                            self._disconnect_platform(platform_id)
                    else:
                        if st.button("🔗 Connect", key=f"connect_{platform_id}"):
                            self._initiate_platform_connection(platform_id)
                
                st.divider()
    
    def _render_content_scheduler(self):
        """Render content scheduling and calendar interface"""
        
        st.subheader("📅 Content Scheduler")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_platforms = st.multiselect(
                "Filter by Platform",
                options=['twitter', 'linkedin', 'instagram', 'facebook', 'youtube'],
                default=[]
            )
        
        with col2:
            date_range = st.date_input(
                "Date Range",
                value=[datetime.now().date(), (datetime.now() + timedelta(days=7)).date()],
                help="Select date range to view scheduled posts"
            )
        
        with col3:
            view_mode = st.radio(
                "View",
                options=['Calendar', 'List'],
                horizontal=True
            )
        
        # Scheduled posts display
        scheduled_posts = self._get_scheduled_posts(selected_platforms, date_range)
        
        if view_mode == 'Calendar':
            self._render_calendar_view(scheduled_posts)
        else:
            self._render_list_view(scheduled_posts)
        
        # Quick schedule new content
        with st.expander("📝 Quick Schedule New Content"):
            self._render_quick_scheduler()
    
    def _render_analytics_dashboard(self):
        """Render analytics and performance dashboard"""
        
        st.subheader("📊 Analytics Dashboard")
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.date_input(
                "Analytics Period",
                value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
                help="Select period for analytics data"
            )
        
        with col2:
            selected_platforms = st.multiselect(
                "Platforms",
                options=['twitter', 'linkedin', 'instagram', 'facebook', 'youtube'],
                default=['twitter', 'linkedin']
            )
        
        if selected_platforms:
            # Overview metrics
            self._render_analytics_overview(selected_platforms, date_range)
            
            # Detailed analytics tabs
            tab1, tab2, tab3 = st.tabs(["📈 Performance", "👥 Audience", "🔍 Content Analysis"])
            
            with tab1:
                self._render_performance_analytics(selected_platforms, date_range)
            
            with tab2:
                self._render_audience_analytics(selected_platforms, date_range)
            
            with tab3:
                self._render_content_analytics(selected_platforms, date_range)
        else:
            st.info("Select platforms to view analytics")
    
    def _render_deepcode_mode(self):
        """Render existing DeepCode research-to-code interface"""
        
        st.header("🧬 DeepCode - AI Research Engine")
        
        # Import and render existing DeepCode interface
        from ui.components import render_deepcode_interface
        render_deepcode_interface()
    
    def _process_zenalto_request(self, user_input: str) -> Dict[str, Any]:
        """Process user request through ZENALTO workflow"""
        
        try:
            # Prepare input data
            input_data = {
                'user_request': user_input,
                'workflow_mode': 'zenalto',
                'context': {
                    'chat_history': st.session_state.chat_history[-5:],  # Last 5 messages
                    'user_preferences': st.session_state.user_preferences
                },
                'platform_context': st.session_state.platform_connections
            }
            
            # Process through orchestration engine
            result = asyncio.run(
                self.orchestration_engine.process_request(input_data)
            )
            
            # Store content in history
            if 'content' in result:
                st.session_state.content_history.append({
                    'request': user_input,
                    'content': result['content'],
                    'created_at': datetime.now().isoformat()
                })
            
            return {
                'summary': self._generate_response_summary(result),
                'content': result.get('content', {}),
                'success': True
            }
            
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            return {
                'summary': f"Sorry, I encountered an error: {str(e)}",
                'content': {},
                'success': False
            }
```

### 2. Enhanced Components

**File**: `ui/components/zenalto_components.py` (New)

```python
"""
ZenAlto-specific UI components for social media management features
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class ZenAltoComponents:
    
    @staticmethod
    def render_platform_connection_card(platform_id: str, config: Dict[str, Any]) -> None:
        """Render individual platform connection card"""
        
        is_connected = st.session_state.platform_connections.get(platform_id, {}).get('connected', False)
        
        with st.container():
            # Platform header with status
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.write(config['icon'])
            
            with col2:
                st.write(f"**{config['name']}**")
                if is_connected:
                    st.success("Connected ✅")
                else:
                    st.error("Not Connected ❌")
            
            with col3:
                if is_connected:
                    if st.button("Disconnect", key=f"disconnect_{platform_id}"):
                        ZenAltoComponents._disconnect_platform(platform_id)
                else:
                    if st.button("Connect", key=f"connect_{platform_id}"):
                        ZenAltoComponents._connect_platform(platform_id)
            
            # Platform features and stats
            if is_connected:
                connection_data = st.session_state.platform_connections[platform_id]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Posts This Month", connection_data.get('posts_this_month', 0))
                with col2:
                    st.metric("Avg. Engagement", f"{connection_data.get('avg_engagement', 0):.1%}")
                with col3:
                    st.metric("Last Post", connection_data.get('last_post_date', 'Never'))
    
    @staticmethod
    def render_content_preview_card(content: Dict[str, Any], platform: str) -> None:
        """Render content preview with actions"""
        
        with st.container():
            # Content preview
            st.write(f"**{platform.title()} Post:**")
            
            # Text content
            content_text = content.get('text', '')
            if len(content_text) > 200:
                st.write(content_text[:200] + "...")
                with st.expander("Show full content"):
                    st.write(content_text)
            else:
                st.write(content_text)
            
            # Hashtags
            hashtags = content.get('hashtags', [])
            if hashtags:
                st.write("**Hashtags:**", " ".join(hashtags))
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            
            platform_specific = content.get('platform_specific', {})
            with col1:
                st.metric("Characters", platform_specific.get('character_count', 0))
            
            with col2:
                engagement = platform_specific.get('estimated_engagement', {})
                st.metric("Est. Engagement", f"{engagement.get('estimated_rate', 0):.1%}")
            
            with col3:
                posting_tips = platform_specific.get('posting_tips', [])
                if posting_tips:
                    st.info(f"💡 {posting_tips[0]}")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📤 Post Now", key=f"post_now_{platform}_{hash(content_text)}"):
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
    
    @staticmethod
    def render_analytics_chart(data: Dict[str, Any], chart_type: str = "line") -> None:
        """Render analytics chart with Plotly"""
        
        if chart_type == "line":
            fig = px.line(
                x=data.get('dates', []),
                y=data.get('values', []),
                title=data.get('title', 'Analytics'),
                labels={'x': 'Date', 'y': data.get('metric', 'Value')}
            )
        
        elif chart_type == "bar":
            fig = px.bar(
                x=data.get('categories', []),
                y=data.get('values', []),
                title=data.get('title', 'Analytics')
            )
        
        elif chart_type == "pie":
            fig = px.pie(
                values=data.get('values', []),
                names=data.get('labels', []),
                title=data.get('title', 'Analytics')
            )
        
        # Customize appearance
        fig.update_layout(
            template="plotly_white",
            height=400,
            title_x=0.5
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_campaign_card(campaign: Dict[str, Any]) -> None:
        """Render campaign management card"""
        
        with st.container():
            # Campaign header
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{campaign.get('name', 'Untitled Campaign')}**")
                st.caption(campaign.get('description', ''))
            
            with col2:
                status = campaign.get('status', 'draft')
                if status == 'active':
                    st.success("🟢 Active")
                elif status == 'scheduled':
                    st.info("🟡 Scheduled")
                elif status == 'completed':
                    st.success("✅ Completed")
                else:
                    st.warning("📝 Draft")
            
            with col3:
                if st.button("⚙️ Manage", key=f"manage_campaign_{campaign.get('id')}"):
                    st.session_state['selected_campaign'] = campaign
            
            # Campaign metrics
            if campaign.get('metrics'):
                col1, col2, col3, col4 = st.columns(4)
                
                metrics = campaign['metrics']
                with col1:
                    st.metric("Posts", metrics.get('total_posts', 0))
                with col2:
                    st.metric("Reach", f"{metrics.get('total_reach', 0):,}")
                with col3:
                    st.metric("Engagement", f"{metrics.get('engagement_rate', 0):.1%}")
                with col4:
                    st.metric("Budget", f"${metrics.get('budget_used', 0):.0f}")
    
    @staticmethod
    def render_content_calendar(posts: List[Dict[str, Any]], date_range: tuple) -> None:
        """Render interactive content calendar"""
        
        # Create calendar grid
        start_date, end_date = date_range
        current_date = start_date
        
        st.write("**Content Calendar**")
        
        # Calendar navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous Week"):
                # Logic to navigate to previous week
                pass
        
        with col2:
            st.write(f"**{start_date.strftime('%B %Y')}**")
        
        with col3:
            if st.button("Next Week →"):
                # Logic to navigate to next week
                pass
        
        # Calendar grid (simplified 7-day view)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        
        for i, day in enumerate(days):
            with cols[i]:
                st.write(f"**{day}**")
                
                # Show posts for this day
                day_posts = [post for post in posts 
                           if post.get('scheduled_date', '').startswith(f"{current_date + timedelta(days=i)}")]
                
                for post in day_posts:
                    with st.container():
                        st.write(f"🔸 {post.get('platform', '').title()}")
                        st.caption(post.get('title', 'Untitled')[:30] + "...")
                        
                        if st.button("View", key=f"view_post_{post.get('id')}"):
                            st.session_state['selected_post'] = post
    
    @staticmethod
    def _connect_platform(platform_id: str) -> None:
        """Initiate OAuth connection flow for platform"""
        st.info(f"Connecting to {platform_id}...")
        # In production, this would redirect to OAuth flow
        
        # Mock connection for demo
        if platform_id not in st.session_state.platform_connections:
            st.session_state.platform_connections[platform_id] = {
                'connected': True,
                'connected_at': datetime.now().isoformat(),
                'posts_this_month': 0,
                'avg_engagement': 0.0,
                'last_post_date': 'Never'
            }
        
        st.success(f"Successfully connected to {platform_id}!")
        st.rerun()
    
    @staticmethod
    def _disconnect_platform(platform_id: str) -> None:
        """Disconnect platform"""
        if platform_id in st.session_state.platform_connections:
            del st.session_state.platform_connections[platform_id]
        
        st.success(f"Disconnected from {platform_id}")
        st.rerun()
    
    @staticmethod
    def _post_immediately(platform: str, content: Dict[str, Any]) -> None:
        """Post content immediately to platform"""
        # In production, this would call the social media MCP server
        st.success(f"Posted to {platform}! 🚀")
        
        # Update platform stats
        if platform in st.session_state.platform_connections:
            st.session_state.platform_connections[platform]['posts_this_month'] += 1
            st.session_state.platform_connections[platform]['last_post_date'] = datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def _save_as_draft(platform: str, content: Dict[str, Any]) -> None:
        """Save content as draft"""
        if 'content_drafts' not in st.session_state:
            st.session_state.content_drafts = []
        
        draft = {
            'platform': platform,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'id': len(st.session_state.content_drafts)
        }
        
        st.session_state.content_drafts.append(draft)
        st.success("Saved as draft! 💾")
```

## Testing Requirements

### 1. UI Component Tests
```python
# Test mode switching
def test_mode_switching():
    # Test switching between DeepCode and ZENALTO modes
    # Verify all UI elements render correctly
    # Ensure no session state conflicts
    pass

# Test chat interface
def test_chat_interface():
    # Test chat input handling
    # Test content generation workflow
    # Test content preview rendering
    pass

# Test platform management
def test_platform_management():
    # Test connection/disconnection flows
    # Test platform status updates
    # Test OAuth integration (mocked)
    pass
```

### 2. Integration Tests
```python
# Test full ZENALTO workflow through UI
def test_full_zenalto_workflow():
    # Test: Chat input → Content generation → Platform posting
    # Verify all steps work through UI
    pass

# Test backward compatibility
def test_deepcode_compatibility():
    # Ensure all existing DeepCode UI functions work
    # Test research paper upload flow
    # Test code generation workflow
    pass
```

## Success Criteria
- [ ] All existing DeepCode UI functionality preserved
- [ ] ZENALTO features integrate seamlessly
- [ ] Mode switching works without errors
- [ ] Chat interface provides intuitive content creation
- [ ] Platform management handles all connection states
- [ ] Analytics dashboard displays meaningful data
- [ ] Responsive design works on different screen sizes
- [ ] No performance degradation from UI enhancements

## Dependencies
- Enhanced agent orchestration (Assignment #1)
- ZENALTO agent implementations (Assignment #2)
- Social media MCP servers (Assignment #3)
- Platform authentication system (Assignment #4)

## Timeline
- **Week 1**: Enhanced main layout and mode switching
- **Week 2**: Chat interface and content creation UI
- **Week 3**: Platform management and scheduler interface
- **Week 4**: Analytics dashboard and testing

## Notes
- Maintain existing Streamlit patterns and styling
- Use session state efficiently to avoid performance issues
- Implement progressive disclosure to avoid overwhelming users
- Ensure mobile-friendly responsive design
- Add comprehensive error handling and user feedback