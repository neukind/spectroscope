import unittest
from unittest.mock import Mock

from eth.v1alpha1 import beacon_chain_pb2, beacon_chain_pb2_grpc
from client import BalanceWatcher


class BalanceWatcherTest(unittest.TestCase):
    def setUp(self):
        self.alerter_mock = Mock()
        self.stub_mock = Mock()

    def test_generate_messages(self):
        bw = BalanceWatcher(self.stub_mock, self.alerter_mock, [])
        messages = bw._generate_messages()
        self.assertEqual(
            next(messages),
            beacon_chain_pb2.ValidatorChangeSet(
                action=beacon_chain_pb2.SET_VALIDATOR_KEYS,
                public_keys=[],
            ),
        )
        with self.assertRaises(StopIteration):
            next(messages)


class ClientTest(unittest.TestCase):
    pass
