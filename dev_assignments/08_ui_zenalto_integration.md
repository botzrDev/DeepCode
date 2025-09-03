# Development Assignment #8: UI ZenAlto Integration

## Priority: 🟡 MEDIUM - Week 3

## Objective
Integrate ZenAlto social media management features into the existing Streamlit UI while preserving all DeepCode functionality. Create a unified interface that supports both research-to-code and social media workflows.

## Background
The current Streamlit interface only supports DeepCode workflows. We need to add ZenAlto features with workflow selection, platform management, and content creation interfaces.

## Deliverables

### 1. Update Main Layout
**File**: `ui/layout.py`

Add workflow mode selector and conditional rendering:

```python
import streamlit as st
from typing import Dict, Any, Optional

def render_main_layout():
    """Enhanced layout supporting both DeepCode and ZenAlto modes."""
    
    # Header with mode selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🚀 DeepCode | ZenAlto")
        st.caption("AI Research-to-Code & Social Media Management")
    
    with col2:
        # Workflow mode selector
        workflow_mode = st.selectbox(
            "Mode",
            ["🔬 Research to Code", "📱 Social Media", "🔄 Hybrid"],
            key="workflow_mode",
            help="Choose your workflow mode"
        )
    
    with col3:
        # Settings and help buttons
        col3_1, col3_2 = st.columns(2)
        with col3_1:
            if st.button("⚙️", key="settings_btn", help="Settings"):
                st.session_state.show_settings = True
        with col3_2:
            if st.button("❓", key="help_btn", help="Help"):
                st.session_state.show_help = True
    
    # Render appropriate interface based on mode
    if "Research" in workflow_mode:
        render_deepcode_interface()
    elif "Social" in workflow_mode:
        render_zenalto_interface()
    else:
        render_hybrid_interface()

def render_zenalto_interface():
    """ZenAlto social media management interface."""
    
    # Platform connection status
    render_platform_status()
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "✍️ Create", 
        "📅 Schedule", 
        "📊 Analytics",
        "🎯 Strategy",
        "📚 History"
    ])
    
    with tab1:
        render_content_creation()
    with tab2:
        render_scheduling()
    with tab3:
        render_analytics_dashboard()
    with tab4:
        render_strategy_planner()
    with tab5:
        render_post_history()
```

### 2. Platform Connection Widget
**File**: `ui/components/platform_status.py` (New)

```python
import streamlit as st
from typing import Dict, List
import asyncio

class PlatformStatusWidget:
    """Widget for displaying and managing platform connections."""
    
    PLATFORMS = {
        "twitter": {"icon": "🐦", "name": "Twitter/X", "color": "#1DA1F2"},
        "linkedin": {"icon": "💼", "name": "LinkedIn", "color": "#0077B5"},
        "instagram": {"icon": "📷", "name": "Instagram", "color": "#E4405F"},
        "facebook": {"icon": "📘", "name": "Facebook", "color": "#1877F2"},
        "youtube": {"icon": "📺", "name": "YouTube", "color": "#FF0000"}
    }
    
    def render(self):
        """Render platform connection status."""
        
        st.subheader("Platform Connections")
        
        cols = st.columns(5)
        for idx, (platform_id, platform_info) in enumerate(self.PLATFORMS.items()):
            with cols[idx]:
                status = self._get_platform_status(platform_id)
                self._render_platform_card(platform_id, platform_info, status)
    
    def _render_platform_card(self, platform_id: str, info: Dict, status: Dict):
        """Render individual platform status card."""
        
        # Container with colored border based on status
        container = st.container()
        with container:
            # Platform header
            st.markdown(f"""
                <div style="
                    padding: 10px;
                    border: 2px solid {info['color'] if status['connected'] else '#gray'};
                    border-radius: 10px;
                    text-align: center;
                ">
                    <h3>{info['icon']} {info['name']}</h3>
                """, unsafe_allow_html=True)
            
            # Connection status
            if status['connected']:
                st.success("✅ Connected", icon="✅")
                st.caption(f"@{status['username']}")
                
                # Quick stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Followers", status.get('followers', 'N/A'))
                with col2:
                    st.metric("Posts", status.get('post_count', 'N/A'))
                
                # Disconnect button
                if st.button(f"Disconnect", key=f"disconnect_{platform_id}"):
                    self._disconnect_platform(platform_id)
            else:
                st.info("Not connected")
                
                # Connect button
                if st.button(f"Connect {info['name']}", key=f"connect_{platform_id}"):
                    self._initiate_connection(platform_id)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    def _initiate_connection(self, platform: str):
        """Initiate OAuth connection flow."""
        st.session_state.connecting_platform = platform
        st.rerun()
```

