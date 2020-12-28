import unittest
from unittest.mock import Mock, patch

from spectroscope.config import DefaultConfigBuilder, SYSTEM_MODULE_CONFIG
from spectroscope.module import ConfigOption


class DefaultConfigBuilderTest(unittest.TestCase):
    @patch("spectroscope.config.iter_entry_points")
    def test_build_no_modules(self, ep_iter_mock):
        ep_iter_mock.return_value = []
        self.assertEquals(DefaultConfigBuilder.build(), SYSTEM_MODULE_CONFIG)

    @patch("spectroscope.config.iter_entry_points")
    def test_build(self, ep_iter_mock):
        ep_one = Mock()
        ep_one.name = "ModuleOne"
        module_one = Mock()
        module_one.config_options = []
        ep_one.load.return_value = module_one
        ep_two = Mock()
        ep_two.name = "ModuleTwo"
        module_two = Mock()
        module_two.config_options = [
            ConfigOption(name="TestModuleTwoOption", param_type=bool),
            ConfigOption(name="TestModuleTwoAnotherOption", param_type=int),
        ]
        ep_two.load.return_value = module_two

        ep_iter_mock.return_value = [ep_one, ep_two]
        self.maxDiff = None
        self.assertEquals(
            DefaultConfigBuilder.build(),
            (lambda d: d.update(SYSTEM_MODULE_CONFIG) or d)(
                {
                    "ModuleOne": [],
                    "ModuleTwo": [
                        ConfigOption(name="TestModuleTwoOption", param_type=bool),
                        ConfigOption(name="TestModuleTwoAnotherOption", param_type=int),
                    ],
                }
            ),
        )
        ep_one.load.assert_called_once()
        ep_two.load.assert_called_once()
