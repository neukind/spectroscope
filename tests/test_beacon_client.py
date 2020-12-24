import unittest
from unittest.mock import Mock
from nose2.tools import params

from ethereumapis.v1alpha1 import beacon_chain_pb2
from spectroscope.beacon_client import BeaconChainStreamer
from spectroscope.model.base import Event
from spectroscope.module import ConfigOption, Plugin, Subscriber
from typing import List, Type, Union


def TestModuleFactory(
    module_type: Union[Type[Plugin], Type[Subscriber]],
    init: Mock = Mock(),
    consume: Mock = Mock(),
):
    class TestModule(module_type):
        config_options: List[ConfigOption] = []

        _consumed_types: List[Event] = []

        def __init__(self, **kwargs):
            init(**kwargs)

        @classmethod
        def register(cls, **kwargs):
            return cls(**kwargs)

        def consume(self, updates: List[Event]):
            return consume(updates)

    return TestModule


TestPluginFactory = lambda *a, **kw: TestModuleFactory(Plugin, *a, **kw)
TestSubscriberFactory = lambda *a, **kw: TestModuleFactory(Subscriber, *a, **kw)


class BeaconChainStreamerTest(unittest.TestCase):
    def setUp(self):
        self.stub_mock = Mock()
        self.stub_mock.StreamValidatorsInfo.return_value = []

    def tearDown(self):
        pass

    def _assert_validator_change_set(self, generator, validator_set):
        self.assertEqual(
            next(generator),
            beacon_chain_pb2.ValidatorChangeSet(
                action=beacon_chain_pb2.SET_VALIDATOR_KEYS,
                public_keys=validator_set,
            ),
        )
        with self.assertRaises(StopIteration):
            next(generator)

    @params([])
    def test_generate_messages(self, validator_set):
        bcs = BeaconChainStreamer(self.stub_mock, [])
        bcs.add_validators(validator_set)

        bcs.stream()

        self.stub_mock.StreamValidatorsInfo.assert_called_once()
        vcs_generator = self.stub_mock.StreamValidatorsInfo.call_args[0][0]
        self._assert_validator_change_set(vcs_generator, validator_set)

    def test_subscriber_activation(self):
        init_mock = Mock()
        module_set = [(TestSubscriberFactory(init=init_mock), {})]
        bcs = BeaconChainStreamer(self.stub_mock, module_set)
        init_mock.assert_called_once()

    def test_plugin_activation(self):
        module_set = [(TestPluginFactory(init=Mock(), consume=Mock()), {})]
        bcs = BeaconChainStreamer(self.stub_mock, module_set)

    def test_add_validators(self):
        pass

    def test_remove_validators(self):
        pass
