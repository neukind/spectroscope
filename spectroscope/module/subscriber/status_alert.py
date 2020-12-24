from spectroscope.model.alert import Alert, Action, RaiseAlert
from spectroscope.model.base import ValidatorIdentity
from spectroscope.model.notification import Notification, Notify
from spectroscope.model.update import UpdateBatch, ValidatorStatusUpdate
from spectroscope.module.subscriber import Subscriber
from typing import List


class StatusChange(Alert, Notification):
    previousStatus: int
    currentStatus: int


class StatusAlert(Subscriber):
    _consumed_types = [ValidatorStatusUpdate]

    def __init__(self, notify_when_enter: List[int], alert_when_exit: List[int]):
        self._statuses = dict()
        self._most_recent_epoch = -1
        self._notify_when_enter = notify_when_enter
        self._alert_when_exit = alert_when_exit

    @classmethod
    def register(cls, **kwargs):
        return cls(
            notify_when_enter=kwargs.get("notify_when_enter", [1]),
            alert_when_exit=kwargs.get("alert_when_exit", [2, 3]),
        )

    def consume(self, batch: UpdateBatch) -> List[Action]:
        ret = list()

        if batch.timestamp.epoch < self._most_recent_epoch:
            return ret
        self._most_recent_epoch = batch.timestamp.epoch

        pk = batch.validator.pubkey
        for update in batch.updates:
            if pk in self._statuses:
                if update.status != self._statuses[pk]:
                    status_change = StatusChange(
                        validator=batch.validator,
                        previousStatus=self._statuses[pk],
                        currentStatus=update.status,
                    )
                    if update.status in self._notify_when_enter:
                        ret.append(Notify(status_change))
                    if (
                        self._statuses[pk] in self._alert_when_exit
                        and update.status not in self._alert_when_exit
                    ):
                        ret.append(RaiseAlert(status_change))
            else:
                self._statuses[pk] = update.status

        return ret


SPECTROSCOPE_MODULE = StatusAlert
