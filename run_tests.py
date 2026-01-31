#!/usr/bin/env python3
"""Test runner for Aideck unit tests"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_tests(test_args=None):
    """Run pytest with the given arguments"""
    cmd = [sys.executable, "-m", "pytest"]

    if test_args:
        cmd.extend(test_args)

    # Add default arguments
    cmd.extend(
        [
            "-v",  # verbose output
            "--tb=short",  # shorter traceback format
            "--strict-markers",  # strict marker validation
            "--disable-warnings",  # disable warnings
            "tests/",  # test directory
        ]
    )

    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description="Run Aideck unit tests")
    parser.add_argument(
        "tests",
        nargs="*",
        help="Specific test files or directories to run (default: all tests)",
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument(
        "--cov-report",
        choices=["term", "html", "xml", "json"],
        default="term",
        help="Coverage report format (default: term)",
    )
    parser.add_argument(
        "-k", "--keyword", help="Only run tests matching the given keyword expression"
    )
    parser.add_argument(
        "-m", "--marker", help="Only run tests matching the given marker expression"
    )
    parser.add_argument(
        "--pdb", action="store_true", help="Start the debugger on test failures"
    )
    parser.add_argument(
        "--no-header", action="store_true", help="Don't show the header"
    )

    args = parser.parse_args()

    if not args.no_header:
        print("🧪 Aideck Unit Test Runner")
        print("=" * 50)

    # Build pytest arguments
    test_args = []

    if args.coverage:
        test_args.extend(["--cov=src/aideck", f"--cov-report={args.cov_report}"])

    if args.keyword:
        test_args.extend(["-k", args.keyword])

    if args.marker:
        test_args.extend(["-m", args.marker])

    if args.pdb:
        test_args.append("--pdb")

    # Add specific tests if provided
    if args.tests:
        test_args.extend(args.tests)

    # Run tests
    exit_code = run_tests(test_args)

    # Print summary
    if not args.no_header:
        print("-" * 50)
        if exit_code == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {exit_code})")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
