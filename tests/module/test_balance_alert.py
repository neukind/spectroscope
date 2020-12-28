import unittest

from spectroscope.module.balance_alert import BalanceAlert


class BalanceAlertTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register(self):
        ba = BalanceAlert.register()
