from zenduty import ApiClient, EventsApi
from spectroscope.model.alert import Action, RaiseAlert, ClearAlert
from spectroscope.module import ConfigOption, Plugin
from typing import List

BEACON_CHAIN_URL = "https://mainnet.beaconcha.in/validator/"
RESOURCE = "Eth2Staking"


class Zenduty(Plugin):
    _consumed_types = [RaiseAlert, ClearAlert]

    config_options = [
        ConfigOption(
            name="api_key",
            param_type=str,
            description="Integration key for connecting to Zenduty",
        ),
    ]

    def __init__(self, key: str, client: EventsApi = EventsApi(ApiClient(""))):
        self._client = client
        self._integration_key = key
        self._handlers = {
            RaiseAlert: self._alert,
            ClearAlert: self._clear,
        }

    @classmethod
    def register(cls, **kwargs):
        return cls(key=kwargs["api_key"])

    def _alert(self, idx: int, pubkey: bytes, event: str, value: str = None, **kwargs):
        self._client.create_event(
            self._integration_key,
            {
                "message": "{} on {}-{}".format(event, RESOURCE, idx),
                "alert_type": "error",
                "summary": "{}{}".format(BEACON_CHAIN_URL, idx),
                "payload": {
                    "value": value,
                    "pubkey": pubkey.hex(),
                },
            },
        )

    def _clear(self, idx: int, pubkey: bytes, event: str, **kwargs):
        self._client.create_event(
            self._integration_key,
            {
                "message": "{} on {}-{}".format(event, RESOURCE, idx),
                "alert_type": "resolved",
                "summary": "{}{}".format(BEACON_CHAIN_URL, idx),
                "payload": {
                    "pubkey": pubkey.hex(),
                },
            },
        )

    def consume(self, events: List[Action]):
        for event in events:
            self._handlers[type(event)](**event.alert.get_dict())
