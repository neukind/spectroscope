from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Event(BaseModel):
    pass


class Action(Event):
    pass


class ChainTimestamp(BaseModel):
    epoch: int
    slot: int
    timestamp: Optional[datetime] = None


class ValidatorIdentity(BaseModel):
    idx: int
    pubkey: bytes
