import enum
from ethereumapis.v1alpha1.validator_pb2 import ValidatorStatus
from pydantic import BaseModel
from spectroscope.model import Event, ChainTimestamp, ValidatorIdentity, Action
from typing import List
import datetime

class Update(Event):
    pass
class ValidatorStatusUpdate(Update):
    status: int

class ValidatorBalanceUpdate(Update):
    balance: int

class ValidatorActivationUpdate(Update):
    status: int

class DatabaseUpdate(Update):
    status: int
    update_type: int
    validator_keys: List[str]
class ActivationBatch(BaseModel):
    validator: ValidatorIdentity
    activation_epoch: int
    updates: List[Update]

class UpdateBatch(BaseModel):
    validator: ValidatorIdentity
    timestamp: ChainTimestamp
    updates: List[Update]

class DatabaseBatch(BaseModel):
    updates: List[Update]
