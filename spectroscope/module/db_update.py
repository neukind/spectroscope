from spectroscope.model.update import DatabaseBatch, Action, DatabaseUpdate
from spectroscope.model.database import Database, DatabaseAction, RaiseUpdateKeys
from spectroscope.module import Subscriber
from typing import Dict, List, Set
from spectroscope.constants import enums


class UpdateKey(Database):
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
        status = 0
        for update in batch.updates:
            ret.append(
                RaiseUpdateKeys(
                    update = UpdateKey(
                        validator_keys = update.validator_keys,
                        status = update.status,
                        update_type = update.update_type
                    ),
                )
            )
        return ret

            