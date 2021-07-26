from spectroscope.model.alert import Alert, Action, RaiseAlert
from spectroscope.model import Event, ValidatorIdentity
from spectroscope.model.notification import Notification, Notify
from spectroscope.model.update import ActivationBatch, ValidatorActivationUpdate
from spectroscope.module import Subscriber
from typing import Dict, List
from ethereumapis.v1alpha1.validator_pb2 import _VALIDATORSTATUS


class DepositStatusChange(Alert, Notification):
    alert_type: str = "DepositStatusChange"
    previousStatus: int
    currentStatus: int

    def get_value(self):
        return "{} -> {}".format(self.previousStatus, self.currentStatus)


class ActivationAlert(Subscriber):
    _consumed_types = [ValidatorActivationUpdate]

    def __init__(self, notify_when_enter: List[int], alert_when_exit: List[int]):
        self._statuses: Dict[bytes, int] = dict()
        self._notify_when_enter = notify_when_enter
        self._alert_when_exit = alert_when_exit

    @classmethod
    def register(cls, **kwargs):
        return cls(
            notify_when_enter=kwargs.get("notify_when_enter", [1]),
            alert_when_exit=kwargs.get("alert_when_exit", [2, 3]),
        )

    def consume(self, batch: ActivationBatch) -> List[Action]:
        ret: List[Action] = list()
        pk = batch.validator.pubkey
        for update in batch.updates:
            if update.status:
                if pk in self._statuses:
                    if update.status != self._statuses[pk]:
                        status_change = DepositStatusChange(
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
                        self._statuses[pk] = update.status
                else:
                    self._statuses[pk] = update.status
        return ret


# the current issue is that the WaitForActivation stream will go from DEPOSITED to ACTIVE directly, without going to Pending.
# seems like the current ethereumapis api will provide the status from the pending status only.
# During the actual DEPOSITED state of the validator, the stream will be returning a blank status, labelled "UNKNOWN_STATUS".
