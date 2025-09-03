# Development Assignment #5: Workflow Router Implementation

## Priority: 🔥 CRITICAL - Week 1

## Objective
Implement the core workflow routing system that enables intelligent switching between DeepCode (research-to-code) and ZenAlto (social media) workflows based on user input analysis.

## Background
The system currently operates as a single-mode DeepCode pipeline. We need a routing layer that can intelligently detect user intent and route requests to the appropriate workflow while maintaining backward compatibility.

## Deliverables

### 1. Create `workflows/workflow_router.py`

Implement a complete workflow routing system with the following capabilities:

```python
class WorkflowRouter:
    """
    Intelligent workflow routing system for DeepCode/ZenAlto dual-mode operation.
    
    Responsibilities:
    - Analyze user input to determine workflow type
    - Support explicit mode selection
    - Provide confidence scores for routing decisions
    - Handle ambiguous cases with smart defaults
    """
```

### 2. Required Methods

#### A. Workflow Detection
```python
async def detect_workflow_type(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns:
    {
        "workflow_type": "deepcode" | "zenalto" | "hybrid",
        "confidence": 0.0-1.0,
        "reasoning": "explanation of decision",
        "indicators": ["list", "of", "detected", "indicators"]
    }
    """
```

#### B. Input Analysis
```python
async def analyze_input_patterns(self, text: str) -> Dict[str, float]:
    """
    Analyze text for workflow-specific patterns.
    
    Returns:
    {
        "deepcode_score": 0.85,
        "zenalto_score": 0.15,
        "hybrid_potential": 0.0
    }
    """
```

#### C. File Type Detection
```python
def analyze_file_types(self, files: List[str]) -> str:
    """
    Determine workflow based on file types.
    
    File mappings:
    - .pdf, .tex, .md (research) → deepcode
    - .png, .jpg, .mp4 (media) → zenalto
    - .py, .js, .java (code) → deepcode
    - .csv with social data → zenalto
    """
```

## Implementation Requirements

### 1. Indicator Lists

Create comprehensive indicator lists for each workflow:

```python
self.deepcode_indicators = {
    'strong': ['research paper', 'implement algorithm', 'code generation', 'github'],
    'moderate': ['pdf', 'academic', 'repository', 'function', 'class'],
    'weak': ['analyze', 'process', 'generate', 'create']
}

self.zenalto_indicators = {
    'strong': ['tweet', 'instagram post', 'linkedin', 'social media', 'hashtag'],
    'moderate': ['post', 'share', 'followers', 'engagement', 'viral'],
    'weak': ['content', 'audience', 'schedule', 'publish']
}
```

### 2. Scoring Algorithm

Implement weighted scoring:
- Strong indicators: 3 points
- Moderate indicators: 2 points
- Weak indicators: 1 point
- Consider word proximity and context

### 3. Configuration Integration

Read from `mcp_agent.config.yaml`:
```yaml
workflow_routing:
  default_mode: "auto"
  confidence_threshold: 0.7
  ambiguous_case_default: "deepcode"
  enable_hybrid: true
  cache_decisions: true
  cache_ttl: 300
```

### 4. Hybrid Workflow Detection

Detect when both workflows are needed:
```python
def detect_hybrid_potential(self, input_data: Dict) -> bool:
    """
    Detect if request requires both workflows.
    
    Examples:
    - "Create a Twitter thread explaining this research paper"
    - "Generate LinkedIn posts about my code implementation"
    """
```

## Error Handling

### 1. Graceful Fallbacks
```python
def get_fallback_workflow(self, error_context: Dict) -> str:
    """
    Determine safe fallback when detection fails.
    Priority: user_preference > config_default > "deepcode"
    """
```

### 2. Validation
```python
def validate_workflow_compatibility(self, workflow_type: str, input_data: Dict) -> Tuple[bool, str]:
    """
    Ensure input data is compatible with selected workflow.
    Returns (is_valid, error_message)
    """
```

## Testing Requirements

### 1. Unit Tests
Create `tests/test_workflow_router.py` with:
- Test cases for each workflow type detection
- Edge cases (empty input, mixed signals)
- File type detection tests
- Configuration override tests

### 2. Test Scenarios
```python
test_cases = [
    # DeepCode detection
    {"input": "Implement the BERT algorithm from this paper", "expected": "deepcode"},
    
    # ZenAlto detection  
    {"input": "Create a viral Twitter thread about AI", "expected": "zenalto"},
    
    # Hybrid detection
    {"input": "Turn this research into LinkedIn posts", "expected": "hybrid"},
    
    # Ambiguous case
    {"input": "Generate content about machine learning", "expected": "deepcode"},  # default
]
```

### 3. Performance Requirements
- Detection must complete in < 100ms
- Support concurrent routing decisions
- Cache recent decisions for performance

## Integration Points

### 1. Agent Orchestration Engine
The router will be called from `agent_orchestration_engine.py`:
```python
router = WorkflowRouter()
routing_decision = await router.detect_workflow_type(input_data)
```

### 2. Logging
Implement comprehensive logging:
```python
self.logger.info(f"Routing decision: {workflow_type} (confidence: {confidence})")
self.logger.debug(f"Detection indicators: {indicators}")
```

### 3. Metrics Collection
Track routing decisions for optimization:
```python
self.metrics = {
    "total_routings": 0,
    "deepcode_count": 0,
    "zenalto_count": 0,
    "hybrid_count": 0,
    "avg_confidence": 0.0,
    "fallback_count": 0
}
```

## Success Criteria

1. **Accuracy**: >95% correct routing for clear cases
2. **Performance**: <100ms decision time
3. **Reliability**: Zero crashes, graceful fallbacks
4. **Coverage**: Handle all input types specified
5. **Integration**: Seamless integration with orchestration engine

## Code Quality Requirements

1. **Type Hints**: Full typing for all methods
2. **Documentation**: Comprehensive docstrings
3. **Testing**: >90% code coverage
4. **Async/Await**: Proper async implementation
5. **Error Handling**: No unhandled exceptions

## Delivery Format

1. Create `workflows/workflow_router.py`
2. Create `tests/test_workflow_router.py`
3. Update `mcp_agent.config.yaml` with routing configuration
4. Provide integration example in comments

## Example Usage

```python
# Example integration in agent_orchestration_engine.py
from workflows.workflow_router import WorkflowRouter

class AgentOrchestrationEngine:
    def __init__(self):
        self.router = WorkflowRouter()
    
    async def process_request(self, input_data: Dict) -> Dict:
        # Route to appropriate workflow
        routing_decision = await self.router.detect_workflow_type(input_data)
        
        if routing_decision["confidence"] < 0.5:
            # Ask user for clarification
            return {"error": "ambiguous_request", "suggestion": routing_decision}
        
        workflow_type = routing_decision["workflow_type"]
        
        if workflow_type == "deepcode":
            return await self.deepcode_workflow(input_data)
        elif workflow_type == "zenalto":
            return await self.zenalto_workflow(input_data)
        else:
            return await self.hybrid_workflow(input_data)
```

## Notes for Developer

- Maintain backward compatibility with existing DeepCode workflows
- Design for extensibility (easy to add new workflow types)
- Consider implementing a plugin system for custom indicators
- Use caching strategically for repeated requests
- Implement comprehensive logging for debugging
- Consider ML-based routing in future iterations

## Acceptance Criteria

- [ ] All test cases pass
- [ ] Integration with orchestration engine works
- [ ] Performance meets requirements
- [ ] Documentation is complete
- [ ] Code follows project style guidelines
- [ ] No breaking changes to existing functionality