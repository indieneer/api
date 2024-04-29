import unittest
from unittest.mock import MagicMock


class UnitTest(unittest.TestCase):
    DISCOVERY_PATTERN = "test_unit_*.py"

    def reset_mock(self, mock: MagicMock):
        """resets a mock to its initial state including return_value and side_effect

        Args:
            mock (MagicMock): A mock to reset
        """

        mock.reset_mock(return_value=True, side_effect=True)
