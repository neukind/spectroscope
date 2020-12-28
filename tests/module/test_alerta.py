import unittest
from unittest.mock import Mock, patch

from spectroscope.model import ValidatorIdentity
from spectroscope.model.alert import Alert, ClearAlert, RaiseAlert
from spectroscope.module.alerta import Alerta

FAKE_PUBKEY = "a" * 96


class FakeAlert(Alert):
    alert_type: str = "FakeAlert"

    @classmethod
    def get(cls):
        return cls(
            validator=ValidatorIdentity(pubkey=bytes.fromhex(FAKE_PUBKEY), idx=0),
        )


class AlertaTest(unittest.TestCase):
    def setUp(self):
        self.alerta_mock = Mock()
        self.alerta_mock.send_alert.return_value = None

    def tearDown(self):
        pass

    @patch("spectroscope.module.alerta.Client")
    def test_register(self, alerta_client_mock):
        endpoint = "http://localhost:8080"
        api_key = "fake_api_key"
        alerta = Alerta.register(endpoint=endpoint, api_key=api_key)
        alerta_client_mock.assert_called_once_with(endpoint=endpoint, key=api_key)

    def test_raise_alert(self):
        alerta = Alerta(self.alerta_mock)
        alerta.consume([RaiseAlert(FakeAlert.get())])
        self.alerta_mock.send_alert.assert_called_once_with(
            environment="Production",
            resource="Eth2Staking-0",
            severity="major",
            event="FakeAlert",
            value=None,
            text="https://mainnet.beaconcha.in/validator/0",
            attributes={"pubkey": FAKE_PUBKEY},
        )

    def test_clear_alert(self):
        alerta = Alerta(self.alerta_mock)
        alerta.consume([ClearAlert(FakeAlert.get())])
        self.alerta_mock.send_alert.assert_called_once_with(
            environment="Production",
            resource="Eth2Staking-0",
            event="FakeAlert",
            status="closed",
            text="https://mainnet.beaconcha.in/validator/0",
            attributes={"pubkey": FAKE_PUBKEY},
        )
