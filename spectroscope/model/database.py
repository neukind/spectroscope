import enum
from ethereumapis.v1alpha1.validator_pb2 import ValidatorStatus
from pydantic import BaseModel
from spectroscope.model import Event, ChainTimestamp, ValidatorIdentity, Action
from typing import List
import datetime

class Database(BaseModel):
    update_type: int
    validator_keys: List[str]
    status: int
    def get_dict(self):
        vals = dict()
        vals['update_type'] = self.update_type
        vals['validator_keys'] = self.validator_keys
        vals['status'] = self.status
        return vals

class DatabaseAction(Action):
    update: Database
    def __init__(self, update: Database):
        super().__init__(update=update)

class RaiseUpdateKeys(DatabaseAction):
    pass
