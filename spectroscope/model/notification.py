from pydantic import BaseModel
from spectroscope.model import Action, ValidatorIdentity


class Notification(BaseModel):
    pass


class Notify(Action):
    notification: Notification

    def __init__(self, notification: Notification):
        super().__init__(notification=notification)
