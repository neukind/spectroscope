import unittest
from unittest.mock import patch
from click import ClickException
from click.testing import CliRunner

import spectroscope.app

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


class CliTest(unittest.TestCase):
    pass


class RunTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def runWithConfig(self, *configs):
        with self.runner.isolated_filesystem():
            with open("config.toml", "w") as config_file:
                for config in configs:
                    config_file.write(config)

            return self.runner.invoke(spectroscope.app.run)

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


class InitTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
