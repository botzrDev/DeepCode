"""
Platform Status Widget for ZenAlto

Widget for displaying and managing platform connections with enhanced functionality.
"""

import streamlit as st
from typing import Dict, List
import asyncio
from datetime import datetime


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
    
    def _get_platform_status(self, platform_id: str) -> Dict:
        """Get platform connection status from session state."""
        platform_connections = st.session_state.get('platform_connections', {})
        connection_data = platform_connections.get(platform_id, {})
        
        if connection_data.get('connected', False):
            return {
                'connected': True,
                'username': connection_data.get('username', f'user_{platform_id}'),
                'followers': connection_data.get('followers', '1.2K'),
                'post_count': connection_data.get('posts_this_month', 24),
                'last_post': connection_data.get('last_post_date', 'Never')
            }
        else:
            return {
                'connected': False,
                'username': None,
                'followers': 0,
                'post_count': 0
            }
    
    def _initiate_connection(self, platform: str):
        """Initiate OAuth connection flow."""
        st.session_state.connecting_platform = platform
        
        # Mock successful connection for demo
        if 'platform_connections' not in st.session_state:
            st.session_state.platform_connections = {}
            
        st.session_state.platform_connections[platform] = {
            'connected': True,
            'connected_at': datetime.now().isoformat(),
            'username': f'demo_user_{platform}',
            'followers': '1.2K',
            'posts_this_month': 24,
            'avg_engagement': 0.045,
            'last_post_date': datetime.now().isoformat(),
            'access_token': f'mock_token_{platform}',
            'user_id': f'mock_user_{platform}'
        }
        
        st.success(f"✅ Successfully connected to {platform.title()}!")
        st.rerun()
    
    def _disconnect_platform(self, platform: str):
        """Disconnect from platform."""
        if 'platform_connections' in st.session_state:
            if platform in st.session_state.platform_connections:
                del st.session_state.platform_connections[platform]
        
        st.success(f"🔓 Disconnected from {platform.title()}")
        st.rerun()


def render_platform_status():
    """Convenience function to render platform status widget."""
    widget = PlatformStatusWidget()
    widget.render()