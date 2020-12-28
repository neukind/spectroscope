from ethereumapis.v1alpha1.validator_pb2 import ValidatorStatus
from pydantic import BaseModel
from spectroscope.model import Event, ChainTimestamp, ValidatorIdentity
from typing import List


class Update(Event):
    pass


class ValidatorStatusUpdate(Update):
    status: int


class ValidatorBalanceUpdate(Update):
    balance: int


class UpdateBatch(BaseModel):
    validator: ValidatorIdentity
    timestamp: ChainTimestamp
    updates: List[Update]
