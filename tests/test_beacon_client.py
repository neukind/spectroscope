import unittest
from unittest.mock import Mock, call

from ethereumapis.v1alpha1 import beacon_chain_pb2, validator_pb2
from spectroscope.beacon_client import BeaconChainStreamer
from spectroscope.model import ChainTimestamp, Event, ValidatorIdentity
from spectroscope.model.update import (
    ValidatorBalanceUpdate,
    ValidatorStatusUpdate,
    UpdateBatch,
)
from spectroscope.module import ConfigOption, Module, Plugin, Subscriber
from typing import List, Type, Union


def TestModuleFactory(
    module_type: Union[Type[Plugin], Type[Subscriber]],
    init: Mock = Mock(),
    consume: Mock = Mock(),
    consumed_types: List[Event] = [],
):
    class TestModule(module_type):
        config_options: List[ConfigOption] = []

        _consumed_types: List[Event] = consumed_types

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

    def test_generate_messages(self):
        validator_set = [bytes.fromhex("a" * 96)]
        bcs = BeaconChainStreamer(self.stub_mock, [])
        bcs.add_validators(validator_set)

        bcs.stream()

        self.stub_mock.StreamValidatorsInfo.assert_called_once()
        vcs_generator = self.stub_mock.StreamValidatorsInfo.call_args[0][0]
        self._assert_validator_change_set(vcs_generator, validator_set)

    def test_stream_messages_e2e(self):
        consume_mock = Mock()
        consume_mock.return_value = []
        subscriber = TestSubscriberFactory(
            consume=consume_mock,
            consumed_types=[ValidatorStatusUpdate, ValidatorBalanceUpdate],
        )
        plugin = TestPluginFactory()
        self.stub_mock.StreamValidatorsInfo.return_value = [
            validator_pb2.ValidatorInfo(
                public_key=bytes.fromhex("a" * 96),
                index=60,
                balance=300,
                epoch=123,
                status=2,
            )
        ]

        bcs = BeaconChainStreamer(self.stub_mock, [(subscriber, {}), (plugin, {})])
        bcs.stream()
        consume_mock.assert_called_once_with(
            UpdateBatch(
                validator=ValidatorIdentity(idx=60, pubkey=bytes.fromhex("a" * 96)),
                timestamp=ChainTimestamp(epoch=123, slot=0, timestamp=None),
                updates=[
                    ValidatorStatusUpdate(status=2),
                    ValidatorBalanceUpdate(balance=300),
                ],
            )
        )

    def test_subscriber_activation(self):
        init_mock = Mock()
        module_set = [(TestSubscriberFactory(init=init_mock), {})]
        bcs = BeaconChainStreamer(self.stub_mock, module_set)
        init_mock.assert_called_once()

    def test_plugin_activation(self):
        init_mock = Mock()
        module_set = [(TestPluginFactory(init=init_mock), {})]
        bcs = BeaconChainStreamer(self.stub_mock, module_set)
        init_mock.assert_called_once()

    def test_module_rejection(self):
        module_set = [(Module, {})]
        with self.assertRaises(TypeError):
            bcs = BeaconChainStreamer(self.stub_mock, module_set)

    def test_add_remove_validators(self):
        validator_one = bytes.fromhex("a" * 96)
        validator_two = bytes.fromhex("b" * 96)

        bcs = BeaconChainStreamer(self.stub_mock, [])
        bcs.add_validators([validator_one])
        self.assertSetEqual(bcs.validator_set, set([validator_one]))
        bcs.add_validators([validator_two])
        self.assertSetEqual(bcs.validator_set, set([validator_one, validator_two]))
        bcs.remove_validators([validator_one])
        self.assertSetEqual(bcs.validator_set, set([validator_two]))
        bcs.remove_validators([validator_two])
        self.assertSetEqual(bcs.validator_set, set())
        with self.assertRaises(KeyError):
            bcs.remove_validators([validator_one])
