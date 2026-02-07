import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from inspyre_vigilance.cli import version as version_module


class TestGetInstalledVersion(unittest.TestCase):
    @patch("inspyre_vigilance.cli.version.metadata.version")
    def test_returns_version_when_package_found(self, mock_version):
        mock_version.return_value = "1.2.3"
        result = version_module.get_installed_version()
        self.assertEqual(result, "1.2.3")
        mock_version.assert_called_once_with("inspyre-vigilance")

    @patch("inspyre_vigilance.cli.version.metadata.version")
    def test_returns_unknown_when_package_not_found(self, mock_version):
        from importlib.metadata import PackageNotFoundError
        mock_version.side_effect = PackageNotFoundError()
        result = version_module.get_installed_version()
        self.assertEqual(result, "unknown")


class TestFetchLatestVersion(unittest.TestCase):
    @patch("inspyre_vigilance.cli.version.urllib.request.urlopen")
    def test_returns_version_on_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = b'{"info": {"version": "2.0.0"}}'
        mock_urlopen.return_value = mock_response

        version, error = version_module.fetch_latest_version()
        self.assertEqual(version, "2.0.0")
        self.assertIsNone(error)

    @patch("inspyre_vigilance.cli.version.urllib.request.urlopen")
    def test_returns_error_on_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Network error")
        version, error = version_module.fetch_latest_version()
        self.assertIsNone(version)
        self.assertIsNotNone(error)
        self.assertIn("Network error", error)

    @patch("inspyre_vigilance.cli.version.urllib.request.urlopen")
    def test_returns_error_on_json_decode_error(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = b'invalid json'
        mock_urlopen.return_value = mock_response

        version, error = version_module.fetch_latest_version()
        self.assertIsNone(version)
        self.assertIsNotNone(error)


class TestCompareVersions(unittest.TestCase):
    def test_installed_less_than_latest(self):
        result = version_module.compare_versions("1.0.0", "2.0.0")
        self.assertEqual(result, -1)

    def test_installed_equal_to_latest(self):
        result = version_module.compare_versions("1.0.0", "1.0.0")
        self.assertEqual(result, 0)

    def test_installed_greater_than_latest(self):
        result = version_module.compare_versions("2.0.0", "1.0.0")
        self.assertEqual(result, 1)

    def test_returns_none_on_invalid_installed_version(self):
        result = version_module.compare_versions("invalid", "1.0.0")
        self.assertIsNone(result)

    def test_returns_none_on_invalid_latest_version(self):
        result = version_module.compare_versions("1.0.0", "invalid")
        self.assertIsNone(result)

    def test_returns_none_on_unknown_installed_version(self):
        result = version_module.compare_versions("unknown", "1.0.0")
        self.assertIsNone(result)


class TestPrintVersionInfo(unittest.TestCase):
    @patch("inspyre_vigilance.cli.version.get_installed_version")
    @patch("builtins.print")
    def test_prints_version_without_update_check(self, mock_print, mock_get_version):
        mock_get_version.return_value = "1.0.0"
        exit_code = version_module.print_version_info(check_updates=False)
        self.assertEqual(exit_code, 0)
        mock_print.assert_called_once_with("Inspyre Vigilance version: 1.0.0")

    @patch("inspyre_vigilance.cli.version.get_installed_version")
    @patch("inspyre_vigilance.cli.version.fetch_latest_version")
    @patch("builtins.print")
    def test_prints_update_available(self, mock_print, mock_fetch, mock_get_version):
        mock_get_version.return_value = "1.0.0"
        mock_fetch.return_value = ("2.0.0", None)
        exit_code = version_module.print_version_info(check_updates=True)
        self.assertEqual(exit_code, 0)
        # Check that both version and update messages were printed
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("1.0.0" in call for call in calls))
        self.assertTrue(any("2.0.0" in call for call in calls))

    @patch("inspyre_vigilance.cli.version.get_installed_version")
    @patch("inspyre_vigilance.cli.version.fetch_latest_version")
    @patch("builtins.print")
    def test_prints_up_to_date(self, mock_print, mock_fetch, mock_get_version):
        mock_get_version.return_value = "2.0.0"
        mock_fetch.return_value = ("2.0.0", None)
        exit_code = version_module.print_version_info(check_updates=True)
        self.assertEqual(exit_code, 0)
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("up to date" in call.lower() for call in calls))

    @patch("inspyre_vigilance.cli.version.get_installed_version")
    @patch("inspyre_vigilance.cli.version.fetch_latest_version")
    @patch("builtins.print")
    def test_handles_fetch_error_gracefully(self, mock_print, mock_fetch, mock_get_version):
        mock_get_version.return_value = "1.0.0"
        mock_fetch.return_value = (None, "Network error")
        exit_code = version_module.print_version_info(check_updates=True)
        self.assertEqual(exit_code, 0)

    @patch("inspyre_vigilance.cli.version.get_installed_version")
    @patch("inspyre_vigilance.cli.version.os.getenv")
    @patch("builtins.print")
    def test_respects_env_var_when_check_updates_is_none(self, mock_print, mock_getenv, mock_get_version):
        mock_get_version.return_value = "1.0.0"
        mock_getenv.return_value = "1"
        # When check_updates is None, it should check the environment variable
        with patch("inspyre_vigilance.cli.version.fetch_latest_version") as mock_fetch:
            mock_fetch.return_value = ("2.0.0", None)
            exit_code = version_module.print_version_info(check_updates=None)
            self.assertEqual(exit_code, 0)
            mock_getenv.assert_called_once_with("INSPYRE_VIGILANCE_CHECK_UPDATES")


if __name__ == "__main__":
    unittest.main()
