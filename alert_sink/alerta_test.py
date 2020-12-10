import unittest
from unittest.mock import Mock

from alert_sink import alerta


class AlertaTest(unittest.TestCase):
    # constants
    API_TOKEN = "fake_api_token"
    VALIDATOR_INDEX = 173
    VALIDATOR_PUBLIC_KEY = bytes.fromhex(
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    ALERT_NAME = "TestAlert"
    ALERT_VALUE = "optional value"

    def setUp(self):
        self.alerta = alerta.Alerter(self.API_TOKEN)
        self.alerta_client_mock = Mock()
        self.alerta.client = self.alerta_client_mock

    def test_alert_with_value(self):
        self.alerta.alert(
            self.VALIDATOR_INDEX,
            self.VALIDATOR_PUBLIC_KEY,
            self.ALERT_NAME,
            self.ALERT_VALUE,
        )
        self.alerta_client_mock.send_alert.assert_called_with(
            environment="Production",
            resource="Eth2Staking-{}".format(self.VALIDATOR_INDEX),
            severity="major",
            event=self.ALERT_NAME,
            value=self.ALERT_VALUE,
            text="{}{}".format(alerta.BEACON_CHAIN_URL, self.VALIDATOR_INDEX),
            attributes={"pubkey": self.VALIDATOR_PUBLIC_KEY.hex()},
        )

    def test_alert_without_value(self):
        self.alerta.alert(
            self.VALIDATOR_INDEX,
            self.VALIDATOR_PUBLIC_KEY,
            self.ALERT_NAME,
        )
        self.alerta_client_mock.send_alert.assert_called_with(
            environment="Production",
            resource="Eth2Staking-{}".format(self.VALIDATOR_INDEX),
            severity="major",
            event=self.ALERT_NAME,
            value=None,
            text="{}{}".format(alerta.BEACON_CHAIN_URL, self.VALIDATOR_INDEX),
            attributes={"pubkey": self.VALIDATOR_PUBLIC_KEY.hex()},
        )

    def test_clear(self):
        self.alerta.clear(
            self.VALIDATOR_INDEX, self.VALIDATOR_PUBLIC_KEY, self.ALERT_NAME
        )
        self.alerta_client_mock.send_alert.assert_called_with(
            environment="Production",
            resource="Eth2Staking-{}".format(self.VALIDATOR_INDEX),
            event=self.ALERT_NAME,
            status="closed",
            text="{}{}".format(alerta.BEACON_CHAIN_URL, self.VALIDATOR_INDEX),
            attributes={"pubkey": self.VALIDATOR_PUBLIC_KEY.hex()},
        )


if __name__ == "__main__":
    unittest.main()