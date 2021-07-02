
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
    def __init__(self,val_count):
        self.val_count: int = val_count
    def need_update(self):
        return self.val_count

class NewKeys(NewValidatorList):
    pass