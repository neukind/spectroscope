from spectroscope.model.alert import Alert, Action, RaiseAlert, ClearAlert
from spectroscope.model.notification import Notification, Notify
from spectroscope.model import ValidatorIdentity
from spectroscope.model.update import UpdateBatch, ValidatorBalanceUpdate
from spectroscope.module import Subscriber
from typing import Dict, List, Set


class BalancePenalty(Alert,Notification):
    alert_type: str = "BalancePenalty"
    loss: int = 0

    def get_value(self):
        return self.loss


class BalanceAlert(Subscriber):
    _consumed_types = [ValidatorBalanceUpdate]

    def __init__(self, penalty_tolerance: int):
        self._highest_balances: Dict[bytes, int] = dict()
        self._alerting_validators: Set[bytes] = set()
        self._most_recent_epoch = -1
        self._penalty_tolerance = penalty_tolerance

    @classmethod
    def register(cls, **kwargs):
        return cls(
            penalty_tolerance=kwargs.get("penalty_tolerance", 0),
        )

    def consume(self, batch: UpdateBatch) -> List[Action]:
        ret: List[Action] = list()

        if batch.timestamp.epoch < self._most_recent_epoch:
            return ret
        self._most_recent_epoch = batch.timestamp.epoch

        pk = batch.validator.pubkey
        for update in batch.updates:
            if pk in self._highest_balances:
                hb = self._highest_balances[pk]
                #checking notify functionality
                ret.append(
                            Notify(BalancePenalty(validator=batch.validator, loss = hb - update.balance))
                        )
                ret.append(
                        RaiseAlert(
                            BalancePenalty(
                                validator=batch.validator, loss=hb - update.balance
                            )
                        )
                    )
                # if update.balance > hb:
                #     if pk in self._alerting_validators:
                #         ret.append(
                #             ClearAlert(BalancePenalty(validator=batch.validator))
                #         )
                #         self._alerting_validators.remove(pk)
                #     self._highest_balances[pk] = update.balance
                # elif update.balance < hb - self._penalty_tolerance:
                #     ret.append(
                #         RaiseAlert(
                #             BalancePenalty(
                #                 validator=batch.validator, loss=hb - update.balance
                #             )
                #         )
                #     )
                #     self._alerting_validators.add(pk)
            else:
                self._highest_balances[pk] = update.balance

        return ret
