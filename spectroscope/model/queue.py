from spectroscope.model.update import Update
from pydantic import BaseModel
from typing import List
class Publish(BaseModel):
    pass

class ValKeys(Publish):
    validator_keys:List[bytes]
    def get_keys(self):
        return self.validator_keys

class AddKeys(ValKeys):
    pass

class DelKeys(ValKeys):
    def __init__(self, validator_keys):
        super().__init__(validator_keys)
    pass

class ActivatedKeys(ValKeys):
    def __init__(self, validator_keys):
        super().__init__(validator_keys)
    pass

