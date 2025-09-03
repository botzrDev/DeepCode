"""
Settings Panel for DeepCode/ZenAlto

Enhanced settings panel with both DeepCode and ZenAlto configurations.
"""

import streamlit as st
from typing import Dict, Any


def render_settings():
    """Render settings panel with ZenAlto options."""
    
    st.header("⚙️ Settings")
    
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


def render_general_settings():
    """Render general application settings."""
    
    st.subheader("General Settings")
    
    # Application mode
    st.selectbox(
        "Default Application Mode",
        ["🧬 DeepCode - Research", "📱 ZenAlto - Social Media", "🔄 Hybrid Mode"],
        key="default_app_mode"
    )
    
    # Theme settings
    st.selectbox(
        "Theme",
        ["Dark", "Light", "Auto"],
        key="theme_setting"
    )
    
    # Language
    st.selectbox(
        "Language",
        ["English", "Spanish", "French", "German", "Chinese"],
        key="language_setting"
    )
    
    # Notification settings
    st.checkbox("Enable notifications", value=True, key="enable_notifications")
    st.checkbox("Show tips and hints", value=True, key="show_tips")


def render_platform_settings():
    """Platform-specific settings."""
    
    st.subheader("Platform Settings")
    
    # Default platforms
    default_platforms = st.multiselect(
        "Default Publishing Platforms",
        ["Twitter", "LinkedIn", "Instagram", "Facebook", "YouTube"],
        default=["Twitter", "LinkedIn"],
        key="default_platforms",
        help="Select platforms to publish to by default"
    )
    
    # Platform-specific configurations
    with st.expander("🐦 Twitter Settings"):
        st.checkbox("Auto-thread long content", key="twitter_auto_thread")
        st.number_input(
            "Default thread length", 
            min_value=2, 
            max_value=25, 
            value=5,
            key="twitter_thread_length"
        )
        st.checkbox("Include hashtags", value=True, key="twitter_include_hashtags")
        st.selectbox(
            "Default posting time",
            ["Immediate", "Optimal time", "Custom time"],
            key="twitter_posting_time"
        )
    
    with st.expander("💼 LinkedIn Settings"):
        st.selectbox(
            "Default post format", 
            ["Post", "Article", "Poll"],
            key="linkedin_post_format"
        )
        st.checkbox(
            "Include professional signature", 
            value=True,
            key="linkedin_include_signature"
        )
        st.checkbox(
            "Enable company page posting",
            key="linkedin_company_posting"
        )
    
    with st.expander("📷 Instagram Settings"):
        st.checkbox("Auto-resize images", value=True, key="instagram_auto_resize")
        st.selectbox(
            "Default aspect ratio",
            ["Square (1:1)", "Portrait (4:5)", "Landscape (16:9)"],
            key="instagram_aspect_ratio"
        )
        st.checkbox("Add location tags", key="instagram_location_tags")
    
    with st.expander("📘 Facebook Settings"):
        st.checkbox("Cross-post to Facebook Page", key="facebook_page_crosspost")
        st.selectbox(
            "Default audience",
            ["Public", "Friends", "Custom"],
            key="facebook_audience"
        )
    
    with st.expander("📺 YouTube Settings"):
        st.selectbox(
            "Default video privacy",
            ["Public", "Unlisted", "Private"],
            key="youtube_privacy"
        )
        st.checkbox("Auto-generate captions", key="youtube_auto_captions")


def render_ai_settings():
    """AI model and enhancement settings."""
    
    st.subheader("AI Model Settings")
    
    # Model selection
    st.selectbox(
        "Primary AI Model",
        ["GPT-4", "Claude-3", "Gemini Pro", "Custom"],
        key="primary_ai_model"
    )
    
    # AI enhancement preferences
    st.subheader("AI Enhancement Preferences")
    
    # Content generation settings
    st.slider(
        "Content creativity level",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        key="ai_creativity_level",
        help="Higher values = more creative, lower values = more conservative"
    )
    
    st.checkbox("Auto-optimize for engagement", value=True, key="ai_auto_optimize")
    st.checkbox("Auto-suggest hashtags", value=True, key="ai_auto_hashtags")
    st.checkbox("Auto-generate image alt text", value=True, key="ai_auto_alt_text")
    
    # Research-to-code settings (DeepCode)
    st.subheader("Research Analysis Settings")
    
    st.selectbox(
        "Code generation model",
        ["Code-focused GPT-4", "Claude-3 Code", "Codex", "Custom"],
        key="code_generation_model"
    )
    
    st.checkbox("Enable automatic testing", value=True, key="auto_testing")
    st.checkbox("Generate documentation", value=True, key="generate_docs")


