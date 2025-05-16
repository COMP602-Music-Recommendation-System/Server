#!/usr/bin/env python
"""
Test runner for the music recommendation API test suite.
Ensures proper setup and tear down of test environment.
"""
import os
import sys
import pytest

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def main():
    """Run all tests"""
    print("Running music recommendation API tests...")

    # Run pytest with verbose output
    args = [
        '-v',  # Verbose output
        '--no-header',  # No header
        '--no-summary',  # No summary
        '.'  # Current directory - since we're already in tests folder
    ]

    # Run the tests
    result = pytest.main(args)

    # Return exit code
    return result


if __name__ == "__main__":
    sys.exit(main())