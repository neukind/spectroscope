import unittest
from unittest.mock import Mock, call

from ethereumapis.v1alpha1 import beacon_chain_pb2, validator_pb2
from client import BalanceWatcher


class BalanceWatcherTest(unittest.TestCase):
    TEST_VALIDATOR_SET = [
        ["a" * 96],
    ]

    def setUp(self):
        self.alerter_mock = Mock()
        self.stub_mock = Mock()

    def test_generate_messages_empty_set(self):
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

    def test_generate_messages(self):
        for validator_set in self.TEST_VALIDATOR_SET:
            bw = BalanceWatcher(self.stub_mock, self.alerter_mock, validator_set)
            messages = bw._generate_messages()
            self.assertEqual(
                next(messages),
                beacon_chain_pb2.ValidatorChangeSet(
                    action=beacon_chain_pb2.SET_VALIDATOR_KEYS,
                    public_keys=map(bytes.fromhex, validator_set),
                ),
            )
            with self.assertRaises(StopIteration):
                next(messages)

    def test_stream_validators_empty_set(self):
        self.stub_mock.StreamValidatorsInfo.return_value = []

        bw = BalanceWatcher(self.stub_mock, self.alerter_mock, [])
        bw.stream_validators()

        self.alerter_mock.alert.assert_not_called()
        self.alerter_mock.clear.assert_not_called()

    def test_validator_eth_loss(self):
        for validator_set in self.TEST_VALIDATOR_SET:
            balance = 32000000000
            self.stub_mock.StreamValidatorsInfo.return_value = list()
            for i in range(1, 5):
                for validator in validator_set:
                    self.stub_mock.StreamValidatorsInfo.return_value.append(
                        validator_pb2.ValidatorInfo(
                            public_key=bytes.fromhex(validator), balance=balance
                        )
                    )
                balance -= i * 1000000000

            bw = BalanceWatcher(self.stub_mock, self.alerter_mock, validator_set)
            bw.stream_validators()

            self.alerter_mock.alert.assert_has_calls(
                [
                    call(0, bytes.fromhex("a" * 96), "ValidatorEthLoss", 1.0),
                    call(0, bytes.fromhex("a" * 96), "ValidatorEthLoss", 2.0),
                    call(0, bytes.fromhex("a" * 96), "ValidatorEthLoss", 3.0),
                ]
            )

            self.alerter_mock.clear.assert_not_called()

    def test_validator_eth_loss_clear(self):
        for validator_set in self.TEST_VALIDATOR_SET:
            balance = 32000000000
            self.stub_mock.StreamValidatorsInfo.return_value = list()
            for validator in validator_set:
                self.stub_mock.StreamValidatorsInfo.return_value.append(
                    validator_pb2.ValidatorInfo(
                        public_key=bytes.fromhex(validator), balance=balance
                    )
                )
                self.stub_mock.StreamValidatorsInfo.return_value.append(
                    validator_pb2.ValidatorInfo(
                        public_key=bytes.fromhex(validator),
                        balance=balance - 1000000000,
                    )
                )
                self.stub_mock.StreamValidatorsInfo.return_value.append(
                    validator_pb2.ValidatorInfo(
                        public_key=bytes.fromhex(validator), balance=balance
                    )
                )

                bw = BalanceWatcher(self.stub_mock, self.alerter_mock, validator_set)
                bw.stream_validators()

                self.alerter_mock.alert.assert_has_calls(
                    [
                        call(0, bytes.fromhex("a" * 96), "ValidatorEthLoss", 1.0),
                    ]
                )
                self.alerter_mock.clear.assert_has_calls(
                    [
                        call(0, bytes.fromhex("a" * 96), "ValidatorEthLoss"),
                    ]
                )


class ClientTest(unittest.TestCase):
    pass
