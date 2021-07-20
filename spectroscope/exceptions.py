import enum
from spectroscope.model import update
from typing import List

from google.protobuf.reflection import ParseMessage

class Invalid(Exception):
    pass

class Interrupt(Exception):
    pass
class ValidatorInvalid(Invalid):
    def __init__(self, expression, message):
        self.expression = expression 
        self.message = message

class ValidatorActivated(Interrupt):
    def __init__(self,activated_keys):
        self.activated_keys: list() = activated_keys
    def get_keys(self):
        return self.activated_keys

class NewValidatorList(Interrupt):
    def __init__(self,val_keys):
        self.val_keys: List[str] = val_keys
    def get_keys(self):
        return self.val_keys

class AddKeys(NewValidatorList):
    pass

class DelKeys(NewValidatorList):
    pass

class AddDelKeys(NewValidatorList):
    pass

class NoKeys(NewValidatorList):
    pass