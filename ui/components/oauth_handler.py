import streamlit as st
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
from auth.oauth_manager import OAuthManager


class StreamlitOAuthHandler:
    """
    OAuth handler for Streamlit UI.
    """
    
    def __init__(self):
        # Initialize OAuth manager with config from secrets
        oauth_config = {}
        if hasattr(st, 'secrets') and 'oauth' in st.secrets:
            oauth_config = dict(st.secrets.oauth)
        
        self.oauth_manager = OAuthManager(oauth_config)
    
    def render_connection_flow(self, platform: str):
        """Render OAuth connection flow in Streamlit."""
        
        # Check if we're handling a callback
        query_params = st.query_params
        
        if "code" in query_params and "state" in query_params:
            # Handle OAuth callback
            self._handle_callback(platform, query_params)
        else:
            # Initiate OAuth flow
            self._initiate_flow(platform)
    
    def render_platform_connections(self, user_id: str = "default"):
        """Render connection status for all platforms."""
        
        platforms = ["twitter", "linkedin", "instagram", "facebook", "youtube"]
        
        st.subheader("🔗 Platform Connections")
        
        col1, col2 = st.columns(2)
        
        for i, platform in enumerate(platforms):
            with col1 if i % 2 == 0 else col2:
                self._render_platform_card(platform, user_id)
    
    def _render_platform_card(self, platform: str, user_id: str):
        """Render individual platform connection card."""
        
        platform_names = {
            "twitter": "🐦 Twitter/X",
            "linkedin": "💼 LinkedIn",
            "instagram": "📸 Instagram",
            "facebook": "📘 Facebook",
            "youtube": "🎥 YouTube"
        }
        
        platform_display = platform_names.get(platform, platform.title())
        
        with st.container():
            st.markdown(f"### {platform_display}")
            
            # Check connection status
            is_connected = self._check_connection_status(user_id, platform)
            
            if is_connected:
                st.success("✅ Connected")
                
                col_info, col_disconnect = st.columns([2, 1])
                
                with col_info:
                    # Show basic connection info
                    connection_info = st.session_state.get(f"connection_info_{platform}", {})
                    if connection_info.get("user_info"):
                        user_info = connection_info["user_info"]
                        st.write(f"**User:** {user_info.get('name', user_info.get('username', 'N/A'))}")
                    
                    connected_at = connection_info.get("connected_at")
                    if connected_at:
                        st.write(f"**Connected:** {connected_at}")
                
                with col_disconnect:
                    if st.button("Disconnect", key=f"disconnect_{platform}"):
                        self._disconnect_platform(platform, user_id)
            else:
                st.error("❌ Not connected")
                
                if st.button(f"Connect {platform.title()}", key=f"connect_{platform}"):
                    self._start_oauth_flow(platform, user_id)
            
            st.markdown("---")
    
    def _initiate_flow(self, platform: str):
        """Initiate OAuth authentication flow."""
        
        st.info(f"Connect your {platform.title()} account")
        
        if st.button(f"Connect {platform.title()}", key=f"oauth_init_{platform}"):
            self._start_oauth_flow(platform, st.session_state.get("user_id", "default"))
    
    def _start_oauth_flow(self, platform: str, user_id: str):
        """Start OAuth flow for a platform."""
        
        try:
            # Get redirect URI
            redirect_uri = self._get_redirect_uri()
            
            # Initiate OAuth flow
            result = asyncio.run(
                self.oauth_manager.initiate_oauth_flow(
                    platform=platform,
                    user_id=user_id,
                    redirect_uri=redirect_uri
                )
            )
            
            if result.get("auth_url"):
                # Store state in session
                st.session_state[f"oauth_state_{platform}"] = result["state"]
                
                # Show authorization URL to user
                st.success("✅ OAuth URL generated!")
                st.markdown(f"**Click here to authorize:** [{platform.title()} OAuth]({result['auth_url']})")
                
                # In a real app, this would redirect automatically
                st.info("After authorizing, you'll be redirected back to this app.")
                
            else:
                st.error("Failed to initiate authentication")
                
        except Exception as e:
            st.error(f"Error starting OAuth flow: {str(e)}")
    
    def _handle_callback(self, platform: str, params: Dict):
        """Handle OAuth callback."""
        
        code = params.get("code")
        state = params.get("state") 
        error = params.get("error")
        
        if isinstance(code, list):
            code = code[0] if code else None
        if isinstance(state, list):
            state = state[0] if state else None
        if isinstance(error, list):
            error = error[0] if error else None
        
        # Validate state
        stored_state = st.session_state.get(f"oauth_state_{platform}")
        
        if state != stored_state:
            st.error("Invalid authentication state")
            return
        
        # Exchange code for tokens
        try:
            result = asyncio.run(
                self.oauth_manager.handle_oauth_callback(
                    platform=platform,
                    code=code,
                    state=state,
                    error=error
                )
            )
            
            if result.get("success"):
                st.success(f"Successfully connected to {platform.title()}!")
                
                # Store connection status
                if "connected_platforms" not in st.session_state:
                    st.session_state.connected_platforms = {}
                
                st.session_state.connected_platforms[platform] = True
                st.session_state[f"connection_info_{platform}"] = {
                    "connected": True,
                    "user_info": result.get("user_info", {}),
                    "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Clear OAuth state
                if f"oauth_state_{platform}" in st.session_state:
                    del st.session_state[f"oauth_state_{platform}"]
                
                # Clear query params and rerun
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"Failed to connect: {result.get('error')}")
                
        except Exception as e:
            st.error(f"Error handling OAuth callback: {str(e)}")
    
    def _disconnect_platform(self, platform: str, user_id: str):
        """Disconnect a platform."""
        
        try:
            # Revoke access
            success = asyncio.run(
                self.oauth_manager.revoke_access(user_id, platform)
            )
            
            if success:
                st.success(f"Successfully disconnected from {platform.title()}")
                
                # Update session state
                if "connected_platforms" in st.session_state:
                    st.session_state.connected_platforms[platform] = False
                
                if f"connection_info_{platform}" in st.session_state:
                    del st.session_state[f"connection_info_{platform}"]
                
                st.rerun()
            else:
                st.error(f"Failed to disconnect from {platform.title()}")
                
        except Exception as e:
            st.error(f"Error disconnecting: {str(e)}")
    
    def _check_connection_status(self, user_id: str, platform: str) -> bool:
        """Check if platform is connected."""
        
        # Check session state first
        connected_platforms = st.session_state.get("connected_platforms", {})
        if connected_platforms.get(platform):
            return True
        
        # Check stored tokens
        try:
            tokens = asyncio.run(
                self.oauth_manager.token_storage.get_tokens(user_id, platform)
            )
            
            if tokens and not tokens.get("expired"):
                # Update session state
                st.session_state.setdefault("connected_platforms", {})[platform] = True
                return True
                
        except Exception as e:
            self.oauth_manager.logger.warning(f"Error checking connection status: {e}")
        
        return False
    
    def _get_redirect_uri(self) -> str:
        """Get OAuth redirect URI."""
        # Get current URL base
        # In production, this should be your configured redirect URI
        return "http://localhost:8501"
    
    def get_platform_tokens(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """Get valid tokens for a platform."""
        
        try:
            return asyncio.run(
                self.oauth_manager.token_storage.get_tokens(user_id, platform)
            )
        except Exception as e:
            self.oauth_manager.logger.error(f"Error getting tokens: {e}")
            return None