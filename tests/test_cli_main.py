import unittest
from unittest.mock import patch

from inspyre_vigilance.cli import main as cli_main


class TestCliMain(unittest.TestCase):
    def test_run_core_int_exit_code_is_returned(self):
        with patch("inspyre_vigilance.cli.main.run_core", return_value=5):
            self.assertEqual(cli_main.main([]), 5)

    def test_run_core_bool_exit_code_defaults_to_zero(self):
        with patch("inspyre_vigilance.cli.main.run_core", return_value=True):
            self.assertEqual(cli_main.main([]), 0)


if __name__ == "__main__":
    unittest.main()
