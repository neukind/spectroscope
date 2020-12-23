from alertaclient.api import Client
from spectroscope.model.alert import RaiseAlert, ClearAlert
from spectroscope.plugin import BasePlugin
from typing import List, Union

BEACON_CHAIN_URL = "https://mainnet.beaconcha.in/validator/"
ENVIRONMENT = "Production"
RESOURCE = "Eth2Staking"


class Alerta(BasePlugin):
    _consumed_types = [RaiseAlert, ClearAlert]

    def register(self, **kwargs):
        self._client = Client(key=kwargs["alerta_api_token"])
        self._handlers = {
            RaiseAlert: self._alert,
            ClearAlert: self._clear,
        }

    def _alert(self, idx: int, pubkey: bytes, event: str, value: str = None):
        self._client.send_alert(
            environment=ENVIRONMENT,
            resource="{}-{}".format(RESOURCE, idx),
            severity="major",
            event=event,
            value=value,
            text="{}{}".format(BEACON_CHAIN_URL, idx),
            attributes={"pubkey": pubkey.hex()},
        )

    def _clear(self, idx: int, pubkey: bytes, event: str):
        self._client.send_alert(
            environment=ENVIRONMENT,
            resource="{}-{}".format(RESOURCE, idx),
            event=event,
            status="closed",
            text="{}{}".format(BEACON_CHAIN_URL, idx),
            attributes={"pubkey": pubkey.hex()},
        )

    def consume(self, events: List[Union[RaiseAlert, ClearAlert]]):
        for event in events:
            self._handlers[type(event)](event.alert)