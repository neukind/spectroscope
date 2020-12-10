from alert_sink.alert_sink import AlertSink
from alertaclient.api import Client

BEACON_CHAIN_URL = "https://mainnet.beaconcha.in/validator/"


class Alerter(AlertSink):
    _ENVIRONMENT = "Production"
    _RESOURCE = "Eth2Staking"

    def __init__(self, alerta_api_token: str):
        self.client = Client(key=alerta_api_token)
        super().__init__()

    def alert(self, idx: int, pubkey: bytes, event: str, value: str = None):
        self.client.send_alert(
            environment=self._ENVIRONMENT,
            resource="{}-{}".format(self._RESOURCE, idx),
            severity="major",
            event=event,
            value=value,
            text="{}{}".format(BEACON_CHAIN_URL, idx),
            attributes={"pubkey": pubkey.hex()},
        )

    def clear(self, idx: int, pubkey: bytes, event: str):
        self.client.send_alert(
            environment=self._ENVIRONMENT,
            resource="{}-{}".format(self._RESOURCE, idx),
            event=event,
            status="closed",
            text="{}{}".format(BEACON_CHAIN_URL, idx),
            attributes={"pubkey": pubkey.hex()},
        )