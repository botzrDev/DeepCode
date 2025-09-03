"""
Workflow Router Implementation for DeepCode/ZenAlto Intelligent Routing System

This module provides the core workflow routing system that enables intelligent switching 
between DeepCode (research-to-code) and ZenAlto (social media) workflows based on 
user input analysis.

Features:
- Intelligent workflow detection with confidence scoring
- Weighted indicator system (strong/moderate/weak patterns)
- File type analysis with comprehensive mappings  
- Hybrid workflow detection for combined requirements
- Configuration-driven behavior with caching
- Comprehensive error handling and fallbacks
- Performance optimized for <100ms response time
- Detailed logging and metrics collection
"""

import logging
import os
import re
import time
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class WorkflowRouter:
    """
    Intelligent workflow routing system for DeepCode/ZenAlto dual-mode operation.
    
    Responsibilities:
    - Analyze user input to determine workflow type
    - Support explicit mode selection
    - Provide confidence scores for routing decisions
    - Handle ambiguous cases with smart defaults
    - Cache decisions for performance optimization
    - Collect metrics for continuous improvement
    """

    def __init__(self, config_path: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the workflow router with configuration and logging.

        Args:
            config_path: Path to configuration file (defaults to mcp_agent.config.yaml)
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Load configuration
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'mcp_agent.config.yaml')
        self.config = self._load_config()
        
        # Initialize workflow routing configuration
        self.routing_config = self.config.get('workflow_routing', {})
        self.default_mode = self.routing_config.get('default_mode', 'auto')
        self.confidence_threshold = self.routing_config.get('confidence_threshold', 0.7)
        self.ambiguous_case_default = self.routing_config.get('ambiguous_case_default', 'deepcode')
        self.enable_hybrid = self.routing_config.get('enable_hybrid', True)
        self.cache_decisions = self.routing_config.get('cache_decisions', True)
        self.cache_ttl = self.routing_config.get('cache_ttl', 300)
        
        # Initialize caching system
        self._decision_cache = {} if self.cache_decisions else None
        
        # Initialize metrics collection
        self.metrics = {
            "total_routings": 0,
            "deepcode_count": 0,
            "zenalto_count": 0,
            "hybrid_count": 0,
            "avg_confidence": 0.0,
            "fallback_count": 0,
            "cache_hits": 0,
            "avg_decision_time_ms": 0.0
        }
        
        # Define weighted indicator lists
        self.deepcode_indicators = {
            'strong': [
                'research paper', 'implement algorithm', 'code generation', 'github repository',
                'academic paper', 'research implementation', 'algorithm implementation',
                'codebase analysis', 'software development', 'programming project'
            ],
            'moderate': [
                'pdf', 'academic', 'repository', 'function', 'class', 'programming',
                'implementation', 'analysis', 'technical', 'development', 'software',
                'code', 'github', 'algorithm', 'research', 'paper'
            ],
            'weak': [
                'analyze', 'process', 'generate', 'create', 'build', 'develop',
                'implement', 'study', 'review', 'document', 'technical'
            ]
        }

        self.zenalto_indicators = {
            'strong': [
                'tweet', 'instagram post', 'linkedin post', 'social media campaign',
                'hashtag strategy', 'viral content', 'social media management',
                'content calendar', 'engagement metrics', 'follower growth'
            ],
            'moderate': [
                'post', 'share', 'followers', 'engagement', 'viral', 'hashtag',
                'social media', 'linkedin', 'twitter', 'instagram', 'facebook',
                'youtube', 'content creation', 'marketing', 'audience', 'brand'
            ],
            'weak': [
                'content', 'audience', 'schedule', 'publish', 'share', 'promote',
                'market', 'campaign', 'social', 'media', 'platform'
            ]
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}

    async def detect_workflow_type(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user input to determine appropriate workflow type with detailed analysis.
        
        Args:
            input_data: Dictionary containing:
                - user_request: str - The user's request text
                - file_types: List[str] - File extensions if files are provided
                - workflow_mode: str - Explicit workflow specification
                - context: Dict - Additional context information
                - platform_context: Dict - Social platform connection status

        Returns:
            Dict containing:
                - workflow_type: "deepcode" | "zenalto" | "hybrid"
                - confidence: float (0.0-1.0)
                - reasoning: str - explanation of decision
                - indicators: List[str] - detected indicators
                - decision_time_ms: float - processing time
                - from_cache: bool - whether result was cached
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(input_data)
            if self._decision_cache and cache_key in self._decision_cache:
                cached_result = self._decision_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    self.metrics["cache_hits"] += 1
                    cached_result["from_cache"] = True
                    return cached_result
                else:
                    # Remove expired cache entry
                    del self._decision_cache[cache_key]

            # Extract and validate input data
            user_request = input_data.get("user_request", "").lower()
            file_types = input_data.get("file_types", [])
            explicit_mode = input_data.get("workflow_mode")
            platform_context = input_data.get("platform_context", {})

            # Initialize result structure
            result = {
                "workflow_type": "deepcode",
                "confidence": 0.0,
                "reasoning": "",
                "indicators": [],
                "decision_time_ms": 0.0,
                "from_cache": False
            }

            # 1. Handle explicit mode specification
            if explicit_mode in ["deepcode", "zenalto", "hybrid"]:
                result.update({
                    "workflow_type": explicit_mode,
                    "confidence": 1.0,
                    "reasoning": f"Explicit workflow mode specified: {explicit_mode}",
                    "indicators": [f"explicit_mode: {explicit_mode}"]
                })
            else:
                # 2. Perform comprehensive analysis
                pattern_scores = await self.analyze_input_patterns(user_request)
                file_type_workflow = self.analyze_file_types(file_types)
                hybrid_potential = self.detect_hybrid_potential(input_data)
                
                # 3. Calculate final workflow decision
                decision_result = self._calculate_workflow_decision(
                    pattern_scores, file_type_workflow, hybrid_potential, 
                    platform_context, user_request
                )
                result.update(decision_result)

            # 4. Record metrics and cache result
            decision_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            result["decision_time_ms"] = round(decision_time, 2)
            
            self._update_metrics(result)
            
            if self._decision_cache is not None:
                result["cache_timestamp"] = datetime.now()
                self._decision_cache[cache_key] = result.copy()
                self.logger.debug(f"Cached result with key: {cache_key}")
            else:
                self.logger.debug("Cache is None, not caching")

            self.logger.info(
                f"Workflow routing: {result['workflow_type']} "
                f"(confidence: {result['confidence']:.2f}, "
                f"time: {result['decision_time_ms']}ms)"
            )

            return result

        except Exception as e:
            decision_time = (time.time() - start_time) * 1000
            self.logger.error(f"Error in workflow detection: {e}")
            self.metrics["fallback_count"] += 1
            self.metrics["total_routings"] += 1
            fallback_result = self.get_fallback_workflow({"error": str(e)})
            fallback_result["decision_time_ms"] = round(decision_time, 2)
            return fallback_result

    async def analyze_input_patterns(self, text: str) -> Dict[str, float]:
        """
        Analyze text for workflow-specific patterns using weighted scoring.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict containing:
                - deepcode_score: float
                - zenalto_score: float  
                - hybrid_potential: float
        """
        if not text:
            return {"deepcode_score": 0.0, "zenalto_score": 0.0, "hybrid_potential": 0.0}

        # Calculate weighted scores
        deepcode_score = self._calculate_weighted_score(text, self.deepcode_indicators)
        zenalto_score = self._calculate_weighted_score(text, self.zenalto_indicators)
        
        # Normalize scores to 0-1 range (more generous normalization)
        max_possible_score = 15  # Reduced for more realistic scoring
        deepcode_normalized = min(deepcode_score / max_possible_score, 1.0)
        zenalto_normalized = min(zenalto_score / max_possible_score, 1.0)
        
        # Calculate hybrid potential
        hybrid_potential = min(deepcode_normalized * zenalto_normalized * 2, 1.0)
        
        return {
            "deepcode_score": deepcode_normalized,
            "zenalto_score": zenalto_normalized,
            "hybrid_potential": hybrid_potential
        }

    def analyze_file_types(self, files: List[str]) -> str:
        """
        Determine workflow based on file types with comprehensive mappings.
        
        Args:
            files: List of file paths or extensions
            
        Returns:
            str: Suggested workflow type based on file analysis
        """
        if not files:
            return "unknown"

        # File mappings as specified in requirements
        deepcode_extensions = {
            # Research documents
            '.pdf', '.tex', '.md', '.rst', '.txt', '.docx', '.doc',
            # Code files
            '.py', '.js', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go',
            '.ts', '.jsx', '.tsx', '.php', '.rb', '.swift', '.kt', '.scala',
            '.r', '.m', '.ipynb', '.html', '.css', '.sql', '.sh', '.bat'
        }
        
        zenalto_extensions = {
            # Media files
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp',
            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv',
            '.mp3', '.wav', '.ogg', '.m4a', '.flac',
            # Data files for social analytics
            '.csv', '.xlsx', '.xls', '.json', '.xml'
        }

        # Analyze file extensions
        deepcode_count = 0
        zenalto_count = 0
        
        for file in files:
            # Extract extension - handle both paths and extensions
            if file.startswith('.') and file.count('.') == 1:
                # This is already an extension
                ext = file.lower()
            else:
                # This is a file path
                ext = Path(file).suffix.lower()
            
            if ext in deepcode_extensions:
                deepcode_count += 1
            elif ext in zenalto_extensions:
                zenalto_count += 1

        # Determine workflow based on file type analysis
        if deepcode_count > 0 and zenalto_count == 0:
            return "deepcode"
        elif zenalto_count > 0 and deepcode_count == 0:
            return "zenalto"
        elif deepcode_count > 0 and zenalto_count > 0:
            return "hybrid"
        else:
            return "unknown"

    def detect_hybrid_potential(self, input_data: Dict) -> bool:
        """
        Detect if request requires both workflows (hybrid approach).
        
        Args:
            input_data: Complete input data dictionary
            
        Returns:
            bool: True if hybrid workflow is recommended
        """
        user_request = input_data.get("user_request", "").lower()
        
        # Hybrid patterns - requests that clearly need both workflows
        hybrid_patterns = [
            r".*twitter.*thread.*research.*paper",
            r".*twitter.*thread.*algorithm",
            r".*twitter.*thread.*implementation",
            r".*linkedin.*post.*about.*my.*code",
            r".*social.*media.*explain.*algorithm",
            r".*create.*posts.*about.*implementation",
            r".*share.*research.*on.*social",
            r".*turn.*paper.*into.*content",
            r".*promote.*code.*project",
            r".*generate.*content.*from.*research",
            r".*explaining.*my.*algorithm.*implementation",
            r".*social.*posts.*about.*code",
            r".*thread.*explaining.*algorithm"
        ]
        
        for pattern in hybrid_patterns:
            if re.search(pattern, user_request):
                return True
        
        # Check if both workflow indicators are present with lower threshold
        pattern_scores = self.analyze_input_patterns_sync(user_request)
        return (pattern_scores["deepcode_score"] > 0.3 and 
                pattern_scores["zenalto_score"] > 0.1)  # Lower threshold for zenalto

    def get_fallback_workflow(self, error_context: Dict) -> Dict[str, Any]:
        """
        Determine safe fallback when detection fails.
        Priority: user_preference > config_default > "deepcode"
        
        Args:
            error_context: Context information about the error
            
        Returns:
            Dict: Fallback workflow decision
        """
        fallback_type = self.ambiguous_case_default
        
        return {
            "workflow_type": fallback_type,
            "confidence": 0.1,  # Low confidence for fallback
            "reasoning": f"Fallback due to detection error: {error_context.get('error', 'unknown')}",
            "indicators": ["fallback"],
            "decision_time_ms": 0.0,
            "from_cache": False
        }

    def validate_workflow_compatibility(self, workflow_type: str, input_data: Dict) -> Tuple[bool, str]:
        """
        Ensure input data is compatible with selected workflow.
        
        Args:
            workflow_type: Selected workflow type
            input_data: Input data to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            user_request = input_data.get("user_request", "")
            file_types = input_data.get("file_types", [])

            if workflow_type == "deepcode":
                if not user_request and not file_types:
                    return False, "DeepCode workflow requires either research content or files"
                
            elif workflow_type == "zenalto":
                if not user_request:
                    return False, "ZenAlto workflow requires content creation request"
                    
            elif workflow_type == "hybrid":
                if not user_request:
                    return False, "Hybrid workflow requires detailed request specification"
                    
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def analyze_input_patterns_sync(self, text: str) -> Dict[str, float]:
        """
        Synchronous version of analyze_input_patterns for internal use.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict containing pattern analysis scores
        """
        if not text:
            return {"deepcode_score": 0.0, "zenalto_score": 0.0, "hybrid_potential": 0.0}

        # Calculate weighted scores
        deepcode_score = self._calculate_weighted_score(text, self.deepcode_indicators)
        zenalto_score = self._calculate_weighted_score(text, self.zenalto_indicators)
        
        # Normalize scores to 0-1 range (more generous normalization)
        max_possible_score = 15  # Reduced for more realistic scoring
        deepcode_normalized = min(deepcode_score / max_possible_score, 1.0)
        zenalto_normalized = min(zenalto_score / max_possible_score, 1.0)
        
        # Calculate hybrid potential
        hybrid_potential = min(deepcode_normalized * zenalto_normalized * 2, 1.0)
        
        return {
            "deepcode_score": deepcode_normalized,
            "zenalto_score": zenalto_normalized,
            "hybrid_potential": hybrid_potential
        }

    def _calculate_weighted_score(self, text: str, indicator_dict: Dict[str, List[str]]) -> float:
        """Calculate weighted score based on indicator categories."""
        score = 0.0
        
        # Weighted scoring: strong=3, moderate=2, weak=1
        for category, weight in [('strong', 3), ('moderate', 2), ('weak', 1)]:
            for indicator in indicator_dict.get(category, []):
                if indicator in text:
                    score += weight
                    
        return score

    def _calculate_workflow_decision(self, pattern_scores: Dict[str, float], 
                                   file_type_workflow: str, hybrid_potential: bool,
                                   platform_context: Dict, user_request: str) -> Dict[str, Any]:
        """Calculate final workflow decision based on all analysis."""
        
        deepcode_score = pattern_scores["deepcode_score"]
        zenalto_score = pattern_scores["zenalto_score"]
        
        # File type influence (stronger weight)
        if file_type_workflow == "deepcode":
            deepcode_score += 0.5
        elif file_type_workflow == "zenalto":
            zenalto_score += 0.5
        elif file_type_workflow == "hybrid":
            hybrid_potential = True
            deepcode_score += 0.3
            zenalto_score += 0.3
            
        # Platform context influence
        connected_platforms = sum(1 for status in platform_context.values() 
                                 if isinstance(status, dict) and status.get("connected", False))
        if connected_platforms > 0:
            zenalto_score += min(connected_platforms * 0.15, 0.4)

        # Ensure minimum confidence for clear indicators
        if deepcode_score > 0.8:
            deepcode_score = min(deepcode_score, 1.0)
        if zenalto_score > 0.8:
            zenalto_score = min(zenalto_score, 1.0)

        # Determine final workflow
        if hybrid_potential and self.enable_hybrid and (deepcode_score >= 0.2 and zenalto_score >= 0.1):
            workflow_type = "hybrid"
            confidence = min((deepcode_score + zenalto_score) / 2, 1.0)
            reasoning = "Hybrid workflow detected - requires both research and social media components"
        elif deepcode_score > zenalto_score and deepcode_score > 0.2:
            workflow_type = "deepcode"
            confidence = min(deepcode_score, 1.0)
            reasoning = "Research/code-focused request detected"
        elif zenalto_score > deepcode_score and zenalto_score > 0.15:  # Lower threshold for zenalto
            workflow_type = "zenalto"
            confidence = min(zenalto_score, 1.0)
            reasoning = "Social media-focused request detected"
        elif zenalto_score > deepcode_score:  # Even if both are low, prefer the higher one
            workflow_type = "zenalto"
            confidence = max(zenalto_score, 0.5)
            reasoning = "Social media-focused request detected (low confidence)"
        elif deepcode_score > zenalto_score:
            workflow_type = "deepcode"
            confidence = max(deepcode_score, 0.5)
            reasoning = "Research/code-focused request detected (low confidence)"
        else:
            # True tie - use default
            workflow_type = self.ambiguous_case_default
            confidence = max(deepcode_score, zenalto_score, 0.5)
            reasoning = "Ambiguous request, using default workflow"
            
        # Generate indicators list
        indicators = []
        if file_type_workflow != "unknown":
            indicators.append(f"file_types: {file_type_workflow}")
        if connected_platforms > 0:
            indicators.append(f"connected_platforms: {connected_platforms}")
        if hybrid_potential:
            indicators.append("hybrid_pattern_detected")
        if deepcode_score > 0.5:
            indicators.append("strong_deepcode_indicators")
        elif deepcode_score > 0.2:
            indicators.append("moderate_deepcode_indicators")
        if zenalto_score > 0.5:
            indicators.append("strong_zenalto_indicators")
        elif zenalto_score > 0.2:
            indicators.append("moderate_zenalto_indicators")
        
        # Add workflow-specific indicators when that workflow is chosen
        if workflow_type == "zenalto" and zenalto_score > 0:
            indicators.append("zenalto_patterns_detected")
        elif workflow_type == "deepcode" and deepcode_score > 0:
            indicators.append("deepcode_patterns_detected")
            
        return {
            "workflow_type": workflow_type,
            "confidence": min(confidence, 1.0),
            "reasoning": reasoning,
            "indicators": indicators
        }

    def _generate_cache_key(self, input_data: Dict[str, Any]) -> str:
        """Generate a cache key for the input data."""
        key_parts = [
            input_data.get("user_request", ""),
            str(sorted(input_data.get("file_types", []))),
            str(input_data.get("workflow_mode", "")),
            str(sorted(input_data.get("platform_context", {}).keys()))
        ]
        return "|".join(key_parts)

    def _is_cache_valid(self, cached_result: Dict) -> bool:
        """Check if cached result is still valid."""
        if not self.cache_decisions:
            return False
            
        cache_time = cached_result.get("cache_timestamp")
        if not cache_time:
            return False
            
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)

    def _update_metrics(self, result: Dict[str, Any]) -> None:
        """Update routing metrics."""
        self.metrics["total_routings"] += 1
        
        workflow_type = result["workflow_type"]
        if workflow_type == "deepcode":
            self.metrics["deepcode_count"] += 1
        elif workflow_type == "zenalto":
            self.metrics["zenalto_count"] += 1
        elif workflow_type == "hybrid":
            self.metrics["hybrid_count"] += 1
            
        # Update average confidence
        total = self.metrics["total_routings"]
        current_avg = self.metrics["avg_confidence"]
        self.metrics["avg_confidence"] = (current_avg * (total - 1) + result["confidence"]) / total
        
        # Update average decision time
        current_time_avg = self.metrics["avg_decision_time_ms"]
        self.metrics["avg_decision_time_ms"] = (current_time_avg * (total - 1) + result["decision_time_ms"]) / total

    def get_metrics(self) -> Dict[str, Any]:
        """Get current routing metrics."""
        return self.metrics.copy()

    def clear_cache(self) -> None:
        """Clear the decision cache."""
        if self._decision_cache:
            self._decision_cache.clear()
            self.logger.info("Decision cache cleared")

    def validate_workflow_input(self, workflow_type: str, input_data: Dict) -> Dict[str, Any]:
        """
        Validate input data for a specific workflow type.
        
        Args:
            workflow_type: The workflow type to validate for
            input_data: Input data to validate
            
        Returns:
            Dict containing validation results with 'valid' and 'warnings' keys
        """
        warnings = []
        
        try:
            user_request = input_data.get("user_request", "")
            file_types = input_data.get("file_types", [])

            if workflow_type == "deepcode":
                if not user_request and not file_types:
                    warnings.append("DeepCode workflow performs best with research content or files")
                    
            elif workflow_type == "zenalto":
                if not user_request:
                    warnings.append("ZenAlto workflow requires a content creation request")
                    
            elif workflow_type == "hybrid":
                if not user_request:
                    warnings.append("Hybrid workflow requires a detailed request specification")
                    
            return {
                "valid": True,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "valid": False,
                "warnings": [f"Validation error: {str(e)}"]
            }

    def get_workflow_description(self, workflow_type: str) -> str:
        """
        Get human-readable description of workflow capabilities.
        
        Args:
            workflow_type: The workflow type identifier
            
        Returns:
            String describing workflow capabilities
        """
        descriptions = {
            "deepcode": (
                "DeepCode workflow: Analyzes research papers, implements algorithms, "
                "generates production-ready code from academic content, and processes "
                "technical documentation with AI-powered code synthesis."
            ),
            "zenalto": (
                "ZenAlto workflow: Creates engaging social media content, manages "
                "posting schedules, analyzes performance metrics, and optimizes "
                "content strategy across multiple platforms including Twitter, LinkedIn, Instagram."
            ),
            "hybrid": (
                "Hybrid workflow: Combines research analysis with social media content creation. "
                "Transforms technical papers into accessible social posts, creates educational "
                "threads about implementations, and bridges academic insights with public engagement."
            )
        }
        
        return descriptions.get(workflow_type, f"Unknown workflow type: {workflow_type}")
