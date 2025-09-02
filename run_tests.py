#!/usr/bin/env python3
"""
Test Runner für GermanCodeZero Cleaner

Führt alle Unit Tests und Integration Tests aus.
Generiert Coverage-Reports und Test-Berichte.
"""

import sys
import os
import unittest
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False
    print("Warning: coverage package not installed. Install with: pip install coverage")

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


class TestRunner:
    """Advanced test runner with reporting capabilities"""
    
    def __init__(self, verbosity: int = 2, coverage_enabled: bool = True):
        self.verbosity = verbosity
        self.coverage_enabled = coverage_enabled and COVERAGE_AVAILABLE
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0,
            "coverage": {},
            "failed_tests": []
        }
    
    def discover_tests(self, test_dir: str = "tests") -> unittest.TestSuite:
        """Discover all tests in the test directory"""
        loader = unittest.TestLoader()
        suite = loader.discover(test_dir, pattern="test_*.py")
        return suite
    
    def run_with_coverage(self, suite: unittest.TestSuite) -> unittest.TestResult:
        """Run tests with code coverage measurement"""
        if self.coverage_enabled:
            # Initialize coverage
            cov = coverage.Coverage(
                source=["src", "cleaner", "api_server"],
                omit=["*/tests/*", "*/test_*.py", "*/__pycache__/*"]
            )
            cov.start()
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = runner.run(suite)
        
        if self.coverage_enabled:
            # Stop coverage and generate report
            cov.stop()
            cov.save()
            
            # Generate coverage report
            print("\n" + "="*70)
            print("CODE COVERAGE REPORT")
            print("="*70)
            cov.report()
            
            # Generate HTML coverage report
            html_dir = Path("htmlcov")
            cov.html_report(directory=str(html_dir))
            print(f"\nHTML coverage report generated in: {html_dir.absolute()}")
            
            # Get coverage percentage
            coverage_percent = cov.report(show_missing=False)
            self.test_results["coverage"]["percentage"] = coverage_percent
            
            # Generate JSON coverage report
            cov.json_report(outfile="coverage.json")
        
        return result
    
    def run_tests(self, test_pattern: str = None) -> bool:
        """Run all tests or specific test pattern"""
        start_time = time.time()
        
        print("="*70)
        print("GERMANCODEZERO CLEANER - TEST SUITE")
        print("="*70)
        print(f"Starting test run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python version: {sys.version}")
        print(f"Coverage enabled: {self.coverage_enabled}")
        print("="*70 + "\n")
        
        # Discover tests
        if test_pattern:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(test_pattern)
        else:
            suite = self.discover_tests()
        
        # Count tests
        test_count = suite.countTestCases()
        print(f"Discovered {test_count} tests\n")
        self.test_results["total_tests"] = test_count
        
        # Run tests with or without coverage
        result = self.run_with_coverage(suite)
        
        # Calculate duration
        duration = time.time() - start_time
        self.test_results["duration"] = duration
        
        # Process results
        self.process_results(result)
        
        # Generate reports
        self.generate_reports()
        
        # Print summary
        self.print_summary()
        
        return result.wasSuccessful()
    
    def process_results(self, result: unittest.TestResult):
        """Process test results"""
        self.test_results["passed"] = result.testsRun - len(result.failures) - len(result.errors)
        self.test_results["failed"] = len(result.failures)
        self.test_results["errors"] = len(result.errors)
        self.test_results["skipped"] = len(result.skipped)
        
        # Collect failed test details
        for test, traceback in result.failures + result.errors:
            self.test_results["failed_tests"].append({
                "test": str(test),
                "traceback": traceback
            })
    
    def generate_reports(self):
        """Generate test reports in various formats"""
        # JSON report
        report_path = Path("test_report.json")
        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nJSON test report saved to: {report_path.absolute()}")
        
        # Markdown report
        self.generate_markdown_report()
    
    def generate_markdown_report(self):
        """Generate markdown test report"""
        report_path = Path("test_report.md")
        
        with open(report_path, "w") as f:
            f.write("# Test Report - GermanCodeZero Cleaner\n\n")
            f.write(f"**Date:** {self.test_results['timestamp']}\n\n")
            f.write(f"**Duration:** {self.test_results['duration']:.2f} seconds\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests:** {self.test_results['total_tests']}\n")
            f.write(f"- **Passed:** ✅ {self.test_results['passed']}\n")
            f.write(f"- **Failed:** ❌ {self.test_results['failed']}\n")
            f.write(f"- **Errors:** 🔥 {self.test_results['errors']}\n")
            f.write(f"- **Skipped:** ⏭️ {self.test_results['skipped']}\n\n")
            
            if self.coverage_enabled and self.test_results["coverage"]:
                f.write("## Code Coverage\n\n")
                f.write(f"**Overall Coverage:** {self.test_results['coverage'].get('percentage', 0):.1f}%\n\n")
            
            if self.test_results["failed_tests"]:
                f.write("## Failed Tests\n\n")
                for failed in self.test_results["failed_tests"]:
                    f.write(f"### {failed['test']}\n\n")
                    f.write("```\n")
                    f.write(failed['traceback'])
                    f.write("\n```\n\n")
        
        print(f"Markdown test report saved to: {report_path.absolute()}")
    
    def print_summary(self):
        """Print test summary to console"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        errors = self.test_results["errors"]
        skipped = self.test_results["skipped"]
        duration = self.test_results["duration"]
        
        # Calculate pass rate
        if total > 0:
            pass_rate = (passed / total) * 100
        else:
            pass_rate = 0
        
        # Print results with colors (if terminal supports)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"🔥 Errors: {errors}")
        print(f"⏭️ Skipped: {skipped}")
        print(f"\nPass Rate: {pass_rate:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.coverage_enabled and self.test_results["coverage"]:
            print(f"\nCode Coverage: {self.test_results['coverage'].get('percentage', 0):.1f}%")
        
        print("="*70)
        
        # Exit code indication
        if failed > 0 or errors > 0:
            print("❌ TEST RUN FAILED")
        else:
            print("✅ ALL TESTS PASSED")
        print("="*70)


def run_specific_test_module(module_name: str):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f"tests.{module_name}")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_pytest_if_available():
    """Run tests using pytest if available"""
    if PYTEST_AVAILABLE:
        import pytest
        
        args = [
            "-v",  # Verbose
            "--tb=short",  # Short traceback
            "--color=yes",  # Colored output
            "tests/",  # Test directory
        ]
        
        if COVERAGE_AVAILABLE:
            args.extend([
                "--cov=src",
                "--cov=cleaner",
                "--cov=api_server",
                "--cov-report=html",
                "--cov-report=term"
            ])
        
        return pytest.main(args) == 0
    return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run tests for GermanCodeZero Cleaner")
    parser.add_argument(
        "--module", "-m",
        help="Run specific test module (e.g., test_database)"
    )
    parser.add_argument(
        "--test", "-t",
        help="Run specific test (e.g., tests.test_database.TestDatabaseManager.test_singleton_pattern)"
    )
    parser.add_argument(
        "--no-coverage", "-nc",
        action="store_true",
        help="Disable code coverage measurement"
    )
    parser.add_argument(
        "--verbosity", "-v",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Test output verbosity (0=quiet, 1=normal, 2=verbose)"
    )
    parser.add_argument(
        "--pytest", "-p",
        action="store_true",
        help="Use pytest instead of unittest"
    )
    
    args = parser.parse_args()
    
    # Use pytest if requested and available
    if args.pytest:
        if PYTEST_AVAILABLE:
            success = run_pytest_if_available()
        else:
            print("Error: pytest is not installed. Install with: pip install pytest pytest-cov")
            sys.exit(1)
    else:
        # Use unittest runner
        runner = TestRunner(
            verbosity=args.verbosity,
            coverage_enabled=not args.no_coverage
        )
        
        if args.module:
            success = run_specific_test_module(args.module)
        elif args.test:
            success = runner.run_tests(args.test)
        else:
            success = runner.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()