# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DeepCode/ZenAlto** is an AI-powered research automation platform that transforms research papers, natural language, and requirements into production-ready code. The system operates as both a general research-to-code engine (DeepCode) and a specialized social media management platform (ZenAlto).

### Core Architecture

- **Multi-Agent System**: Specialized AI agents coordinate through the `agent_orchestration_engine.py` 
- **MCP Integration**: Built on Model Context Protocol (MCP) for standardized AI-tool communication
- **Async/Await**: High-performance asynchronous processing throughout the system
- **Dual Interfaces**: CLI and Streamlit web interface for different user preferences

## Common Development Commands

### Running the Application

```bash
# Web interface (recommended)
python deepcode.py
# Or after installation: deepcode

# CLI interface (advanced users) 
python cli/main_cli.py

# Using UV (development)
uv run streamlit run ui/streamlit_app.py
uv run python cli/main_cli.py
```

### Code Quality & Linting

```bash
# Pre-commit hooks (includes ruff formatting and linting)
pre-commit run --all-files

# Manual ruff checks
ruff format .
ruff check --fix .
```

### Testing

The project uses the pre-commit hooks for code quality assurance. No dedicated test framework is configured - testing is primarily done through the MCP server integration testing.

### Dependencies

```bash
# Install dependencies
pip install -r requirements.txt

# Development installation
uv venv --python=3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Key System Components

### 1. Agent Orchestration (`workflows/agent_orchestration_engine.py`)

Central coordination engine managing:
- Content Intent Agent (analyzes user requests)
- Document Parsing Agent (processes papers/documents) 
- Code Planning Agent (designs architecture)
- Code Reference Mining Agent (discovers relevant repositories)
- Code Indexing Agent (builds knowledge graphs)
- Code Generation Agent (synthesizes implementations)

### 2. MCP Server Architecture (`tools/*.py`)

Custom MCP servers providing specialized capabilities:
- `code_implementation_server.py`: Code generation and execution
- `social_media_server.py`: Social platform integration
- `content_intent_server.py`: Intent analysis for content creation
- `document_segmentation_server.py`: Intelligent document processing
- `code_reference_indexer.py`: Repository analysis and indexing

### 3. Workflow Implementations (`workflows/`)

- `code_implementation_workflow.py`: Paper-to-code pipeline
- `codebase_index_workflow.py`: Repository indexing workflow  
- Agent classes in `workflows/agents/` implement specialized behaviors

### 4. Configuration System

- `mcp_agent.config.yaml`: MCP server configurations and agent settings
- `mcp_agent.secrets.yaml`: API keys and authentication (gitignored)
- Two planning modes: "segmented" (recommended) vs "traditional"
- Document segmentation with configurable size thresholds

## Development Guidelines

### File Organization

- **Core Logic**: `workflows/` - Main processing workflows and agent implementations  
- **MCP Servers**: `tools/` - Custom MCP server implementations
- **UI Components**: `ui/` - Streamlit interface modules
- **CLI Interface**: `cli/` - Command-line interface components
- **Prompts**: `prompts/` - LLM prompt templates
- **Utils**: `utils/` - Helper utilities and common functions
- **Config**: `config/` - MCP tool definitions and configuration helpers

### Code Patterns

1. **Async/Await**: All major operations use async patterns for performance
2. **MCP Integration**: Custom tools extend MCP protocol for specialized functionality  
3. **Agent Coordination**: Multi-agent workflows coordinate through central orchestration
4. **Modular Design**: Clear separation between CLI, web UI, and core logic
5. **Configuration-Driven**: Behavior controlled through YAML configuration files

### Important Configuration Notes

- **Search API Keys**: Configure BRAVE_API_KEY or BOCHA_API_KEY in `mcp_agent.config.yaml` 
- **Document Segmentation**: Enable for large documents exceeding token limits
- **Planning Mode**: Use "segmented" mode to avoid token truncation issues
- **Windows Compatibility**: MCP server paths may need absolute path configuration

### Entry Points

- `deepcode.py`: Main application launcher (web interface)
- `cli/main_cli.py`: CLI application entry point
- `ui/streamlit_app.py`: Streamlit web interface
- `setup.py`: Package configuration with `deepcode` console script

### Social Media Features (ZenAlto)

When working on social media functionality:
- Social platforms: Twitter/X, Instagram, LinkedIn, Facebook, YouTube
- Content intent analysis for user request understanding
- Multi-platform content optimization
- Chat-driven content creation workflow
- Analytics and performance tracking capabilities