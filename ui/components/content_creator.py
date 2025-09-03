"""
Content Creator Widget for ZenAlto

Interactive content creation interface with platform-specific optimization.
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime, timedelta


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
    
    def _render_character_counter(self, content: str):
        """Render character counter for different platforms."""
        if not content:
            return
            
        char_count = len(content)
        
        # Platform character limits
        limits = {
            'Twitter': 280,
            'LinkedIn': 1300,
            'Instagram': 2200,
            'Facebook': 63206
        }
        
        st.markdown("**Character Count:**")
        cols = st.columns(4)
        
        for i, (platform, limit) in enumerate(limits.items()):
            with cols[i]:
                color = "normal" if char_count <= limit else "inverse"
                st.metric(
                    platform, 
                    f"{char_count}/{limit}",
                    delta=None,
                    delta_color=color
                )
    
    def _render_media_preview(self, uploaded_files):
        """Render preview of uploaded media files."""
        st.markdown("**Media Preview:**")
        
        for file in uploaded_files:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if file.type.startswith('image'):
                    st.image(file, width=100)
                else:
                    st.video(file)
            
            with col2:
                st.caption(f"**{file.name}**")
                st.caption(f"Type: {file.type}")
                st.caption(f"Size: {file.size / 1024:.1f} KB")
    
    def _render_content_options(self):
        """Render content configuration options."""
        
        st.subheader("Options")
        
        # Platform selection
        target_platforms = st.multiselect(
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
    
    def _generate_content(self):
        """Generate AI-enhanced content."""
        with st.spinner("🤖 Generating AI-enhanced content..."):
            # Mock AI content generation
            import time
            time.sleep(2)
            
            st.success("✅ AI content generated! Check the preview below.")
            
            # Store generated content in session state
            st.session_state['generated_content'] = {
                'twitter': {
                    'text': "🚀 Excited to share our latest AI breakthrough! The future of automation is here. #AI #Innovation #TechTrends",
                    'hashtags': ['AI', 'Innovation', 'TechTrends'],
                    'estimated_engagement': 0.045
                },
                'linkedin': {
                    'text': "We're thrilled to announce a significant breakthrough in AI automation that will revolutionize how businesses operate. This innovation represents months of dedicated research and development, bringing us closer to a future where intelligent systems seamlessly integrate with human workflows.",
                    'hashtags': ['ArtificialIntelligence', 'Innovation', 'BusinessAutomation'],
                    'estimated_engagement': 0.032
                }
            }
            st.rerun()
    
    def _preview_content(self):
        """Show content preview for different platforms."""
        st.session_state.show_content_preview = True
        st.rerun()
    
    def _publish_content(self):
        """Publish content to selected platforms."""
        target_platforms = st.session_state.get('target_platforms', [])
        
        if not target_platforms:
            st.error("Please select at least one platform to publish to.")
            return
        
        with st.spinner("📤 Publishing content..."):
            import time
            time.sleep(1)
            
            for platform in target_platforms:
                # Mock publishing
                pass
        
        st.success(f"🚀 Content published to {', '.join(target_platforms)}!")


def render_content_creation():
    """Convenience function to render content creation widget."""
    widget = ContentCreatorWidget()
    widget.render()
    
    # Show content preview if requested
    if st.session_state.get('show_content_preview'):
        st.subheader("Content Preview")
        
        generated_content = st.session_state.get('generated_content', {})
        if generated_content:
            for platform, content in generated_content.items():
                with st.expander(f"📱 {platform.title()} Preview", expanded=True):
                    st.markdown(f"**Content:** {content['text']}")
                    st.markdown(f"**Hashtags:** {', '.join(['#' + tag for tag in content['hashtags']])}")
                    st.metric("Estimated Engagement", f"{content['estimated_engagement']:.1%}")
        else:
            st.info("No generated content available. Click 'Generate with AI' first.")