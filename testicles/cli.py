import argparse
import unittest
import traceback
import importlib
import io
import os
import re
import sys
from typing import Callable, Any, Pattern

from .unit_test import UnitTest
from .integration_test import IntegrationTest
from .text_test_result import CustomTextTestResult, TestFailException
from .environment import setup_environment

# Usage
#
# $ python -m testicles.cli [options]
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
#   $ python -m testicles.cli --run profiles
# 2. Find all tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m testicles.cli --run ^test_get_profiles
# 3. Find all UNIT tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m testicles.cli --type unit --run ^test_get_profiles
# 4. Find all INTEGRATION tests in any subdirectory and match a specific function that starts with "test_get_profiles"
#   $ python -m testicles.cli --type integration --run ^test_get_profiles
# 5. Find all UNIT tests in any subdirectory
#   $ python -m testicles.cli --type unit
# 6. Find all INTEGRATION tests in any subdirectory
#   $ python -m testicles.cli --type integration
# 7. Find tests in a specific file
#   $ python -m testicles.cli --file ./tests/app/api/v1/test_unit_health.py
# 8. Find a specific test in a specific file
#   $ python -m testicles.cli --file ./tests/app/api/v1/test_unit_health.py --run ^test_get_health_exception$

cli_parser = argparse.ArgumentParser(description='CLI for test runs')

# Setup arguments for CLI
cli_parser.add_argument(
    "-sd", "--start-dir", type=str, help="path to directory with tests relative to the current working directory, e.g. \"tests\", defaults to \"tests\"", default="tests")
cli_parser.add_argument(
    "-td", "--top-level-dir", type=str, help="path to the project root directory, e.g. \".\", defaults to \".\"", default=".")
cli_parser.add_argument(
    "-t", "--type", type=str, help="\"unit\" or \"integration\"")
cli_parser.add_argument(
    "-f", "--file", type=str, help="path to file relative to the current working directory, e.g. \".\\tests\\path\\to\\file.py\"")
cli_parser.add_argument(
    "-r", "--run", type=str, help="regular expression that matches a test function, e.g. \"^test_incorrect_token\"")

# Parse CLI arguments
args = cli_parser.parse_args()

# Settings for discovery
start_dir = args.start_dir
top_level_dir = args.top_level_dir
discovery_pattern = "test_*.py"

# Setup env
setup_environment(args.type)

# Adjust discovery pattern based on specified test type
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
suite = test_loader.discover(start_dir, discovery_pattern, top_level_dir)

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
            if not callback(test_case):
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

# Global setups
setup_module = None

try:
    setup_module = importlib.import_module(f"{args.start_dir}.setup")
except ModuleNotFoundError as e:
    print('WARN: setup.py not found')

if setup_module is not None:
    if tests_count["unit"] != 0 and hasattr(setup_module, 'unit'):
        setup_module.unit()
    if tests_count["integration"] != 0 and hasattr(setup_module, 'integration'):
        setup_module.integration()


# Start the test run
try:
    unittest.runner.TextTestRunner(
        stream=stream,
        resultclass=CustomTextTestResult,
    ).run(suite)
except TestFailException:
    sys.exit(1)
except Exception as e:
    print(traceback.format_exc())
    print(e.__class__, str(e))

    sys.exit(1)
finally:
    # Dispose resources
    importlib.import_module(f"{args.start_dir}.teardown")
    teardown_module = None

    try:
        teardown_module = importlib.import_module(f"{args.start_dir}.teardown")
    except ModuleNotFoundError as e:
        print('WARN: teardown.py not found')

    if teardown_module is not None:
        if tests_count["unit"] != 0 and hasattr(teardown_module, 'unit'):
            teardown_module.unit()
        if tests_count["integration"] != 0 and hasattr(teardown_module, 'integration'):
            teardown_module.integration()

    stream.close()
