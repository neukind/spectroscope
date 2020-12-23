from ethereumapis.v1alpha1.validator_pb2 import ValidatorStatus
from pydantic import BaseModel
from spectroscope.model.base import ChainTimestamp, ValidatorIdentity
from typing import List


class BaseUpdate(BaseModel):
    pass


class ValidatorStatusUpdate(BaseUpdate):
    status: int


class ValidatorBalanceUpdate(BaseUpdate):
    balance: int


class UpdateBatch(BaseModel):
    validator: ValidatorIdentity
    timestamp: ChainTimestamp
    updates: List[BaseUpdate]