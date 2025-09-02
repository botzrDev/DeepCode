# ZenAlto - AI Social Media Management Platform

## Overview

ZenAlto is a comprehensive AI-powered social media management platform built on the DeepCode architecture. It transforms conversational input into optimized social media content across multiple platforms including Twitter/X, Instagram, LinkedIn, Facebook, and YouTube.

## Architecture Conversion Summary

### From DeepCode to ZenAlto

| Component | DeepCode (Original) | ZenAlto (Converted) |
|-----------|-------------------|-------------------|
| **Purpose** | Research-to-code automation | Social media content management |
| **Primary Input** | Research papers, technical docs | Natural language conversations |
| **Output** | Production-ready code | Optimized social media posts |
| **Target Users** | Researchers, developers | Content creators, marketers |
| **Core Workflow** | Paper analysis → Code generation | Intent analysis → Content creation |

### Preserved Architecture Elements

✅ **Python 3.13** - Same language and runtime environment
✅ **MCP (Model Context Protocol)** - Tool integration framework maintained
✅ **Streamlit** - Web interface foundation preserved
✅ **Multi-Agent Architecture** - Agent orchestration system kept
✅ **Async/Await Processing** - Performance model unchanged
✅ **YAML Configuration** - Configuration management system
✅ **Modular Project Structure** - Same organizational approach

### Converted Components

#### Agents Transformation

| Original Agent | New Purpose | Key Responsibilities |
|---------------|-------------|-------------------|
| Research Analysis Agent | Content Intent Agent | Analyze user content requests, extract goals, identify platforms |
| Code Architecture Agent | Content Strategy Agent | Plan posting strategies, optimize timing, manage campaigns |
| Code Implementation Agent | Content Generation Agent | Create posts, captions, threads with AI assistance |
| Document Parsing Agent | Social Content Parser | Process existing content, extract themes, analyze engagement |

#### MCP Tools Transformation

| Original Tool | New Purpose | Integration Points |
|---------------|-------------|-------------------|
| Code Implementation Server | Social Media Server | Platform posting, analytics, scheduling |
| Git Command Server | Content Scheduling Server | Queue management, timing optimization |
| PDF Downloader | Media Upload Server | Image/video processing, optimization |
| Document Segmentation | Content Analysis Server | Intent parsing, content optimization |

## Core Features

### 1. Conversational AI Interface
- **Natural Language Processing**: Understand user intent from casual conversation
- **Context Awareness**: Maintain conversation history and user preferences
- **Multi-Platform Targeting**: Automatically identify appropriate social platforms
- **Smart Content Suggestions**: Proactive recommendations based on user behavior

### 2. Multi-Platform Social Media Management
- **Unified Interface**: Single dashboard for all social platforms
- **Platform-Specific Optimization**: Tailored content for each platform's requirements
- **OAuth 2.0 Integration**: Secure authentication with PKCE security
- **Real-time Status Monitoring**: Live connection status and API health

### 3. AI-Powered Content Intelligence
- **Automated Content Generation**: Create posts, threads, and captions
- **Platform Optimization**: Adjust content length, format, and style
- **Hashtag Intelligence**: AI-generated relevant hashtags
- **Tone Adaptation**: Professional, casual, humorous, engaging styles

### 4. Advanced Scheduling & Automation
- **Smart Scheduling**: Optimal posting times based on audience analytics
- **Bulk Operations**: Schedule multiple posts across platforms
- **Queue Management**: Retry logic for failed publications
- **Campaign Management**: Coordinated multi-post campaigns

### 5. Analytics & Performance Tracking
- **Engagement Metrics**: Track likes, shares, comments, clicks
- **Cross-Platform Analytics**: Unified view across all connected platforms
- **Performance Prediction**: ML-based engagement forecasting
- **Trend Analysis**: Identify optimal content types and posting patterns

## Technical Architecture

### System Components

