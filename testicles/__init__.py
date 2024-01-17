from os import environ as env
env["PYTHON_ENV"] = "test"  # nopep8

from .unit_test import UnitTest
from .integration_test import IntegrationTest