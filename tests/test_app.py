import unittest
from unittest.mock import patch
from click import ClickException
from click.testing import CliRunner

import spectroscope.app
from tests.test_config import FakeModuleEntryPoint, FakeModuleWithOptions

BASIC_CONFIG = """
[spectroscope]
eth2_endpoint = "fake.eth2.endpoint:8080"
pubkeys = [
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    ]
"""

MODULE_CONFIG = """
[module_one]
enabled = false
foo = "bar"

[module_two]
enabled = true
baz = ["qux"]
"""


class RunTest(unittest.TestCase):
    _CLICK_INVOKE_PATH = spectroscope.app.run

    def setUp(self):
        self.runner = CliRunner()

    def runWithConfig(self, *configs):
        with self.runner.isolated_filesystem():
            with open(spectroscope.app.DEFAULT_CONFIG_PATH, "w") as config_file:
                for config in configs:
                    config_file.write(config)

            return self.runner.invoke(self._CLICK_INVOKE_PATH)

    def test_empty_config(self):
        result = self.runWithConfig("")
        self.assertIsInstance(result.exception.__context__, ClickException)

    @patch("spectroscope.app.BeaconChainStreamer")
    def test_basic_config(self, bcs_mock):
        result = self.runWithConfig(BASIC_CONFIG)
        self.assertIsNone(result.exception)
        bcs_mock.assert_called_once()

    @patch("spectroscope.app.BeaconChainStreamer")
    @patch("spectroscope.app.load_entry_point")
    def test_with_modules(self, ep_loader_mock, bcs_mock):
        result = self.runWithConfig(BASIC_CONFIG, MODULE_CONFIG)
        self.assertIsNone(result.exception)
        bcs_mock.assert_called_once()
        ep_loader_mock.assert_called_once_with(
            "spectroscope", "spectroscope.module", "module_two"
        )

    @patch("spectroscope.app.load_entry_point")
    def test_with_bad_module(self, ep_loader_mock):
        ep_loader_mock.side_effect = ImportError()
        result = self.runWithConfig(BASIC_CONFIG, MODULE_CONFIG)
        self.assertIsInstance(result.exception.__context__, ClickException)
        ep_loader_mock.assert_called_once_with(
            "spectroscope", "spectroscope.module", "module_two"
        )


class CliTest(RunTest):
    _CLICK_INVOKE_PATH = spectroscope.app.cli


class InitTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def runInit(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(spectroscope.app.init)
            try:
                with open(spectroscope.app.DEFAULT_CONFIG_PATH, "r") as file:
                    contents = file.read()
            except FileNotFoundError:
                contents = None

            return result, contents

    @patch("spectroscope.config.iter_entry_points")
    def test_no_modules(self, ep_iter_mock):
        ep_iter_mock.return_value = []
        result, contents = self.runInit()
        self.assertIsNone(result.exception)
        self.assertRegex(contents, "^\[spectroscope\]\n")

    @patch("spectroscope.config.iter_entry_points")
    def test_prohibit_overwrite(self, ep_iter_mock):
        ep_iter_mock.return_value = []
        with self.runner.isolated_filesystem():
            with open(spectroscope.app.DEFAULT_CONFIG_PATH, "w") as file:
                file.write("")
            result = self.runner.invoke(spectroscope.app.init)

        self.assertIsInstance(result.exception.__context__, ClickException)

    @patch("spectroscope.config.iter_entry_points")
    def test_with_fake_module(self, ep_iter_mock):
        ep_iter_mock.return_value = [
            FakeModuleEntryPoint("fake_module", FakeModuleWithOptions())
        ]
        result, contents = self.runInit()
        self.assertIsNone(result.exception)
        self.assertRegex(contents, "^\[spectroscope\]\n")
        self.assertRegex(contents, "\n\[fake_module\]\n")
