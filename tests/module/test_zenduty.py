import unittest
from unittest.mock import Mock, patch

from spectroscope.model import ValidatorIdentity
from spectroscope.model.alert import Alert, ClearAlert, RaiseAlert
from spectroscope.module.zenduty import Zenduty

FAKE_PUBKEY = "a" * 96


class FakeAlert(Alert):
    alert_type: str = "FakeAlert"

    def get_value(self):
        return "FakeValue"

    @classmethod
    def get(cls):
        return cls(
            validator=ValidatorIdentity(pubkey=bytes.fromhex(FAKE_PUBKEY), idx=0),
        )


class ZendutyTest(unittest.TestCase):
    API_KEY = "fake_api_key"

    def setUp(self):
        self.zenduty_mock = Mock()
        self.zenduty_mock.create_event.return_value = None

    def tearDown(self):
        pass

    def test_register(self):
        zenduty = Zenduty.register(api_key=self.API_KEY)

    def test_raise_alert(self):
        zenduty = Zenduty(key=self.API_KEY, client=self.zenduty_mock)
        zenduty.consume([RaiseAlert(FakeAlert.get())])
        self.zenduty_mock.create_event.assert_called_once_with(
            self.API_KEY,
            {
                "message": "{} on {}-{}".format("FakeAlert", "Eth2Staking", 0),
                "alert_type": "error",
                "summary": "https://mainnet.beaconcha.in/validator/0",
                "payload": {
                    "value": "FakeValue",
                    "pubkey": FAKE_PUBKEY,
                },
                "entity_id": FAKE_PUBKEY,
            },
        )

    def test_clear_alert(self):
        zenduty = Zenduty(key=self.API_KEY, client=self.zenduty_mock)
        zenduty.consume([ClearAlert(FakeAlert.get())])
        self.zenduty_mock.create_event.assert_called_once_with(
            self.API_KEY,
            {
                "message": "{} on {}-{}".format("FakeAlert", "Eth2Staking", 0),
                "alert_type": "resolved",
                "summary": "https://mainnet.beaconcha.in/validator/0",
                "payload": {
                    "pubkey": FAKE_PUBKEY,
                },
                "entity_id": FAKE_PUBKEY,
            },
        )
