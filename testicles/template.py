import argparse
import os.path
from pathlib import Path

# Usage
#
# $ python -m testicles.template [options]
#
# Options:
#
# -t, --type   - Specifies the test type
# -m, --module - Specifies the test module
# -f, --file   - Specifies the file path
#
# Examples:
#
# 1. Generate a unit test file for a model
#    $ python -m testicles.template -t unit -f .\app\models\products.py -m models
# 2. Generate an integration test file for a model
#    $ python -m testicles.template -t integration -f .\app\models\products.py -m models
#

cli_parser = argparse.ArgumentParser(description='CLI for test templates')

cli_parser.add_argument(
    "-t", "--type", type=str, help="\"unit\" or \"integration\"")
cli_parser.add_argument(
    "-m", "--module", type=str, help="one of: \"handler\", \"model\"")
cli_parser.add_argument(
    "-f",
    "--file",
    type=str,
    help="path to file relative to the current working directory, e.g. \".\\app\\path\\to\\file.py\"")


# Parse CLI arguments
args = cli_parser.parse_args()

test_type = args.type
if test_type is None:
    raise Exception("type was not provided")

test_module = args.module
if test_module is None:
    raise Exception("module was not provided")

test_path = args.file
if test_path is None:
    raise Exception("file path was not provided")

test_file_dir = os.path.dirname(test_path)
test_file_name = os.path.basename(test_path)
test_file_stem = Path(test_path).stem

test_path = Path(os.path.join('tests', test_file_dir))
test_path.mkdir(parents=True, exist_ok=True)


template = None
with open(os.path.join('tests', 'templates', f"{test_module}.{test_type}.tes"), 'r') as f:
    template = f.read()

with open(os.path.join('tests', test_file_dir, f"test_{test_type}_{test_file_name}"), 'w') as f:
    content = template
    content = content.replace("{{entity_low}}", test_file_stem)
    content = content.replace("{{entity_cap}}", test_file_stem.capitalize())
    content = content.replace("{{test_type_cap}}", test_type.capitalize())
    content = content.replace("{{test_type_low}}", test_type)

    f.write(content)
