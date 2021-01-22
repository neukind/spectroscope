import unittest
from unittest.mock import Mock, patch

from spectroscope.model import ValidatorIdentity
from spectroscope.model.notification import Notification, Notify
from spectroscope.module.webhook import Webhook

FAKE_PUBKEY = "a" * 96
FAKE_ENDPOINT = "http://www.example.com/api"


class FakeNotification(Notification):
    value: str = "Foo"


class WebhookTest(unittest.TestCase):
    def setUp(self):
        self.webhook = Webhook(FAKE_ENDPOINT)

    @patch("spectroscope.module.webhook.requests")
    def testNotifyOnce(self, requests_mock):
        self.webhook.consume([Notify(notification=FakeNotification())])
        requests_mock.post.assert_called_once_with(FAKE_ENDPOINT, json={"value": "Foo"})
