from spectroscope.model.update import Update, UpdateDatabase, Action, RaiseUpdate
from spectroscope.module import Subscriber
from typing import Dict, List, Set


class UpdateKey(Update):
    pass

class DbUpdate(Subscriber):
    _consumed_types = [UpdateDatabase]

    def consume(self, batch: UpdateDatabase) -> List[Action]:
        ret: List[Action] = list()
        ret.append(
            RaiseUpdate(
                update = UpdateKey(),
                validators = batch.validator_keys,
                status = batch.status,
                update_type = batch.update_type
            )
        )
        return ret

            