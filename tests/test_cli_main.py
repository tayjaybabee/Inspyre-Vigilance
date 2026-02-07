import unittest
from unittest.mock import patch

from inspyre_vigilance.cli import main as cli_main


class TestCliMain(unittest.TestCase):
    def test_run_core_returns_zero(self):
        with patch("inspyre_vigilance.cli.main.run_core", return_value=None):
            self.assertEqual(cli_main.main([]), 0)


if __name__ == "__main__":
    unittest.main()
