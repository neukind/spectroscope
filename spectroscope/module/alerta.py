from alertaclient.api import Client
from spectroscope.model.alert import Action, RaiseAlert, ClearAlert
from spectroscope.module import ConfigOption, Plugin
from typing import Callable, List, Type, Union

BEACON_CHAIN_URL = "https://mainnet.beaconcha.in/validator/"
ENVIRONMENT = "Production"
RESOURCE = "Eth2Staking"


class Alerta(Plugin):
    _consumed_types = [RaiseAlert, ClearAlert]

    config_options = [
        ConfigOption(
            name="endpoint",
            param_type=str,
            description="URI endpoint for Alerta API",
            default="http://localhost:8080",
        ),
        ConfigOption(
            name="api_key",
            param_type=str,
            description="API key for connecting to Alerta",
        ),
    ]

    def __init__(self, client: Client):
        self._client = client
        self._handlers = {
            RaiseAlert: self._alert,
            ClearAlert: self._clear,
        }

    @classmethod
    def register(cls, **kwargs):
        return cls(
            client=Client(endpoint=kwargs["endpoint"], key=kwargs["api_key"]),
        )

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
            self._handlers[type(event)](**event.alert.get_dict())