### 3. Content Creation Interface
**File**: `ui/components/content_creator.py` (New)

```python
import streamlit as st
from typing import Dict, Any, List

class ContentCreatorWidget:
    """Interactive content creation interface."""
    
    def render(self):
        """Render content creation interface."""
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_content_input()
        
        with col2:
            self._render_content_options()
    
    def _render_content_input(self):
        """Render main content input area."""
        
        st.subheader("Create Content")
        
        # Content type selector
        content_type = st.radio(
            "Content Type",
            ["📝 Single Post", "🧵 Thread", "📰 Article", "🎥 Video Post"],
            horizontal=True
        )
        
        # Main content input
        if content_type == "🧵 Thread":
            self._render_thread_creator()
        else:
            content = st.text_area(
                "Content",
                placeholder="What would you like to share?",
                height=200,
                key="main_content"
            )
            
            # Character counter for platforms
            self._render_character_counter(content)
        
        # Media attachments
        st.subheader("Media Attachments")
        uploaded_files = st.file_uploader(
            "Upload images or videos",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'gif', 'mp4'],
            key="media_uploads"
        )
        
        if uploaded_files:
            self._render_media_preview(uploaded_files)
    
    def _render_thread_creator(self):
        """Special interface for creating threads."""
        
        st.info("📝 Creating a thread")
        
        # Dynamic thread posts
        if 'thread_posts' not in st.session_state:
            st.session_state.thread_posts = [""]
        
        for idx, post in enumerate(st.session_state.thread_posts):
            st.text_area(
                f"Tweet {idx + 1}",
                value=post,
                height=100,
                key=f"thread_post_{idx}",
                max_chars=280
            )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ Add Tweet"):
                st.session_state.thread_posts.append("")
                st.rerun()
        with col2:
            if len(st.session_state.thread_posts) > 1:
                if st.button("➖ Remove Last"):
                    st.session_state.thread_posts.pop()
                    st.rerun()
    
    def _render_content_options(self):
        """Render content configuration options."""
        
        st.subheader("Options")
        
        # Platform selection
        st.multiselect(
            "Publish to",
            ["Twitter", "LinkedIn", "Instagram", "Facebook"],
            default=["Twitter"],
            key="target_platforms"
        )
        
        # Tone selector
        tone = st.select_slider(
            "Tone",
            options=["Professional", "Casual", "Friendly", "Humorous", "Educational"],
            value="Professional",
            key="content_tone"
        )
        
        # AI Enhancement options
        st.subheader("AI Enhancement")
        
        enhance_options = st.multiselect(
            "Enhance with AI",
            [
                "🎯 Optimize for engagement",
                "🏷️ Add hashtags",
                "😊 Add emojis",
                "✨ Polish writing",
                "🌍 Translate"
            ],
            key="ai_enhancements"
        )
        
        # Scheduling options
        st.subheader("Scheduling")
        
        schedule_option = st.radio(
            "When to publish",
            ["📤 Post now", "⏰ Schedule for later", "🎯 Optimal time"],
            key="schedule_option"
        )
        
        if schedule_option == "⏰ Schedule for later":
            col1, col2 = st.columns(2)
            with col1:
                schedule_date = st.date_input("Date", key="schedule_date")
            with col2:
                schedule_time = st.time_input("Time", key="schedule_time")
        
        # Generate/Preview buttons
        st.divider()
        
        if st.button("🤖 Generate with AI", type="primary", use_container_width=True):
            self._generate_content()
        
        if st.button("👁️ Preview", use_container_width=True):
            self._preview_content()
        
        if st.button("🚀 Publish", type="primary", use_container_width=True):
            self._publish_content()
```