def render_preference_settings():
    """User preferences for ZenAlto."""
    
    st.subheader("Content Preferences")
    
    # Tone preferences
    default_tone = st.select_slider(
        "Default Content Tone",
        options=["Professional", "Casual", "Friendly", "Humorous", "Educational"],
        value="Professional",
        key="default_content_tone"
    )
    
    # AI assistance level
    ai_assistance = st.slider(
        "AI Assistance Level",
        min_value=0,
        max_value=100,
        value=75,
        key="ai_assistance_level",
        help="How much AI help do you want? (0 = minimal, 100 = maximum)"
    )
    
    # Content length preferences
    st.subheader("Content Length Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input(
            "Twitter optimal length",
            min_value=50,
            max_value=280,
            value=180,
            key="twitter_optimal_length"
        )
    
    with col2:
        st.number_input(
            "LinkedIn optimal length",
            min_value=100,
            max_value=1300,
            value=600,
            key="linkedin_optimal_length"
        )
    
    # Automation preferences
    st.subheader("Automation Settings")
    
    st.checkbox("Auto-schedule to optimal times", value=False, key="auto_schedule_optimal")
    st.checkbox("Auto-crosspost between platforms", value=False, key="auto_crosspost")
    st.checkbox("Auto-reply to comments", value=False, key="auto_reply")
    st.checkbox("Auto-repost top performing content", value=False, key="auto_repost")
    
    # Privacy and security
    st.subheader("Privacy & Security")
    
    st.checkbox("Enable analytics tracking", value=True, key="enable_analytics")
    st.checkbox("Store content history", value=True, key="store_content_history")
    st.selectbox(
        "Data retention period",
        ["1 month", "3 months", "6 months", "1 year", "Indefinite"],
        key="data_retention"
    )
    
    # Export/Import settings
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Settings"):
            export_settings()
    
    with col2:
        uploaded_file = st.file_uploader("📥 Import Settings", type=['json'])
        if uploaded_file:
            import_settings(uploaded_file)


def export_settings():
    """Export current settings to JSON."""
    import json
    
    # Collect all settings from session state
    settings = {}
    setting_keys = [key for key in st.session_state.keys() if key.endswith('_setting') or 
                   key.startswith('default_') or key.startswith('ai_') or 
                   key.startswith('twitter_') or key.startswith('linkedin_')]
    
    for key in setting_keys:
        settings[key] = st.session_state[key]
    
    settings_json = json.dumps(settings, indent=2)
    
    st.download_button(
        label="Download Settings",
        data=settings_json,
        file_name=f"zenalto_settings_{st.session_state.get('user_id', 'user')}.json",
        mime="application/json"
    )
    
    st.success("Settings exported successfully!")


def import_settings(uploaded_file):
    """Import settings from JSON file."""
    import json
    
    try:
        settings = json.load(uploaded_file)
        
        # Update session state with imported settings
        for key, value in settings.items():
            st.session_state[key] = value
        
        st.success(f"Settings imported successfully! {len(settings)} settings restored.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error importing settings: {str(e)}")


def get_user_preferences() -> Dict[str, Any]:
    """Get current user preferences from session state."""
    
    return {
        'default_tone': st.session_state.get('default_content_tone', 'Professional'),
        'ai_assistance_level': st.session_state.get('ai_assistance_level', 75),
        'default_platforms': st.session_state.get('default_platforms', ['Twitter', 'LinkedIn']),
        'auto_optimize': st.session_state.get('ai_auto_optimize', True),
        'auto_hashtags': st.session_state.get('ai_auto_hashtags', True),
        'auto_schedule': st.session_state.get('auto_schedule_optimal', False)
    }