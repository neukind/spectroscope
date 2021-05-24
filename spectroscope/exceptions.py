
class Invalid(Exception):
    pass

class ValidatorInvalid(Invalid):
    def __init__(self, expression, message):
        self.expression = expression 
        self.message = message

class ValidatorActivated(Invalid):
    def __init__(self,activated_keys):
        self.activated_keys: list() = activated_keys
    def get_keys(self):
        return self.activated_keys
