import unittest
from unittest.mock import Mock, patch

from spectroscope.config import DefaultConfigBuilder, SYSTEM_MODULE_CONFIG
from spectroscope.module import ConfigOption


def FakeModuleEntryPoint(name, module):
    ep = Mock()
    ep.name = name
    ep.load.return_value = module
    return ep


def FakeModuleWithOptions():
    module = Mock()
    module.config_options = [
        ConfigOption(name="TestModuleOption", param_type=bool),
        ConfigOption(name="TestModuleAnotherOption", param_type=int, default=3),
    ]
    return module


class DefaultConfigBuilderTest(unittest.TestCase):
    @patch("spectroscope.config.iter_entry_points")
    def test_build_no_modules(self, ep_iter_mock):
        ep_iter_mock.return_value = []
        self.assertEqual(DefaultConfigBuilder.build(), SYSTEM_MODULE_CONFIG)

    @patch("spectroscope.config.iter_entry_points")
    def test_build(self, ep_iter_mock):
        ep_one = Mock()
        ep_one.name = "module_one"
        module_one = Mock()
        module_one.config_options = []
        ep_one.load.return_value = module_one
        ep_two = FakeModuleEntryPoint("module_two", FakeModuleWithOptions())

        ep_iter_mock.return_value = [ep_one, ep_two]
        self.assertEqual(
            DefaultConfigBuilder.build(),
            (lambda d: d.update(SYSTEM_MODULE_CONFIG) or d)(
                {
                    "module_one": [],
                    "module_two": [
                        ConfigOption(name="TestModuleOption", param_type=bool),
                        ConfigOption(
                            name="TestModuleAnotherOption", param_type=int, default=3
                        ),
                    ],
                }
            ),
        )
        ep_one.load.assert_called_once()
        ep_two.load.assert_called_once()
