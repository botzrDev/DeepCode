"""
Enhanced Chat Interface for DeepCode/ZenAlto

Chat interface supporting both research-to-code and social media workflows
with specialized commands and context awareness.
"""

import streamlit as st
from typing import Dict, List, Any
from datetime import datetime


class ChatInterface:
    """Enhanced chat interface for both DeepCode and ZenAlto."""
    
    DEEPCODE_COMMANDS = {
        "/analyze": "Analyze research paper or document",
        "/code": "Generate code from requirements", 
        "/implement": "Implement specific functionality",
        "/test": "Generate test cases",
        "/docs": "Generate documentation"
    }
    
    ZENALTO_COMMANDS = {
        "/post": "Create a social media post",
        "/schedule": "Schedule content for posting",
        "/analytics": "View analytics and insights",
        "/trending": "Check trending topics",
        "/optimize": "Optimize content for engagement",
        "/thread": "Create a Twitter thread",
        "/campaign": "Create a marketing campaign"
    }
    
    def render(self):
        """Render chat interface with mode awareness."""
        
        # Detect current mode
        mode = st.session_state.get('app_mode', 'deepcode')
        
        # Chat container
        st.subheader("🤖 AI Assistant")
        st.caption(f"Active mode: {mode.title()}")
        
        # Show mode-specific quick commands
        self._render_quick_commands(mode)
        
        # Chat messages display
        self._render_chat_messages()
        
        # Chat input
        self._render_chat_input(mode)
    
    def _render_quick_commands(self, mode: str):
        """Render quick command buttons based on mode."""
        
        commands = self.ZENALTO_COMMANDS if mode == 'zenalto' else self.DEEPCODE_COMMANDS
        
        with st.expander("⚡ Quick Commands", expanded=False):
            # Display commands in a grid
            command_items = list(commands.items())
            rows = [command_items[i:i+2] for i in range(0, len(command_items), 2)]
            
            for row in rows:
                cols = st.columns(len(row))
                for i, (cmd, desc) in enumerate(row):
                    with cols[i]:
                        if st.button(f"{cmd}", key=f"quick_cmd_{cmd}"):
                            self._execute_quick_command(cmd, mode)
                        st.caption(desc)
    
    def _render_chat_messages(self):
        """Render chat message history."""
        
        # Initialize chat history if not exists
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Display messages
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_messages:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                        if message.get('timestamp'):
                            st.caption(f"⏰ {message['timestamp'][:19]}")
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        if message.get('timestamp'):
                            st.caption(f"⏰ {message['timestamp'][:19]}")
                        
                        # Show additional data if available
                        if message.get('data'):
                            self._render_message_data(message['data'])
    
    def _render_message_data(self, data: Dict[str, Any]):
        """Render additional message data like generated content or analysis results."""
        
        if data.get('type') == 'content_generated':
            st.success("✅ Content generated successfully!")
            
            generated_content = data.get('content', {})
            for platform, content in generated_content.items():
                with st.expander(f"📱 {platform.title()} Content"):
                    st.write(content.get('text', ''))
                    if content.get('hashtags'):
                        st.caption(f"Hashtags: {', '.join(['#' + tag for tag in content['hashtags']])}")
        
        elif data.get('type') == 'analytics_data':
            st.info("📊 Analytics data retrieved")
            
            metrics = data.get('metrics', {})
            if metrics:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Reach", metrics.get('reach', 'N/A'))
                with col2:
                    st.metric("Engagement", metrics.get('engagement', 'N/A'))  
                with col3:
                    st.metric("Followers", metrics.get('followers', 'N/A'))
        
        elif data.get('type') == 'code_generated':
            st.success("💻 Code generated successfully!")
            
            if data.get('code'):
                st.code(data['code'], language=data.get('language', 'python'))
        
        elif data.get('type') == 'error':
            st.error(f"❌ Error: {data.get('message', 'Unknown error')}")
    
    def _render_chat_input(self, mode: str):
        """Render chat input area."""
        
        # Placeholder text based on mode
        placeholder_text = {
            'zenalto': "Ask me to create content, analyze performance, or help with social media...",
            'deepcode': "Ask me to analyze papers, generate code, or help with research...",
            'hybrid': "Ask me anything about research, code, or social media..."
        }.get(mode, "How can I help you?")
        
        user_input = st.chat_input(placeholder_text)
        
        if user_input:
            self._process_user_input(user_input, mode)
    
    def _process_user_input(self, input_text: str, mode: str):
        """Process user input and generate appropriate response."""
        
        # Add user message
        user_message = {
            'role': 'user',
            'content': input_text,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_messages.append(user_message)
        
        # Process input
        if input_text.startswith("/"):
            self._handle_command(input_text, mode)
        else:
            self._handle_conversation(input_text, mode)
        
        # Scroll to bottom
        st.rerun()
    
    def _handle_command(self, command: str, mode: str):
        """Handle slash commands."""
        
        command_part = command.split()[0]
        
        # Route command based on mode
        if mode == 'zenalto':
            self._handle_zenalto_command(command, command_part)
        elif mode == 'deepcode':
            self._handle_deepcode_command(command, command_part)
        else:  # hybrid mode
            # Try both command sets
            if command_part in self.ZENALTO_COMMANDS:
                self._handle_zenalto_command(command, command_part)
            elif command_part in self.DEEPCODE_COMMANDS:
                self._handle_deepcode_command(command, command_part)
            else:
                self._add_assistant_message(f"Unknown command: {command_part}")
    
    def _handle_zenalto_command(self, full_command: str, command: str):
        """Handle ZenAlto-specific commands."""
        
        if command == "/post":
            self._add_assistant_message("I'll help you create a social media post! What topic or message would you like to share?")
        
        elif command == "/schedule":
            self._add_assistant_message("Let me help you schedule content. Do you have existing content to schedule, or would you like me to create new content?")
        
        elif command == "/analytics":
            # Mock analytics data
            analytics_data = {
                'type': 'analytics_data',
                'metrics': {
                    'reach': '45.2K',
                    'engagement': '4.8%',
                    'followers': '+127'
                }
            }
            self._add_assistant_message("Here are your latest analytics:", analytics_data)
        
        elif command == "/trending":
            trending_topics = ["#AI", "#Innovation", "#TechTrends", "#Automation", "#MachineLearning"]
            self._add_assistant_message(f"Current trending topics: {', '.join(trending_topics)}")
        
        elif command == "/optimize":
            self._add_assistant_message("I can help optimize your content! Share the content you'd like me to improve, and I'll suggest enhancements for better engagement.")
        
        elif command == "/thread":
            self._add_assistant_message("Let's create a Twitter thread! What's the main topic or story you want to tell?")
        
        elif command == "/campaign":
            self._add_assistant_message("I'll help you create a marketing campaign! What's your campaign goal and target audience?")
        
        else:
            self._add_assistant_message(f"Unknown ZenAlto command: {command}")
    
    def _handle_deepcode_command(self, full_command: str, command: str):
        """Handle DeepCode-specific commands."""
        
        if command == "/analyze":
            self._add_assistant_message("I'll help you analyze research content! Please upload a paper or paste a URL for analysis.")
        
        elif command == "/code":
            self._add_assistant_message("I'll generate code for you! What functionality or requirements would you like me to implement?")
        
        elif command == "/implement":
            self._add_assistant_message("Let's implement specific functionality! Describe what you need, and I'll create the implementation.")
        
        elif command == "/test":
            self._add_assistant_message("I'll generate test cases! Share the code or functionality you'd like me to test.")
        
        elif command == "/docs":
            self._add_assistant_message("I'll help generate documentation! What code or project needs documentation?")
        
        else:
            self._add_assistant_message(f"Unknown DeepCode command: {command}")
    
    def _handle_conversation(self, input_text: str, mode: str):
        """Handle natural conversation based on mode."""
        
        # Mock AI response based on mode and content
        with st.spinner("🤖 Thinking..."):
            import time
            time.sleep(1)  # Simulate processing time
            
            response = self._generate_contextual_response(input_text, mode)
            
            # Check if this should generate content
            if any(keyword in input_text.lower() for keyword in ['create', 'post', 'content', 'share']):
                if mode in ['zenalto', 'hybrid']:
                    # Generate mock content
                    generated_content = {
                        'type': 'content_generated',
                        'content': {
                            'twitter': {
                                'text': f"🚀 {input_text[:50]}... What do you think?",
                                'hashtags': ['AI', 'Innovation', 'Tech']
                            },
                            'linkedin': {
                                'text': f"Insights about {input_text[:30]}... This could transform our approach to innovation.",
                                'hashtags': ['Innovation', 'Technology', 'Business']
                            }
                        }
                    }
                    self._add_assistant_message(response, generated_content)
                    return
            
            # Check if this should generate code
            elif any(keyword in input_text.lower() for keyword in ['code', 'function', 'implement', 'programming']):
                if mode in ['deepcode', 'hybrid']:
                    # Generate mock code
                    code_data = {
                        'type': 'code_generated',
                        'code': f'def process_{input_text.split()[0].lower()}():\n    """Generated function based on: {input_text[:50]}"""\n    # Implementation here\n    return True',
                        'language': 'python'
                    }
                    self._add_assistant_message(response, code_data)
                    return
            
            self._add_assistant_message(response)
    
    def _generate_contextual_response(self, input_text: str, mode: str) -> str:
        """Generate contextual response based on input and mode."""
        
        if mode == 'zenalto':
            responses = [
                f"I'd be happy to help you create engaging social media content about {input_text[:30]}...",
                f"Great idea! Let me help you optimize this for your social media platforms.",
                f"I can create compelling content around '{input_text[:40]}...' for your audience.",
            ]
        elif mode == 'deepcode':
            responses = [
                f"I'll analyze and help implement solutions for: {input_text[:40]}...",
                f"Let me break down the research and generate code for: {input_text[:40]}...",
                f"I can help you build this functionality: {input_text[:40]}...",
            ]
        else:  # hybrid
            responses = [
                f"I can help you with both the technical implementation and content creation for: {input_text[:30]}...",
                f"Let me assist you with research analysis and social media strategy for: {input_text[:30]}...",
                f"I'll help you from research to social sharing: {input_text[:30]}...",
            ]
        
        import random
        return random.choice(responses)
    
    def _add_assistant_message(self, content: str, data: Dict[str, Any] = None):
        """Add assistant message to chat history."""
        
        assistant_message = {
            'role': 'assistant',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        st.session_state.chat_messages.append(assistant_message)
    
    def _execute_quick_command(self, command: str, mode: str):
        """Execute a quick command button click."""
        
        # Add command as user message
        user_message = {
            'role': 'user',
            'content': command,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.chat_messages.append(user_message)
        
        # Process the command
        self._handle_command(command, mode)
        st.rerun()


def render_chat_interface():
    """Convenience function to render chat interface."""
    chat_interface = ChatInterface()
    chat_interface.render()