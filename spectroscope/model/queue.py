from spectroscope.model.update import Update
from pydantic import BaseModel
from typing import List, Set


class Publish(BaseModel):
    pass


class ValKeys(Publish):
    validator_keys: Set[bytes]

    def get_keys(self):
        return self.validator_keys


class AddKeys(ValKeys):
    pass


class DelKeys(ValKeys):
    pass


class ActivatedKeys(ValKeys):
    pass
