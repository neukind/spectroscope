import unittest

from spectroscope.model import ChainTimestamp, ValidatorIdentity
from spectroscope.model.alert import RaiseAlert
from spectroscope.model.notification import Notify
from spectroscope.model.update import UpdateBatch, ValidatorStatusUpdate
from spectroscope.module.status_alert import StatusAlert, StatusChange


class StatusAlertTest(unittest.TestCase):
    def setUp(self):
        self.validator_one = ValidatorIdentity(pubkey=bytes.fromhex("a" * 96), idx=0)
        self.validator_two = ValidatorIdentity(pubkey=bytes.fromhex("b" * 96), idx=1)
        self.validator_three = ValidatorIdentity(pubkey=bytes.fromhex("c" * 96), idx=2)

    def tearDown(self):
        pass

    def test_defaults(self):
        sa = StatusAlert.register()
        self.assertEquals(sa._notify_when_enter, [1])
        self.assertEquals(sa._alert_when_exit, [2, 3])

    def test_consume_single(self):
        sa = StatusAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=0, slot=0),
            updates=[ValidatorStatusUpdate(status=0)],
        )
        self.assertEquals(sa.consume(update), [])

    def test_consume_multiple(self):
        sa = StatusAlert.register()
        updates = [
            UpdateBatch(
                validator=self.validator_one,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorStatusUpdate(status=1)],
            ),
            UpdateBatch(
                validator=self.validator_two,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorStatusUpdate(status=2)],
            ),
            UpdateBatch(
                validator=self.validator_three,
                timestamp=ChainTimestamp(epoch=0, slot=0),
                updates=[ValidatorStatusUpdate(status=3)],
            ),
        ]

        self.assertListEqual([sa.consume(update) for update in updates], [[], [], []])

    def test_notify_single(self):
        sa = StatusAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=0, slot=0),
            updates=[ValidatorStatusUpdate(status=0)],
        )
        self.assertEquals(sa.consume(update), [])

        activation_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=1, slot=32),
            updates=[ValidatorStatusUpdate(status=1)],
        )
        self.assertEquals(
            sa.consume(activation_update),
            [
                Notify(
                    StatusChange(
                        validator=self.validator_one, previousStatus=0, currentStatus=1
                    )
                )
            ],
        )

    def test_alert_single(self):
        sa = StatusAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=0, slot=0),
            updates=[ValidatorStatusUpdate(status=2)],
        )
        self.assertEquals(sa.consume(update), [])

        activation_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=1, slot=32),
            updates=[ValidatorStatusUpdate(status=3)],
        )
        self.assertEquals(sa.consume(activation_update), [])

        alert_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=2, slot=64),
            updates=[ValidatorStatusUpdate(status=4)],
        )
        self.assertEquals(
            sa.consume(alert_update),
            [
                RaiseAlert(
                    StatusChange(
                        validator=self.validator_one, previousStatus=3, currentStatus=4
                    )
                )
            ],
        )

    def test_ignore_history_rewrite(self):
        sa = StatusAlert.register()
        update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=2, slot=64),
            updates=[ValidatorStatusUpdate(status=3)],
        )
        self.assertEquals(sa.consume(update), [])

        alert_update = UpdateBatch(
            validator=self.validator_one,
            timestamp=ChainTimestamp(epoch=1, slot=32),
            updates=[ValidatorStatusUpdate(status=4)],
        )
        self.assertEquals(sa.consume(alert_update), [])
