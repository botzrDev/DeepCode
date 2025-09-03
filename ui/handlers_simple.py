"""
Temporary simplified handlers for UI testing
This bypasses the complex MCP agent dependencies for demonstration purposes
"""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable


def initialize_session_state():
    """Initialize Streamlit session state with default values"""
    default_values = {
        'processing': False,
        'show_results': False,
        'last_result': None,
        'last_error': None,
        'results': [],
        'task_counter': 1
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def handle_start_processing_button(input_source: str, input_type: str):
    """Mock handler for start processing button"""
    st.session_state.processing = True
    st.session_state.last_error = None
    
    # Mock processing result
    mock_result = {
        'status': 'success',
        'analysis_result': f'Mock analysis of {input_type}: {input_source[:100]}...',
        'download_result': f'Mock download completed for {input_type}',
        'repo_result': 'Mock code implementation completed successfully!'
    }
    
    st.session_state.last_result = mock_result
    st.session_state.show_results = True
    st.session_state.processing = False
    
    # Add to results history
    st.session_state.results.append({
        'timestamp': datetime.now().isoformat(),
        'status': 'success',
        'input_type': input_type,
        'result': mock_result
    })
    
    st.rerun()


def handle_error_display():
    """Handle error display in the UI"""
    if st.session_state.get('last_error'):
        st.error(f"Error: {st.session_state.last_error}")
        
        if st.button("Clear Error"):
            st.session_state.last_error = None
            st.rerun()