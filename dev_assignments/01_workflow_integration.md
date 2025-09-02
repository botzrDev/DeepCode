# ZENALTO Integration Assignment #1: Workflow Integration

## Objective
Integrate ZENALTO social media workflows into the existing DeepCode agent orchestration system without breaking existing research-to-code functionality.

## Background
The existing `workflows/agent_orchestration_engine.py` handles research paper analysis and code generation. We need to extend this to support social media content creation while preserving all existing DeepCode capabilities.

## Key Requirements

### 1. Preserve DeepCode Functionality
- **Critical**: Existing research-to-code workflows must remain fully functional
- All existing agents and tools should continue working unchanged
- Existing API endpoints and interfaces must be preserved

### 2. Add ZENALTO Workflow Routing
- Implement intelligent input detection to route requests appropriately
- Support hybrid workflows that can handle both research and social media tasks
- Maintain performance standards of existing async/await patterns

## Technical Implementation

### 1. Update Agent Orchestration Engine

**File**: `workflows/agent_orchestration_engine.py`

**Required Changes**:
```python
class AgentOrchestrationEngine:
    def __init__(self):
        # Existing DeepCode initialization
        self.deepcode_agents = self._init_deepcode_agents()
        
        # New ZENALTO initialization
        self.zenalto_agents = self._init_zenalto_agents()
        
        # Workflow routing
        self.workflow_router = WorkflowRouter()
    
    async def process_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point - routes to appropriate workflow"""
        
        # Detect workflow type
        workflow_type = await self.workflow_router.detect_workflow_type(input_data)
        
        if workflow_type == "deepcode":
            return await self.deepcode_workflow(input_data)
        elif workflow_type == "zenalto":
            return await self.zenalto_workflow(input_data)
        elif workflow_type == "hybrid":
            return await self.hybrid_workflow(input_data)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    def _init_zenalto_agents(self):
        """Initialize ZENALTO-specific agents"""
        return {
            'content_intent': ContentIntentAgent(self.mcp_agent, self.logger),
            'content_strategy': ContentStrategyAgent(self.mcp_agent, self.logger),
            'content_generation': ContentGenerationAgent(self.mcp_agent, self.logger),
            'social_content_parser': SocialContentParser(self.mcp_agent, self.logger),
            'analytics': AnalyticsAgent(self.mcp_agent, self.logger),
            'scheduling': SchedulingAgent(self.mcp_agent, self.logger)
        }
    
    async def zenalto_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """ZENALTO social media workflow"""
        
        # Step 1: Analyze content intent
        intent_analysis = await self.zenalto_agents['content_intent'].analyze_content_intent(
            input_data.get('user_request', ''),
            input_data.get('context', {}),
            input_data.get('platform_context', {})
        )
        
        # Step 2: Develop content strategy
        strategy = await self.zenalto_agents['content_strategy'].plan_content_strategy(
            intent_analysis,
            input_data.get('platform_preferences', {})
        )
        
        # Step 3: Generate content
        content = await self.zenalto_agents['content_generation'].generate_content(
            intent_analysis,
            strategy
        )
        
        # Step 4: Schedule or post immediately
        if input_data.get('schedule_time'):
            result = await self.zenalto_agents['scheduling'].schedule_content(
                content,
                input_data['schedule_time']
            )
        else:
            result = await self._post_content_immediately(content)
        
        return {
            'workflow_type': 'zenalto',
            'intent_analysis': intent_analysis,
            'strategy': strategy,
            'content': content,
            'posting_result': result,
            'timestamp': datetime.now().isoformat()
        }
```

### 2. Create Workflow Router

**File**: `workflows/workflow_router.py` (New)

```python
class WorkflowRouter:
    def __init__(self):
        self.deepcode_indicators = [
            'research paper', 'implement', 'code', 'algorithm',
            'github', 'repository', 'pdf', 'academic', 'paper'
        ]
        
        self.zenalto_indicators = [
            'post', 'tweet', 'linkedin', 'instagram', 'social media',
            'facebook', 'youtube', 'hashtag', 'engagement', 'followers'
        ]
    
    async def detect_workflow_type(self, input_data: Dict[str, Any]) -> str:
        """Intelligently detect which workflow to use"""
        
        user_request = input_data.get('user_request', '').lower()
        file_types = input_data.get('file_types', [])
        explicit_mode = input_data.get('workflow_mode')
        
        # Check for explicit mode specification
        if explicit_mode in ['deepcode', 'zenalto', 'hybrid']:
            return explicit_mode
        
        # Check file types
        if any(ft in ['.pdf', '.tex', '.py', '.js', '.md'] for ft in file_types):
            return 'deepcode'
        
        # Analyze request content
        deepcode_score = sum(1 for indicator in self.deepcode_indicators 
                           if indicator in user_request)
        zenalto_score = sum(1 for indicator in self.zenalto_indicators 
                          if indicator in user_request)
        
        if deepcode_score > zenalto_score:
            return 'deepcode'
        elif zenalto_score > deepcode_score:
            return 'zenalto'
        else:
            # Default to deepcode for ambiguous cases
            return 'deepcode'
```

