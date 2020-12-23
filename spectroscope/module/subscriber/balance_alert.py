from spectroscope.model.alert import Alert, Action, RaiseAlert, ClearAlert
from spectroscope.model.base import ValidatorIdentity
from spectroscope.model.update import UpdateBatch, ValidatorBalanceUpdate
from spectroscope.subscriber import Subscriber
from typing import List


class BalancePenalty(Alert):
    validator: ValidatorIdentity
    loss: int = 0


class BalanceAlert(Subscriber):
    _consumed_types = [ValidatorBalanceUpdate]

    def register(self, **kwargs):
        self._highest_balances = dict()
        self._alerting_validators = set()
        self._most_recent_epoch = -1
        self._penalty_tolerance = kwargs.get("penalty_tolerance", 0)

    def consume(self, batch: UpdateBatch) -> List[Action]:
        ret = list()

        if batch.timestamp.epoch < self._most_recent_epoch:
            return ret
        self._most_recent_epoch = batch.timestamp.epoch

        pk = batch.validator.pubkey
        for update in batch.updates:
            if pk in self._highest_balances:
                hb = self._highest_balances[pk]
                if update.balance > hb:
                    if pk in self._alerting_validators:
                        ret.append(
                            ClearAlert(BalancePenalty(validator=batch.validator))
                        )
                        self._alerting_validators.remove(pk)
                    self._highest_balances[pk] = update.balance
                elif update.balance <= hb - self._penalty_tolerance:
                    ret.append(
                        RaiseAlert(
                            BalancePenalty(
                                validator=batch.validator, loss=hb - update.balance
                            )
                        )
                    )
                    self._alerting_validators.add(pk)
            else:
                self._highest_balances[pk] = update.balance

        return ret


SPECTROSCOPE_MODULE = BalanceAlert