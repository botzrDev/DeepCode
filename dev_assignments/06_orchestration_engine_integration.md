# Development Assignment #6: Agent Orchestration Engine Integration

## Priority: 🔥 CRITICAL - Week 1

## Objective
Update the existing `agent_orchestration_engine.py` to support dual-mode operation (DeepCode + ZenAlto) while maintaining full backward compatibility with existing research-to-code workflows.

## Background
The orchestration engine currently only handles DeepCode workflows. We need to extend it to initialize ZenAlto agents, integrate the workflow router, and support both workflow types seamlessly.

## Deliverables

### 1. Update `workflows/agent_orchestration_engine.py`

Modify the existing class to support dual-mode operation WITHOUT breaking existing functionality.

## Required Modifications

### 1. Class Structure Updates

```python
class AgentOrchestrationEngine:
    """
    Extended orchestration engine supporting both DeepCode and ZenAlto workflows.
    
    CRITICAL: All existing DeepCode functionality must remain unchanged.
    """
    
    def __init__(self):
        # PRESERVE ALL EXISTING INITIALIZATION
        self.mcp_agent = self._initialize_mcp_agent()
        self.logger = self._setup_logger()
        
        # ADD NEW COMPONENTS
        self.workflow_router = WorkflowRouter()
        self.zenalto_agents = self._init_zenalto_agents()
        self.workflow_metrics = self._init_metrics()
```

### 2. ZenAlto Agent Initialization

Add new method to initialize social media agents:

```python
def _init_zenalto_agents(self) -> Dict[str, Any]:
    """
    Initialize ZenAlto-specific agents for social media management.
    
    Returns dictionary of initialized agents:
    - content_intent: Analyzes user content requests
    - content_strategy: Plans content campaigns
    - content_generation: Creates social media content
    - social_parser: Processes existing social content
    - analytics: Tracks performance metrics
    - scheduling: Manages posting schedules
    """
    
    agents = {}
    
    try:
        # Import ZenAlto agents
        from workflows.agents.content_intent_agent import ContentIntentAgent
        from workflows.agents.content_strategy_agent import ContentStrategyAgent
        from workflows.agents.content_generation_agent import ContentGenerationAgent
        from workflows.agents.social_content_parser import SocialContentParser
        from workflows.agents.analytics_agent import AnalyticsAgent
        from workflows.agents.scheduling_agent import SchedulingAgent
        
        # Initialize each agent
        agents['content_intent'] = ContentIntentAgent(
            self.mcp_agent, 
            self.logger,
            config=self._get_agent_config('content_intent')
        )
        
        agents['content_strategy'] = ContentStrategyAgent(
            self.mcp_agent,
            self.logger,
            config=self._get_agent_config('content_strategy')
        )
        
        # Initialize remaining agents...
        
        self.logger.info("✅ ZenAlto agents initialized successfully")
        
    except ImportError as e:
        self.logger.warning(f"⚠️ Some ZenAlto agents not available: {e}")
        # Return partial agent set
        
    return agents
```

### 3. Main Request Processing Updates

Modify the main entry point to support routing:

```python
async def process_request(
    self, 
    input_data: Dict[str, Any],
    force_workflow: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point - routes to appropriate workflow.
    
    Args:
        input_data: User request and context
        force_workflow: Optional workflow override ("deepcode", "zenalto", "hybrid")
    
    CRITICAL: Must maintain backward compatibility - if no routing info,
    default to DeepCode workflow.
    """
    
    try:
        # Check for forced workflow
        if force_workflow:
            workflow_type = force_workflow
            routing_info = {"confidence": 1.0, "forced": True}
        else:
            # Use router to detect workflow
            routing_decision = await self.workflow_router.detect_workflow_type(input_data)
            workflow_type = routing_decision["workflow_type"]
            routing_info = routing_decision
        
        # Log routing decision
        self.logger.info(f"🔀 Routing to {workflow_type} workflow (confidence: {routing_info.get('confidence', 'N/A')})")
        
        # Track metrics
        self._track_routing_metrics(workflow_type, routing_info)
        
        # Route to appropriate workflow
        if workflow_type == "deepcode":
            # PRESERVE EXISTING DEEPCODE WORKFLOW
            result = await self._execute_deepcode_workflow(input_data)
        elif workflow_type == "zenalto":
            result = await self._execute_zenalto_workflow(input_data)
        elif workflow_type == "hybrid":
            result = await self._execute_hybrid_workflow(input_data)
        else:
            # Fallback to DeepCode for unknown types
            self.logger.warning(f"Unknown workflow type: {workflow_type}, defaulting to deepcode")
            result = await self._execute_deepcode_workflow(input_data)
        
        # Add routing info to result
        result["routing_info"] = routing_info
        result["workflow_type"] = workflow_type
        
        return result
        
    except Exception as e:
        self.logger.error(f"Error in request processing: {e}")
        # Attempt fallback to DeepCode
        return await self._fallback_to_deepcode(input_data, error=str(e))
```