### 3. Update Configuration

**File**: `mcp_agent.config.yaml`

**Add new section**:
```yaml
# Workflow configuration
workflow:
  default_mode: "auto"  # auto, deepcode, zenalto, hybrid
  auto_detection: true
  fallback_mode: "deepcode"

# ZENALTO-specific configuration
zenalto:
  platforms:
    twitter:
      enabled: true
      rate_limit: 300
      default_tone: "professional"
    linkedin:
      enabled: true
      rate_limit: 100
      default_tone: "professional"
    instagram:
      enabled: true
      rate_limit: 200
      default_tone: "casual"
  
  content_generation:
    max_length:
      twitter: 280
      linkedin: 3000
      instagram: 2200
    default_hashtags: 5
    ai_model: "anthropic/claude-3.5-sonnet"
```

## Testing Requirements

### 1. Unit Tests
```python
# Test workflow routing
async def test_workflow_detection():
    router = WorkflowRouter()
    
    # DeepCode detection
    deepcode_input = {"user_request": "Implement this research paper algorithm"}
    assert await router.detect_workflow_type(deepcode_input) == "deepcode"
    
    # ZENALTO detection
    zenalto_input = {"user_request": "Create a Twitter post about AI"}
    assert await router.detect_workflow_type(zenalto_input) == "zenalto"
    
    # File type detection
    pdf_input = {"user_request": "Process this", "file_types": [".pdf"]}
    assert await router.detect_workflow_type(pdf_input) == "deepcode"
```

### 2. Integration Tests
```python
# Test full workflow integration
async def test_zenalto_workflow_integration():
    engine = AgentOrchestrationEngine()
    
    input_data = {
        "user_request": "Create a professional LinkedIn post about machine learning trends",
        "platform_context": {"linkedin": {"connected": True}},
        "workflow_mode": "zenalto"
    }
    
    result = await engine.process_request(input_data)
    
    assert result["workflow_type"] == "zenalto"
    assert "content" in result
    assert "posting_result" in result
    assert result["posting_result"]["success"] == True
```

### 3. Backward Compatibility Tests
```python
# Ensure existing DeepCode functionality is preserved
async def test_deepcode_backward_compatibility():
    engine = AgentOrchestrationEngine()
    
    # Test existing research paper workflow
    input_data = {
        "user_request": "Implement the algorithm from this research paper",
        "paper_content": "...",
        "workflow_mode": "deepcode"
    }
    
    result = await engine.process_request(input_data)
    
    assert result["workflow_type"] == "deepcode"
    assert "implementation" in result
    # Verify all existing DeepCode outputs are present
```

## Success Criteria

### 1. Functionality
- [ ] All existing DeepCode workflows continue to work without modification
- [ ] ZENALTO workflows can successfully create and post social media content
- [ ] Workflow routing correctly identifies input types with >90% accuracy
- [ ] Hybrid workflows can handle complex requests spanning both domains

### 2. Performance
- [ ] No performance degradation in existing DeepCode workflows
- [ ] ZENALTO workflows complete within acceptable time limits (< 30 seconds)
- [ ] Memory usage remains within current system limits
- [ ] Concurrent workflow processing works correctly

### 3. Error Handling
- [ ] Graceful fallback when workflow detection fails
- [ ] Proper error messages for unsupported operations
- [ ] Recovery mechanisms for partial workflow failures

## Implementation Timeline
- **Week 1**: Update agent orchestration engine structure
- **Week 2**: Implement workflow router and detection logic
- **Week 3**: Integration testing and debugging
- **Week 4**: Performance optimization and documentation

## Dependencies
- Completion of ZENALTO agent implementations (Assignment #2)
- Social media MCP servers (Assignment #3)
- UI updates for workflow selection (Assignment #4)

## Notes
- Maintain backward compatibility at all costs
- Use feature flags for gradual rollout
- Implement comprehensive logging for workflow routing decisions
- Consider caching workflow detection results for performance

## Acceptance Testing
1. Load existing DeepCode test suite - all tests must pass
2. Create comprehensive ZENALTO workflow test suite
3. Test workflow switching in production environment
4. Performance benchmarking against current system