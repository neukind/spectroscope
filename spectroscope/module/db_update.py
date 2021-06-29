from spectroscope.model.update import DatabaseUpdate, Update, DatabaseBatch, Action, RaiseUpdate
from spectroscope.module import Subscriber
from typing import Dict, List, Set


class UpdateKey(DatabaseUpdate):
    pass

class DbUpdate(Subscriber):
    def __init__(self,db_type):
        self.db_type = db_type

    _consumed_types = [DatabaseUpdate]

    @classmethod
    def register(cls, **kwargs):
        return cls(
            db_type=kwargs.get("db_type", "mongodb"),
        )

    def consume(self, batch: DatabaseBatch) -> List[Action]:
        ret: List[Action] = list()
        for update in batch.updates:
            ret.append(
                RaiseUpdate(
                    update = UpdateKey(
                        validator_keys = update.validator_keys,
                        status = update.status,
                        update_type = update.update_type
                    ),
                )
            )
        return ret

            