### 4. ZenAlto Workflow Implementation

Add the new social media workflow:

```python
async def _execute_zenalto_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute ZenAlto social media content workflow.
    
    Pipeline:
    1. Analyze content intent
    2. Develop content strategy
    3. Generate optimized content
    4. Schedule or post
    5. Track analytics
    """
    
    result = {
        "workflow": "zenalto",
        "timestamp": datetime.now().isoformat(),
        "stages": {}
    }
    
    try:
        # Stage 1: Intent Analysis
        self.logger.info("🎯 Stage 1: Analyzing content intent...")
        intent_result = await self.zenalto_agents['content_intent'].analyze_intent(
            user_request=input_data.get('user_request', ''),
            context=input_data.get('context', {}),
            platform_preferences=input_data.get('platforms', [])
        )
        result['stages']['intent'] = intent_result
        
        # Stage 2: Content Strategy
        self.logger.info("📋 Stage 2: Developing content strategy...")
        strategy = await self.zenalto_agents['content_strategy'].create_strategy(
            intent=intent_result,
            target_platforms=input_data.get('platforms', ['twitter', 'linkedin']),
            scheduling_preferences=input_data.get('scheduling', {})
        )
        result['stages']['strategy'] = strategy
        
        # Stage 3: Content Generation
        self.logger.info("✍️ Stage 3: Generating content...")
        content = await self.zenalto_agents['content_generation'].generate(
            strategy=strategy,
            tone=input_data.get('tone', 'professional'),
            optimization_params=input_data.get('optimization', {})
        )
        result['stages']['content'] = content
        
        # Stage 4: Scheduling/Posting
        self.logger.info("📅 Stage 4: Scheduling content...")
        if input_data.get('schedule_time'):
            posting_result = await self.zenalto_agents['scheduling'].schedule(
                content=content,
                schedule_time=input_data['schedule_time'],
                platforms=strategy['platforms']
            )
        else:
            posting_result = await self._post_immediately(content, strategy['platforms'])
        result['stages']['posting'] = posting_result
        
        # Stage 5: Analytics Setup
        if posting_result.get('success'):
            self.logger.info("📊 Stage 5: Setting up analytics tracking...")
            analytics = await self.zenalto_agents['analytics'].setup_tracking(
                post_ids=posting_result.get('post_ids', []),
                platforms=strategy['platforms']
            )
            result['stages']['analytics'] = analytics
        
        result['success'] = True
        result['summary'] = self._generate_zenalto_summary(result['stages'])
        
    except Exception as e:
        self.logger.error(f"Error in ZenAlto workflow: {e}")
        result['success'] = False
        result['error'] = str(e)
        
    return result
```

### 5. Hybrid Workflow Implementation

Add support for combined workflows:

```python
async def _execute_hybrid_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute hybrid workflow combining research analysis with social media content.
    
    Example: "Create a Twitter thread explaining this research paper"
    """
    
    result = {
        "workflow": "hybrid",
        "timestamp": datetime.now().isoformat(),
        "deepcode_result": {},
        "zenalto_result": {}
    }
    
    try:
        # Phase 1: DeepCode Analysis
        self.logger.info("📚 Phase 1: Analyzing research content...")
        deepcode_input = self._extract_deepcode_input(input_data)
        deepcode_result = await self._execute_deepcode_workflow(deepcode_input)
        result['deepcode_result'] = deepcode_result
        
        # Phase 2: Transform to Social Content
        self.logger.info("🔄 Phase 2: Transforming to social content...")
        zenalto_input = self._transform_research_to_social(
            research_result=deepcode_result,
            original_request=input_data.get('user_request', ''),
            platforms=input_data.get('platforms', [])
        )
        
        # Phase 3: Generate Social Media Content
        zenalto_result = await self._execute_zenalto_workflow(zenalto_input)
        result['zenalto_result'] = zenalto_result
        
        result['success'] = True
        result['summary'] = self._generate_hybrid_summary(
            deepcode_result, 
            zenalto_result
        )
        
    except Exception as e:
        self.logger.error(f"Error in hybrid workflow: {e}")
        result['success'] = False
        result['error'] = str(e)
        
    return result
```

### 6. Backward Compatibility Preservation

Ensure existing method signatures remain unchanged:

