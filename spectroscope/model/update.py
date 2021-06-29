import enum
from ethereumapis.v1alpha1.validator_pb2 import ValidatorStatus
from pydantic import BaseModel
from spectroscope.model import Event, ChainTimestamp, ValidatorIdentity, Action
from typing import List
import datetime

class Update(Event):
    pass

class UpdateAction(Action):
    update: Update
    update_type: int
    validator_keys: List[str]
    status: int
    def __init__(self, update: Update):
        super().__init__(update=update)

    def get_dict(self):
        vals = dict()
        vals['update_type'] = self.update_type
        vals['validator_keys'] = self.validator_keys
        vals['status'] = self.status
        return vals

class RaiseUpdate(UpdateAction):
    pass

class ValidatorAddUpdate():
    pass

class ValidatorUpUpdate():
    pass

class ValidatorDelUpdate():
    pass

class ValidatorStatusUpdate(Update):
    status: int


class ValidatorBalanceUpdate(Update):
    balance: int

class ValidatorActivationUpdate(Update):
    status: int

class ActivationBatch(BaseModel):
    validator: ValidatorIdentity
    activation_epoch: int
    updates: List[Update]

class UpdateBatch(BaseModel):
    validator: ValidatorIdentity
    timestamp: ChainTimestamp
    updates: List[Update]

class UpdateDatabase(BaseModel):
    validator_keys: List[str]
    status: int
    update_type: int

