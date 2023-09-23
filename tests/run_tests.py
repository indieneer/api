import argparse
import unittest
from . import UnitTest, IntegrationTest


cli_parser = argparse.ArgumentParser(description='CLI for test runs')

cli_parser.add_argument(
    "type", type=str, help="\"unit\" or \"integration\"")

args = cli_parser.parse_args()

test_loader = unittest.TestLoader()

if args.type == "unit":
    suite = test_loader.discover(".", UnitTest.DISCOVERY_PATTERN)
elif args.type == "integration":
    suite = test_loader.discover(".", IntegrationTest.DISCOVERY_PATTERN)
else:
    cli_parser.error("invalid value for argument \"type\"")

test_runner = unittest.runner.TextTestRunner()
test_runner.run(suite)