```python
# PRESERVE EXISTING METHOD - DO NOT MODIFY
async def process_research_paper(self, paper_content: str, **kwargs):
    """Original DeepCode method - must remain unchanged."""
    # Existing implementation
    pass

# PRESERVE EXISTING METHOD - DO NOT MODIFY  
async def generate_code_from_paper(self, paper_analysis: Dict, **kwargs):
    """Original DeepCode method - must remain unchanged."""
    # Existing implementation
    pass

# ADD COMPATIBILITY WRAPPER
async def process(self, *args, **kwargs):
    """
    Compatibility wrapper for various input formats.
    """
    # Detect old-style calls and route appropriately
    if len(args) == 1 and isinstance(args[0], str):
        # Old-style paper processing
        return await self.process_research_paper(args[0], **kwargs)
    else:
        # New-style with input_data dict
        return await self.process_request(*args, **kwargs)
```

## Configuration Updates

Add to `mcp_agent.config.yaml`:

```yaml
orchestration:
  enable_zenalto: true
  enable_hybrid: true
  default_workflow: "auto"
  
  zenalto_agents:
    content_intent:
      enabled: true
      model: "claude-3.5-sonnet"
      max_tokens: 2000
    
    content_strategy:
      enabled: true
      model: "claude-3.5-sonnet"
      max_tokens: 3000
    
    content_generation:
      enabled: true
      model: "claude-3.5-sonnet"
      max_tokens: 4000
      
    # Additional agent configs...

  workflow_timeouts:
    deepcode: 300  # 5 minutes
    zenalto: 60    # 1 minute
    hybrid: 360    # 6 minutes
```

## Testing Requirements

### 1. Backward Compatibility Tests

```python
def test_existing_deepcode_workflows():
    """Ensure all existing DeepCode functionality works unchanged."""
    
    engine = AgentOrchestrationEngine()
    
    # Test old-style paper processing
    result = await engine.process_research_paper("paper content...")
    assert result  # Should work exactly as before
    
    # Test old-style code generation
    result = await engine.generate_code_from_paper({...})
    assert result  # Should work exactly as before
```

### 2. New Workflow Tests

```python
def test_zenalto_workflow():
    """Test new ZenAlto workflow."""
    
    engine = AgentOrchestrationEngine()
    
    input_data = {
        "user_request": "Create a Twitter thread about AI trends",
        "platforms": ["twitter"],
        "workflow_mode": "zenalto"
    }
    
    result = await engine.process_request(input_data)
    assert result["workflow_type"] == "zenalto"
    assert result["success"] == True
```

### 3. Hybrid Workflow Tests

```python
def test_hybrid_workflow():
    """Test hybrid research-to-social workflow."""
    
    engine = AgentOrchestrationEngine()
    
    input_data = {
        "user_request": "Create LinkedIn posts explaining this research paper",
        "paper_content": "...",
        "platforms": ["linkedin"]
    }
    
    result = await engine.process_request(input_data)
    assert result["workflow_type"] == "hybrid"
    assert "deepcode_result" in result
    assert "zenalto_result" in result
```

## Error Handling Requirements

1. **Graceful Degradation**: If ZenAlto agents fail to initialize, system should still support DeepCode
2. **Workflow Isolation**: Errors in one workflow shouldn't affect others
3. **Comprehensive Logging**: All routing decisions and errors must be logged
4. **Fallback Mechanisms**: Always fallback to DeepCode when uncertain

## Performance Requirements

1. **No Performance Degradation**: DeepCode workflows must maintain current performance
2. **Lazy Loading**: ZenAlto agents only initialized when needed
3. **Concurrent Processing**: Support parallel workflow execution
4. **Resource Management**: Proper cleanup of agents after use

## Success Criteria

- [ ] All existing DeepCode tests pass without modification
- [ ] New ZenAlto workflow fully functional
- [ ] Hybrid workflow successfully combines both systems
- [ ] No breaking changes to existing API
- [ ] Performance metrics remain stable
- [ ] Comprehensive error handling implemented

## Notes for Developer

- **CRITICAL**: Do not modify existing DeepCode methods - add new methods instead
- Use dependency injection for new agents to maintain testability
- Implement feature flags for gradual rollout
- Consider adding workflow versioning for future updates
- Document all new methods thoroughly
- Add telemetry for monitoring workflow distribution

## Delivery Checklist

- [ ] Updated `agent_orchestration_engine.py` with dual-mode support
- [ ] All existing tests still pass
- [ ] New tests for ZenAlto and hybrid workflows
- [ ] Updated configuration file
- [ ] Performance benchmarks show no degradation
- [ ] Documentation updated with new workflows