### 4. Analytics Dashboard
**File**: `ui/components/analytics_dashboard.py` (New)

```python
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

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
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
```

### 5. Chat Interface Enhancement
**File**: `ui/components/chat_interface.py` (Update)

Add ZenAlto-specific chat commands:

```python
class ChatInterface:
    """Enhanced chat interface for both DeepCode and ZenAlto."""
    
    ZENALTO_COMMANDS = {
        "/post": "Create a social media post",
        "/schedule": "Schedule content",
        "/analytics": "View analytics",
        "/trending": "Check trending topics",
        "/optimize": "Optimize content for engagement"
    }
    
    def render(self):
        """Render chat interface with mode awareness."""
        
        # Detect current mode
        mode = st.session_state.get('workflow_mode', 'Research')
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            st.subheader("AI Assistant")
            
            # Show mode-specific hints
            if "Social" in mode:
                with st.expander("Quick Commands"):
                    for cmd, desc in self.ZENALTO_COMMANDS.items():
                        st.text(f"{cmd} - {desc}")
            
            # Chat messages
            for message in st.session_state.get('messages', []):
                self._render_message(message)
            
            # Input area
            user_input = st.text_input(
                "Message",
                placeholder="Ask me anything or use / commands...",
                key="chat_input"
            )
            
            if user_input:
                self._process_input(user_input, mode)
    
    def _process_input(self, input_text: str, mode: str):
        """Process user input based on mode."""
        
        if input_text.startswith("/"):
            self._handle_command(input_text, mode)
        else:
            self._handle_conversation(input_text, mode)
```

### 6. Settings Panel
**File**: `ui/components/settings.py` (Update)

Add ZenAlto-specific settings:

```python
def render_settings():
    """Render settings panel with ZenAlto options."""
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "General", "Platforms", "AI Models", "Preferences"
    ])
    
    with tab1:
        render_general_settings()
    
    with tab2:
        render_platform_settings()
    
    with tab3:
        render_ai_settings()
    
    with tab4:
        render_preference_settings()

def render_platform_settings():
    """Platform-specific settings."""
    
    st.subheader("Platform Settings")
    
    # Default platforms
    st.multiselect(
        "Default Platforms",
        ["Twitter", "LinkedIn", "Instagram", "Facebook", "YouTube"],
        default=["Twitter", "LinkedIn"],
        key="default_platforms"
    )
    
    # Platform-specific configurations
    with st.expander("Twitter Settings"):
        st.checkbox("Auto-thread long content", key="twitter_auto_thread")
        st.number_input("Default thread length", min_value=2, max_value=25, value=5)
        st.checkbox("Include hashtags", value=True)
    
    with st.expander("LinkedIn Settings"):
        st.selectbox("Default post format", ["Post", "Article", "Poll"])
        st.checkbox("Include professional signature", value=True)
    
    # Continue for other platforms...

def render_preference_settings():
    """User preferences for ZenAlto."""
    
    st.subheader("Content Preferences")
    
    # Tone preferences
    st.select_slider(
        "Default Tone",
        options=["Professional", "Casual", "Friendly", "Humorous", "Educational"],
        value="Professional"
    )
    
    # AI assistance level
    st.slider(
        "AI Assistance Level",
        min_value=0,
        max_value=100,
        value=75,
        help="How much AI help do you want?"
    )
    
    # Automation preferences
    st.subheader("Automation")
    
    st.checkbox("Auto-optimize for engagement", value=True)
    st.checkbox("Auto-suggest hashtags", value=True)
    st.checkbox("Auto-schedule to optimal times", value=False)
    st.checkbox("Auto-generate image alt text", value=True)
```

