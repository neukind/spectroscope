import unittest
from unittest.mock import Mock, patch

from spectroscope.model import ValidatorIdentity
from spectroscope.model.notification import Notification, Notify
from spectroscope.module.webhook import Webhook

FAKE_PUBKEY = "a" * 96


class FakeNotification(Notification):
    pass


class WebhookTest(unittest.TestCase):
    def setUp(self):
        self.requests_mock = Mock()

    def tearDown(self):
        pass