```
ZenAlto Architecture
├── Frontend Layer (Streamlit)
│   ├── Chat Interface
│   ├── Dashboard & Analytics
│   ├── Content Calendar
│   └── Platform Management
│
├── Agent Orchestration Layer
│   ├── Content Intent Agent
│   ├── Content Strategy Agent
│   ├── Content Generation Agent
│   └── Analytics Agent
│
├── MCP Integration Layer
│   ├── Social Media Server
│   ├── Content Analysis Server
│   ├── Scheduling Server
│   └── Media Management Server
│
├── Platform Integration Layer
│   ├── Twitter/X API Client
│   ├── LinkedIn API Client
│   ├── Instagram API Client
│   ├── Facebook API Client
│   └── YouTube API Client
│
└── Data Persistence Layer
    ├── User Preferences
    ├── Content History
    ├── Analytics Data
    └── Platform Credentials
```

### Data Flow

1. **User Input** → Chat interface receives natural language request
2. **Intent Analysis** → Content Intent Agent processes and categorizes request
3. **Strategy Planning** → Content Strategy Agent determines platforms and timing
4. **Content Generation** → Content Generation Agent creates optimized content
5. **Platform Integration** → Social Media Server posts to target platforms
6. **Analytics Collection** → Performance data gathered and analyzed
7. **Learning Loop** → User preferences and performance inform future suggestions

## Development Setup

### Prerequisites

```bash
# Python 3.13+
python --version

# Required Python packages
pip install streamlit mcp-agent anthropic aiohttp

# Social Media API Keys (for development)
# Twitter API v2.0
# LinkedIn API v2.0
# Instagram Basic Display API
# Facebook Graph API
# YouTube Data API v3.0
```

### Project Structure

```
/workspaces/DeepCode/ (ZenAlto)
├── deepcode.py                 # Main application launcher (renamed to zenalto.py)
├── zenalto_demo.py            # Conversion demonstration
├── requirements.txt           # Python dependencies
├── mcp_agent.config.yaml      # MCP server configuration
├── mcp_agent.secrets.yaml     # API keys and secrets
│
├── prompts/
│   ├── social_prompts.py      # Social media AI prompts
│   └── code_prompts.py        # Legacy code prompts (kept for reference)
│
├── workflows/
│   ├── agent_orchestration_engine.py  # Main orchestration (updated)
│   └── agents/
│       ├── content_intent_agent.py    # New: Intent analysis
│       ├── code_implementation_agent.py # Legacy (kept for reference)
│       └── [other legacy agents]
│
├── tools/
│   ├── social_media_server.py        # New: Platform integrations
│   ├── content_intent_server.py      # New: Intent analysis MCP server
│   ├── code_implementation_server.py # Legacy (kept for reference)
│   └── [other legacy tools]
│
├── ui/
│   ├── streamlit_app.py       # Main Streamlit application
│   ├── layout.py              # UI layout components
│   └── components.py          # Reusable UI components
│
├── cli/
│   ├── main_cli.py           # CLI interface (updated branding)
│   └── cli_app.py            # CLI application logic
│
└── config/
    ├── mcp_tool_definitions.py # Tool definitions (updated)
    └── mcp_tool_definitions_index.py
```

### Configuration

#### MCP Server Configuration (`mcp_agent.config.yaml`)

```yaml
# Social Media Platform Configuration
social_platforms:
  twitter:
    enabled: true
    api_version: "2.0"
    rate_limit: 300
  linkedin:
    enabled: true
    api_version: "2.0"
    rate_limit: 100
  instagram:
    enabled: true
    api_version: "basic_display"
    rate_limit: 200

# AI Model Configuration
ai_models:
  primary: "anthropic/claude-3.5-sonnet"
  fallback: "openai/gpt-4"

# Content Generation Settings
content:
  max_length:
    twitter: 280
    linkedin: 3000
    instagram: 2200
  default_tone: "professional"
  hashtag_limit: 5
```

#### Environment Variables

```bash
# API Keys (store in mcp_agent.secrets.yaml)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Development Workflow

### 1. Starting the Application

```bash
# Launch ZenAlto
python deepcode.py

# Or run directly
streamlit run ui/streamlit_app.py
```

### 2. Development Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with development configuration
python deepcode.py --config development
```

### 3. Testing Components

