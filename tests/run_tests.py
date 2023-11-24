import argparse
import unittest
import io
import os
import re
import sys
from typing import Callable, Any, Pattern

from . import UnitTest, IntegrationTest, CustomTextTestResult
from tests.test_setup import setup_integration_tests

# Usage
#
# $ python -m tests.run_tests [options]
#
# Options:
#
# -t, --type - Specifies the type that tests must match
# -f, --file - Specifies the file path for tests
# -r, --run  - Specifies a regular expression for test functions
#
# Examples:
#
# 1. Find all tests in any subdirectory and match a specific function that contains "profiles"
#   $ python -m tests.run_tests --run profiles
# 2. Find all tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m tests.run_tests --run ^test_get_profiles
# 3. Find all UNIT tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m tests.run_tests --type unit --run ^test_get_profiles
# 4. Find all INTEGRATION tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m tests.run_tests --type integration --run ^test_get_profiles
# 5. Find all UNIT tests in any subdirectory
#   $ python -m tests.run_tests --type unit
# 6. Find all INTEGRATION tests in any subdirectory
#   $ python -m tests.run_tests --type integration
# 7. Find tests in a specific file
#   $ python -m tests.run_tests --file ./tests/app/api/v1/test_unit_health.py
# 8. Find a specific test in a specific file
#   $ python -m tests.run_tests --file ./tests/app/api/v1/test_unit_health.py --run ^test_get_health_exception$


cli_parser = argparse.ArgumentParser(description='CLI for test runs')

cli_parser.add_argument(
    "-t", "--type", type=str, help="\"unit\" or \"integration\"")
cli_parser.add_argument(
    "-f", "--file", type=str, help="path to file starting from the current working directory, e.g. \".\\tests\\path\\to\\file.py\"")
cli_parser.add_argument(
    "-r", "--run", type=str, help="regular expression that matches a test function, e.g. \"^test_incorrect_token\"")

# Parse args
args = cli_parser.parse_args()

# if args.file is None and args.type is None and args.run is None:
#     cli_parser.error(
#         "Either \"--file\", \"--type\" or \"--run\" must be present")

start_dir = "."
discovery_pattern = "test_*.py"

if args.type is not None:
    if args.type == "unit":
        discovery_pattern = UnitTest.DISCOVERY_PATTERN
    elif args.type == "integration":
        discovery_pattern = IntegrationTest.DISCOVERY_PATTERN
    else:
        cli_parser.error("invalid value for argument \"--type\"")
else:
    if args.file is not None:
        start_dir, discovery_pattern = os.path.split(args.file)

# Load tests
test_loader = unittest.TestLoader()
suite = test_loader.discover(start_dir, discovery_pattern)

tests_count = {
    "unit": 0,
    "integration": 0,
    "other": 0
}

# Scan tests


def create_callback():
    def count_test(test_case: unittest.TestCase):
        if isinstance(test_case, UnitTest):
            tests_count["unit"] += 1
        elif isinstance(test_case, IntegrationTest):
            tests_count["integration"] += 1
        else:
            tests_count["other"] += 1

        return True

    def count_and_pick_if_matches(test_case: unittest.TestCase, pattern: Pattern[Any]):
        matches = pattern.search(test_case.id().split('.').pop())

        if matches is None:
            return False

        count_test(test_case)

        return True

    if args.run is None:
        return lambda test_case: count_test(test_case)
    else:
        pattern = re.compile(args.run)

        return lambda test_case: count_and_pick_if_matches(test_case, pattern)


def scan_skip_recursively(suite: unittest.TestSuite, callback: Callable[[unittest.TestCase], bool]):
    to_remove = []

    for test_case in suite:
        if isinstance(test_case, unittest.TestSuite):
            if test_case.countTestCases() == 0:
                continue

            scan_skip_recursively(test_case, callback)
        else:
            should_pick = callback(test_case)

            if should_pick:
                continue

            to_remove.append(test_case)

    for test_case in to_remove:
        suite._tests.remove(test_case)


callback = create_callback()
scan_skip_recursively(suite, callback)

# Display test run
print()
print("\n".join([f"{k}: {v}" for (k, v) in tests_count.items()]))
print()

# Pipe the default test output to this stream
stream = io.StringIO()

# Global setup
cleanup = None
if tests_count["integration"] != 0:
    cleanup = setup_integration_tests(suite)

# Start the test run
try:
    unittest.runner.TextTestRunner(
        stream=stream,
        resultclass=CustomTextTestResult,
    ).run(suite)
except Exception as e:
    import traceback
    print(traceback.format_exc())
    print(e.__class__, str(e))

    sys.exit(1)
finally:
    # Dispose resources
    if cleanup is not None:
        print("Tear down")
        cleanup()

    stream.close()
