from datetime import datetime
from pydantic import BaseModel


class Action:
    pass


class ChainTimestamp(BaseModel):
    epoch: int
    slot: int
    timestamp: datetime = None


class ValidatorIdentity(BaseModel):
    idx: int
    pubkey: bytes