```bash
# Run the conversion demo
python zenalto_demo.py

# Test individual agents
python -c "from workflows.agents.content_intent_agent import ContentIntentAgent; print('Agent loaded successfully')"
```

## API Reference

### Content Intent Agent

#### `analyze_content_intent(user_request, context)`

Analyzes user content requests and extracts structured intent information.

**Parameters:**
- `user_request` (str): Natural language content request
- `context` (dict): Conversation history and platform status

**Returns:**
```python
{
    "intent_summary": "Create engaging post about AI automation",
    "platforms": ["twitter", "linkedin"],
    "audience": "Tech professionals",
    "content_type": "Professional post",
    "tone": "Professional",
    "topics": ["AI", "automation", "technology"],
    "urgency": "Normal"
}
```

### Social Media Server

#### `post_content(platform, content)`

Posts content to specified social media platform.

**Parameters:**
- `platform` (str): Target platform ("twitter", "linkedin", etc.)
- `content` (dict): Content data with text, media, hashtags

**Returns:**
```python
{
    "success": True,
    "post_id": "1234567890",
    "url": "https://twitter.com/user/status/1234567890",
    "timestamp": "2025-01-15T10:00:00Z"
}
```

#### `get_analytics(platform, post_id, date_range)`

Retrieves analytics data for posts or account performance.

**Parameters:**
- `platform` (str): Target platform
- `post_id` (str, optional): Specific post ID
- `date_range` (dict, optional): Date range for analytics

**Returns:**
```python
{
    "success": True,
    "analytics": {
        "impressions": 1500,
        "engagements": 45,
        "clicks": 12,
        "shares": 3
    },
    "timestamp": "2025-01-15T10:00:00Z"
}
```

### Content Generation Agent

#### `generate_content(intent_analysis, platform_requirements)`

Generates optimized content based on intent analysis.

**Parameters:**
- `intent_analysis` (dict): Structured intent from Content Intent Agent
- `platform_requirements` (dict): Platform-specific requirements

**Returns:**
```python
{
    "success": True,
    "generated_content": {
        "twitter": {
            "text": "Excited to share how AI is transforming business processes! #AI #Automation",
            "hashtags": ["#AI", "#Automation", "#Tech"],
            "media_urls": [],
            "posting_tips": "Post during business hours for max engagement"
        },
        "linkedin": {
            "text": "The future of business is here. AI automation is revolutionizing how we work...",
            "hashtags": ["#AI", "#BusinessAutomation", "#FutureOfWork"],
            "media_urls": ["https://example.com/image.jpg"],
            "posting_tips": "Use professional tone and include industry insights"
        }
    }
}
```

## Error Handling

### Common Error Scenarios

1. **Platform API Rate Limits**
   ```python
   try:
       result = await social_server.post_content("twitter", content)
   except RateLimitError:
       # Implement exponential backoff
       await asyncio.sleep(60)
       result = await social_server.post_content("twitter", content)
   ```

2. **Authentication Failures**
   ```python
   if not platform_status[platform]["connected"]:
       # Trigger OAuth re-authentication flow
       await initiate_oauth_flow(platform)
   ```

3. **Content Validation Errors**
   ```python
   if len(content["text"]) > platform_limits[platform]["max_length"]:
       # Truncate or split content
       content["text"] = truncate_content(content["text"], platform_limits[platform])
   ```

## Security Considerations

### API Key Management
- Store API keys in encrypted `mcp_agent.secrets.yaml`
- Use environment variables for sensitive configuration
- Implement key rotation policies

### OAuth 2.0 Implementation
- Use PKCE (Proof Key for Code Exchange) for enhanced security
- Implement secure token storage and refresh mechanisms
- Validate redirect URIs and state parameters

### Data Privacy
- Encrypt user data and platform credentials
- Implement data retention policies
- Provide user data export/deletion capabilities

## Performance Optimization

### Caching Strategies
- Cache platform API responses for 5-15 minutes
- Store user preferences and conversation history
- Cache analytics data with appropriate TTL

### Rate Limiting
- Implement per-platform rate limiting
- Use exponential backoff for API failures
- Queue requests during high-traffic periods

