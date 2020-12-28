import unittest

from spectroscope.model import ChainTimestamp, ValidatorIdentity
from spectroscope.model.alert import ClearAlert, RaiseAlert
from spectroscope.model.update import UpdateBatch, ValidatorBalanceUpdate
from spectroscope.module.balance_alert import BalanceAlert, BalancePenalty


class BalanceAlertTest(unittest.TestCase):
    def setUp(self):
        self.validator_one = ValidatorIdentity(pubkey=bytes.fromhex("a" * 96), idx=0)
        self.validator_two = ValidatorIdentity(pubkey=bytes.fromhex("b" * 96), idx=1)
        self.validator_three = ValidatorIdentity(pubkey=bytes.fromhex("c" * 96), idx=2)

    def tearDown(self):
        pass

    def test_register(self):
        ba = BalanceAlert.register()
        self.assertEquals(ba._penalty_tolerance, 0)

    def test_consume_single(self):
        ba = BalanceAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=0, slot=0),
            updates=[ValidatorBalanceUpdate(balance=0)],
        )
        self.assertEquals(ba.consume(update), [])

    def test_consume_multiple(self):
        ba = BalanceAlert.register()
        updates = [
            UpdateBatch(
                validator=self.validator_one,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorBalanceUpdate(balance=100)],
            ),
            UpdateBatch(
                validator=self.validator_two,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorBalanceUpdate(balance=200)],
            ),
            UpdateBatch(
                validator=self.validator_three,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorBalanceUpdate(balance=300)],
            ),
        ]

        self.assertListEqual([ba.consume(update) for update in updates], [[], [], []])

    def test_alert_clear_single(self):
        ba = BalanceAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=0, slot=0),
            updates=[ValidatorBalanceUpdate(balance=500)],
        )
        self.assertEquals(ba.consume(update), [])

        alert_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=1, slot=32),
            updates=[ValidatorBalanceUpdate(balance=499)],
        )
        self.assertEquals(
            ba.consume(alert_update),
            [RaiseAlert(BalancePenalty(validator=self.validator_one, loss=1))],
        )

        noop_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=2, slot=64),
            updates=[ValidatorBalanceUpdate(balance=500)],
        )
        self.assertEquals(ba.consume(noop_update), [])

        clear_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=3, slot=96),
            updates=[ValidatorBalanceUpdate(balance=501)],
        )
        self.assertEquals(
            ba.consume(clear_update),
            [ClearAlert(BalancePenalty(validator=self.validator_one))],
        )

    def test_ignore_history_rewrite(self):
        ba = BalanceAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=2, slot=64),
            updates=[ValidatorBalanceUpdate(balance=500)],
        )
        self.assertEquals(ba.consume(update), [])

        alert_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=1, slot=32),
            updates=[ValidatorBalanceUpdate(balance=0)],
        )
        self.assertEquals(ba.consume(alert_update), [])
