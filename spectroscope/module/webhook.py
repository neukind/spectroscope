import requests
from spectroscope.model import Action
from spectroscope.model.notification import Notify
from spectroscope.module import ConfigOption, Plugin
from typing import List


class Webhook(Plugin):
    _consumed_types = [Notify]

    config_options = [
        ConfigOption(
            name="uri_endpoint", param_type=str, description="Endpoint to call webhook from"
        )
    ]

    def __init__(self, uri_endpoint: str):
        self._uri_endpoint = uri_endpoint

    @classmethod
    def register(cls, **kwargs):
        return cls(kwargs["uri_endpoint"])

    def consume(self, events: List[Action]):
        for event in events:
            print(event)