## State Management

### 1. Session State Structure

```python
# Initialize ZenAlto session state
if 'zenalto_state' not in st.session_state:
    st.session_state.zenalto_state = {
        'connected_platforms': {},
        'current_content': {},
        'scheduled_posts': [],
        'analytics_data': {},
        'ai_suggestions': [],
        'workflow_mode': 'Research to Code'
    }
```

### 2. Platform Connection State

```python
def manage_platform_state(platform: str, action: str, data: Dict = None):
    """Manage platform connection state."""
    
    if action == "connect":
        st.session_state.zenalto_state['connected_platforms'][platform] = {
            'connected': True,
            'username': data.get('username'),
            'token': data.get('token'),
            'expires': data.get('expires')
        }
    elif action == "disconnect":
        if platform in st.session_state.zenalto_state['connected_platforms']:
            del st.session_state.zenalto_state['connected_platforms'][platform]
    elif action == "refresh":
        # Refresh connection status
        pass
```

## Styling and Theme

### 1. Custom CSS

```python
def apply_zenalto_styling():
    """Apply custom styling for ZenAlto interface."""
    
    st.markdown("""
    <style>
    /* Platform cards */
    .platform-card {
        padding: 1rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .platform-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Connected status */
    .connected {
        border: 2px solid #00d26a;
        background: rgba(0, 210, 106, 0.05);
    }
    
    .disconnected {
        border: 2px solid #e0e0e0;
        background: #f5f5f5;
    }
    
    /* Content preview */
    .content-preview {
        border-left: 3px solid #1DA1F2;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    /* Analytics cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
```

## Integration Points

### 1. Backend Communication

```python
import asyncio
from workflows.agent_orchestration_engine import AgentOrchestrationEngine

async def process_zenalto_request(request_data: Dict) -> Dict:
    """Process ZenAlto request through orchestration engine."""
    
    engine = AgentOrchestrationEngine()
    
    # Add workflow mode
    request_data['workflow_mode'] = 'zenalto'
    
    # Process request
    result = await engine.process_request(request_data)
    
    return result

# Streamlit async wrapper
def handle_zenalto_action(action: str, data: Dict):
    """Handle ZenAlto actions in Streamlit."""
    
    with st.spinner(f"Processing {action}..."):
        result = asyncio.run(process_zenalto_request({
            'action': action,
            'data': data,
            'user_id': st.session_state.get('user_id')
        }))
        
        if result['success']:
            st.success(f"✅ {action} completed successfully!")
            return result
        else:
            st.error(f"❌ Error: {result.get('error')}")
            return None
```

## Testing Requirements

### 1. UI Component Tests

```python
def test_platform_status_widget():
    """Test platform status widget rendering."""
    # Test with connected platforms
    # Test with disconnected platforms
    # Test connection initiation
    pass

def test_content_creator():
    """Test content creation interface."""
    # Test single post creation
    # Test thread creation
    # Test media upload
    pass

def test_workflow_switching():
    """Test switching between DeepCode and ZenAlto."""
    # Test mode persistence
    # Test state isolation
    pass
```

## Success Criteria

- [ ] Workflow mode selector functional
- [ ] Platform connection UI working
- [ ] Content creation interface complete
- [ ] Analytics dashboard displaying data
- [ ] Chat interface supports both modes
- [ ] No regression in DeepCode features
- [ ] Responsive design on all screen sizes
- [ ] State management working correctly

## Delivery Checklist

- [ ] Updated `ui/layout.py` with mode selector
- [ ] Created platform status widget
- [ ] Created content creator widget
- [ ] Created analytics dashboard
- [ ] Updated chat interface
- [ ] Updated settings panel
- [ ] Added custom styling
- [ ] Integration with backend working
- [ ] All tests passing