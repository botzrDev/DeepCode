#!/usr/bin/env python3
"""
Test runner script for DeepCode/ZenAlto comprehensive testing suite.

This script provides convenient test execution with different modes:
- Unit tests only
- Integration tests only  
- End-to-end tests only
- Full test suite
- Specific test files or functions
"""

import sys
import subprocess
import argparse
from typing import List, Optional

def run_tests(
    test_type: str = "all",
    test_paths: Optional[List[str]] = None,
    verbose: bool = True,
    coverage: bool = False
) -> int:
    """
    Run the test suite with specified parameters.
    
    Args:
        test_type: Type of tests to run ('all', 'unit', 'integration', 'e2e')
        test_paths: Specific test paths to run
        verbose: Whether to use verbose output
        coverage: Whether to generate coverage report
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=workflows", "--cov=utils", "--cov=social_apis", "--cov=models"])
        cmd.extend(["--cov-report=html", "--cov-report=term"])
    
    # Determine test paths based on type
    if test_paths:
        cmd.extend(test_paths)
    elif test_type == "unit":
        cmd.extend([
            "tests/test_workflow_router.py",
            "tests/test_social_clients.py::TestSocialClients::test_social_models_integration",
            "tests/test_oauth.py::TestOAuthAuthentication::test_encryption_functionality"
        ])
    elif test_type == "integration":
        cmd.extend([
            "tests/test_agent_integration.py",
            "tests/test_social_clients.py",
            "tests/test_oauth.py"
        ])
    elif test_type == "e2e":
        cmd.extend(["-m", "e2e", "tests/test_e2e.py"])
    else:  # all
        cmd.append("tests/")
    
    print(f"🧪 Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=".")
    
    return result.returncode

def main():
    """Main entry point for test runner."""
    
    parser = argparse.ArgumentParser(description="DeepCode/ZenAlto Test Runner")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "e2e"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Run tests in quiet mode"
    )
    parser.add_argument(
        "test_paths",
        nargs="*",
        help="Specific test paths to run"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🚀 DeepCode/ZenAlto Testing Suite")
    print("=" * 50)
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        test_paths=args.test_paths if args.test_paths else None,
        verbose=not args.quiet,
        coverage=args.coverage
    )
    
    # Print summary
    print("-" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
        print("🎉 DeepCode/ZenAlto integration is working correctly")
    else:
        print("❌ Some tests failed")
        print("🔍 Review the test output above for details")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()