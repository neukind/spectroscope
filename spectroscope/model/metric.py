from pydantic import BaseModel
from spectroscope.model import ChainTimestamp, ValidatorIdentity
from typing import List, Optional
from uuid import UUID


class ValidatorMetricsUpdate(Event):
    class ValidatorMetrics(BaseModel):
        uuid: UUID
        identity: ValidatorIdentity
        balance: Optional[int]
        effectiveBalance: Optional[int]
        inclusionDistance: Optional[int]

    timestamp: ChainTimestamp
    validatorMetrics: List[ValidatorMetrics]