### Async Processing
- Use async/await for all I/O operations
- Implement connection pooling for API calls
- Process multiple platform posts concurrently

## Testing Strategy

### Unit Tests
```python
# Test content intent analysis
def test_content_intent_analysis():
    agent = ContentIntentAgent()
    result = await agent.analyze_content_intent("Create a Twitter post about AI")
    assert result["platforms"] == ["twitter"]
    assert "AI" in result["topics"]
```

### Integration Tests
```python
# Test full content creation workflow
def test_content_creation_workflow():
    # Test intent analysis → content generation → scheduling
    intent = await intent_agent.analyze_content_intent(user_request)
    content = await generation_agent.generate_content(intent)
    result = await social_server.post_content("twitter", content)
    assert result["success"] == True
```

### API Mocking
```python
# Mock social media APIs for testing
@patch('social_apis.twitter_client.TwitterClient.post_tweet')
def test_twitter_posting(mock_post):
    mock_post.return_value = {"id": "12345", "url": "https://twitter.com/status/12345"}
    result = await social_server.post_content("twitter", content)
    assert result["post_id"] == "12345"
```

## Deployment

### Development Environment
```bash
# Local development
streamlit run ui/streamlit_app.py --server.port 8501

# With debugging
streamlit run ui/streamlit_app.py --logger.level debug
```

### Production Deployment
```bash
# Build for production
pip install -r requirements.txt

# Set production environment variables
export ENV=production
export LOG_LEVEL=INFO

# Run with production config
python deepcode.py --config production
```

### Docker Deployment
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.address", "0.0.0.0"]
```

## Monitoring & Logging

### Application Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/zenalto.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Performance Monitoring
- Track API response times
- Monitor agent processing times
- Log platform API usage and errors
- Track user engagement metrics

### Health Checks
```python
# Platform connectivity health check
async def health_check():
    results = {}
    for platform in ["twitter", "linkedin", "instagram"]:
        try:
            status = await social_server.get_platform_status(platform)
            results[platform] = status["connected"]
        except Exception as e:
            results[platform] = False
            logger.error(f"Health check failed for {platform}: {str(e)}")
    return results
```

## Future Enhancements

### Phase 2 Features
- **Advanced Analytics Dashboard**: Real-time engagement tracking
- **Media Management**: AI-powered image/video optimization
- **Campaign Management**: Multi-post campaign orchestration
- **Team Collaboration**: Multi-user content approval workflows

### Phase 3 Features
- **Predictive Analytics**: ML-based performance forecasting
- **Automated A/B Testing**: Content optimization experiments
- **Trend Analysis**: Social media trend detection and recommendations
- **Integration APIs**: Third-party tool integrations

### Technical Improvements
- **Database Integration**: PostgreSQL for data persistence
- **Caching Layer**: Redis for performance optimization
- **Microservices Architecture**: Separate services for scalability
- **Real-time Notifications**: WebSocket-based live updates

## Contributing

### Code Standards
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all classes and methods
- Implement proper error handling and logging

### Development Process
1. Create feature branch from `main`
2. Implement changes with comprehensive tests
3. Update documentation as needed
4. Submit pull request with detailed description
5. Code review and approval before merging

### Testing Requirements
- Unit test coverage > 80%
- Integration tests for all major workflows
- API mocking for external service dependencies
- Performance testing for critical paths

## Support & Resources

### Documentation
- [API Reference](./api_reference.md)
- [User Guide](./user_guide.md)
- [Deployment Guide](./deployment.md)
- [Troubleshooting](./troubleshooting.md)

### Community
- **Discord**: Join our community for support and discussions
- **GitHub Issues**: Report bugs and request features
- **Documentation Wiki**: Comprehensive guides and tutorials

### Getting Help
1. Check the troubleshooting guide first
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Join our Discord community for real-time help

---

*This documentation covers the conversion from DeepCode to ZenAlto. For the original DeepCode documentation and legacy components, see the `legacy/` directory.*</content>
<parameter name="filePath">/workspaces/DeepCode/ZENALTO_DEVELOPER_GUIDE.md
