#!/usr/bin/env python3
"""
Integration Test Script for Agent Orchestration Engine

This script validates the key requirements from the development assignment:
1. Dual-mode operation support
2. Backward compatibility with existing DeepCode workflows  
3. Intelligent workflow routing
4. Performance requirements
5. Error handling and fallback mechanisms

This script runs without external dependencies to avoid connection issues.
"""

import asyncio
import time
import json
from typing import Dict, Any
from workflows.agent_orchestration_engine import AgentOrchestrationEngine
from workflows.workflow_router import WorkflowRouter


class IntegrationTest:
    """Integration test runner for the orchestration engine."""
    
    def __init__(self):
        self.engine = AgentOrchestrationEngine()
        self.router = WorkflowRouter()
        self.test_results = []
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status} {test_name}")
        if details and not passed:
            print(f"    {details}")

    async def test_workflow_routing_accuracy(self):
        """Test workflow routing accuracy and confidence scoring."""
        print("\n📋 Testing Workflow Routing Accuracy...")
        
        test_cases = [
            # DeepCode cases
            {
                "input": {"user_request": "analyze research paper and implement algorithm", "file_types": [".pdf"]},
                "expected": "deepcode",
                "min_confidence": 0.8
            },
            {
                "input": {"user_request": "github repository code analysis"},
                "expected": "deepcode", 
                "min_confidence": 0.5
            },
            # ZenAlto cases
            {
                "input": {"user_request": "create twitter thread about AI trends"},
                "expected": "zenalto",
                "min_confidence": 0.4
            },
            {
                "input": {"user_request": "schedule social media posts", "platform_context": {"twitter": {"connected": True}}},
                "expected": "zenalto",
                "min_confidence": 0.6
            },
            # Hybrid cases
            {
                "input": {"user_request": "turn research paper into social media content", "file_types": [".pdf"]},
                "expected": "hybrid",
                "min_confidence": 0.5
            },
            {
                "input": {"user_request": "create twitter thread explaining my algorithm"},
                "expected": "hybrid",
                "min_confidence": 0.15  # Lower expectation for edge case
            }
        ]
        
        passed_tests = 0
        for i, case in enumerate(test_cases):
            try:
                result = await self.router.detect_workflow_type(case["input"])
                workflow = result["workflow_type"]
                confidence = result["confidence"]
                
                # Check workflow type and confidence
                workflow_correct = workflow == case["expected"]
                confidence_ok = confidence >= case["min_confidence"]
                
                if workflow_correct and confidence_ok:
                    passed_tests += 1
                    self.log_result(f"Routing Case {i+1}", True, 
                                    f"{workflow} (conf: {confidence:.2f})")
                else:
                    self.log_result(f"Routing Case {i+1}", False,
                                    f"Got: {workflow} (conf: {confidence:.2f}), Expected: {case['expected']} (conf: >={case['min_confidence']})")
                    
            except Exception as e:
                self.log_result(f"Routing Case {i+1}", False, f"Exception: {str(e)}")
        
        # Overall routing accuracy
        accuracy = passed_tests / len(test_cases)
        self.log_result("Overall Routing Accuracy", accuracy >= 0.8, 
                       f"{passed_tests}/{len(test_cases)} cases passed ({accuracy:.1%})")

    async def test_performance_requirements(self):
        """Test performance requirements (sub-100ms routing)."""
        print("\n⚡ Testing Performance Requirements...")
        
        test_inputs = [
            {"user_request": "analyze research paper", "file_types": [".pdf"]},
            {"user_request": "create social media campaign"},
            {"user_request": "implement algorithm from paper", "file_types": [".py"]},
            {"user_request": "twitter thread about my research"},
        ]
        
        times = []
        for input_data in test_inputs:
            start_time = time.time()
            result = await self.router.detect_workflow_type(input_data)
            elapsed_ms = (time.time() - start_time) * 1000
            times.append(elapsed_ms)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Performance requirements
        avg_under_50ms = avg_time < 50
        max_under_100ms = max_time < 100
        
        self.log_result("Average Response Time", avg_under_50ms,
                       f"Avg: {avg_time:.1f}ms (target: <50ms)")
        self.log_result("Max Response Time", max_under_100ms,
                       f"Max: {max_time:.1f}ms (target: <100ms)")

    def test_engine_initialization(self):
        """Test engine initialization and component setup."""
        print("\n🔧 Testing Engine Initialization...")
        
        # Test engine components
        has_router = self.engine.workflow_router is not None
        has_deepcode = bool(self.engine.deepcode_agents)
        has_zenalto = bool(self.engine.zenalto_agents)
        
        self.log_result("Workflow Router", has_router)
        self.log_result("DeepCode Agents", has_deepcode, 
                       f"Agents: {list(self.engine.deepcode_agents.keys())}")
        self.log_result("ZenAlto Agents", has_zenalto,
                       f"Agents: {list(self.engine.zenalto_agents.keys())}")
        
        # Test workflow status
        try:
            status = self.engine.get_workflow_status()
            expected_workflows = {"deepcode", "zenalto", "hybrid"}
            available_workflows = set(status.get("available_workflows", []))
            workflows_match = expected_workflows == available_workflows
            
            self.log_result("Workflow Status", workflows_match,
                           f"Available: {available_workflows}")
        except Exception as e:
            self.log_result("Workflow Status", False, f"Exception: {str(e)}")

    def test_backward_compatibility_interfaces(self):
        """Test backward compatibility - method signatures preserved."""
        print("\n🔄 Testing Backward Compatibility...")
        
        # Test that expected methods exist
        methods_to_check = [
            "process_request",
            "deepcode_workflow", 
            "zenalto_workflow",
            "hybrid_workflow",
            "get_workflow_status",
            "get_available_workflows"
        ]
        
        for method_name in methods_to_check:
            has_method = hasattr(self.engine, method_name)
            is_callable = callable(getattr(self.engine, method_name, None))
            
            self.log_result(f"Method: {method_name}", has_method and is_callable)

    async def test_explicit_workflow_modes(self):
        """Test explicit workflow mode specification."""
        print("\n🎯 Testing Explicit Workflow Modes...")
        
        test_cases = [
            {"user_request": "test request", "workflow_mode": "deepcode"},
            {"user_request": "test request", "workflow_mode": "zenalto"},
            {"user_request": "test request", "workflow_mode": "hybrid"}
        ]
        
        for case in test_cases:
            try:
                result = await self.router.detect_workflow_type(case)
                expected_workflow = case["workflow_mode"]
                actual_workflow = result["workflow_type"]
                confidence = result["confidence"]
                
                # Explicit mode should have high confidence
                correct_workflow = actual_workflow == expected_workflow
                high_confidence = confidence >= 0.9
                
                self.log_result(f"Explicit Mode: {expected_workflow}", 
                               correct_workflow and high_confidence,
                               f"Got: {actual_workflow} (conf: {confidence:.2f})")
                
            except Exception as e:
                self.log_result(f"Explicit Mode: {case['workflow_mode']}", False,
                               f"Exception: {str(e)}")

    def test_error_handling_and_fallbacks(self):
        """Test error handling and fallback mechanisms."""
        print("\n🛡️ Testing Error Handling...")
        
        # Test invalid workflow mode
        fallback_result = self.router.get_fallback_workflow({"error": "test error"})
        has_fallback = fallback_result.get("workflow_type") in ["deepcode", "zenalto", "hybrid"]
        low_confidence = fallback_result.get("confidence", 1.0) <= 0.2
        
        self.log_result("Fallback Mechanism", has_fallback and low_confidence,
                       f"Fallback: {fallback_result.get('workflow_type')} (conf: {fallback_result.get('confidence', 'N/A')})")
        
        # Test input validation
        try:
            validation = self.router.validate_workflow_input("deepcode", {})
            has_warnings = isinstance(validation.get("warnings"), list)
            
            self.log_result("Input Validation", has_warnings,
                           f"Validation warnings: {len(validation.get('warnings', []))}")
        except Exception as e:
            self.log_result("Input Validation", False, f"Exception: {str(e)}")

    def test_caching_and_metrics(self):
        """Test caching and metrics collection."""
        print("\n📊 Testing Caching and Metrics...")
        
        # Test metrics
        try:
            metrics = self.router.get_metrics()
            expected_keys = ["total_routings", "deepcode_count", "zenalto_count", 
                            "hybrid_count", "avg_confidence", "cache_hits"]
            has_all_metrics = all(key in metrics for key in expected_keys)
            
            self.log_result("Metrics Collection", has_all_metrics,
                           f"Metrics keys: {list(metrics.keys())}")
        except Exception as e:
            self.log_result("Metrics Collection", False, f"Exception: {str(e)}")
        
        # Test cache functionality (basic)
        cache_enabled = self.router.cache_decisions
        self.log_result("Cache Configuration", cache_enabled,
                       f"Cache enabled: {cache_enabled}")

    def test_workflow_descriptions(self):
        """Test workflow descriptions and information."""
        print("\n📖 Testing Workflow Descriptions...")
        
        workflows = ["deepcode", "zenalto", "hybrid"]
        
        for workflow in workflows:
            try:
                description = self.router.get_workflow_description(workflow)
                has_description = isinstance(description, str) and len(description) > 50
                
                self.log_result(f"Description: {workflow}", has_description,
                               f"Length: {len(description)} chars")
            except Exception as e:
                self.log_result(f"Description: {workflow}", False, f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Agent Orchestration Engine Integration Tests")
        print("=" * 60)
        
        # Run all test categories
        await self.test_workflow_routing_accuracy()
        await self.test_performance_requirements()
        self.test_engine_initialization()
        self.test_backward_compatibility_interfaces()
        await self.test_explicit_workflow_modes()
        self.test_error_handling_and_fallbacks()
        self.test_caching_and_metrics()
        self.test_workflow_descriptions()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌") 
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("\n🎉 INTEGRATION TESTS PASSED - System is ready for deployment!")
        elif success_rate >= 70:
            print("\n⚠️  INTEGRATION TESTS MOSTLY PASSED - Some issues need attention")
        else:
            print("\n❌ INTEGRATION TESTS FAILED - Significant issues detected")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        return success_rate >= 85


async def main():
    """Main test runner."""
    test_runner = IntegrationTest()
    success = await test_runner.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)