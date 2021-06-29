from enum import Enum
class ActionTypes(Enum):
        ADD = 1
        UP = 2
        DEL = 3

class ValidatorStatus(Enum):
        UNKNOWN_STATUS = 0
        DEPOSITED = 1
        PENDING = 2
        ACTIVE = 3
        EXITING = 4
        SLASHING = 5
        EXITED = 6
        INVALID = 7
        PARTIALLY_DEPOSITED = 8