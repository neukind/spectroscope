import unittest
import unittest.mock
import nose2.tools

from ethereumapis.v1alpha1 import beacon_chain_pb2
from spectroscope.beacon_client import BeaconChainStreamer


class BeaconChainStreamerTest(unittest.TestCase):
    def setUp(self):
        self.stub_mock = unittest.mock.Mock()

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

    @nose2.tools.params([])
    def test_streamer_no_modules(self, validator_set):
        bcs = BeaconChainStreamer(self.stub_mock, validator_set)
        self.stub_mock.StreamValidatorsInfo.return_value = []

        bcs.stream()

        self.stub_mock.StreamValidatorsInfo.assert_called_once()
        vcs_generator = self.stub_mock.StreamValidatorsInfo.call_args[0][0]
        self._assert_validator_change_set(vcs_generator, validator_set)
