#!/usr/bin/env python3
"""
Run All Tests
=============

Master test runner for all system tests.
"""

import sys
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_test_file(test_file: str) -> int:
    """Run a test file and return exit code"""
    print(f"\n{'=' * 80}")
    print(f"Running: {test_file}")
    print(f"{'=' * 80}")
    
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "tests" / test_file)],
        capture_output=False
    )
    
    return result.returncode


def main():
    """Run all test suites"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SYSTEM TEST SUITE")
    print("=" * 80)
    print(f"Project: {PROJECT_ROOT.name}")
    print(f"Python: {sys.version.split()[0]}")
    
    test_files = [
        "test_persistence_system.py",
        "test_automation_system.py",
        "test_report_system.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        test_path = PROJECT_ROOT / "tests" / test_file
        if not test_path.exists():
            print(f"⚠️  Skipping {test_file} (not found)")
            continue
        
        exit_code = run_test_file(test_file)
        results[test_file] = "PASS" if exit_code == 0 else "FAIL"
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_file, result in results.items():
        status = "✅" if result == "PASS" else "❌"
        print(f"{status} {test_file}: {result}")
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r == "PASS")
    failed = total_tests - passed
    
    print(f"\nTotal: {total_tests} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total_tests*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
