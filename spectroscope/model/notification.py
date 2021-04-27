from pydantic import BaseModel
from spectroscope.model import Action


class Notification(BaseModel):
    pass


class Notify(Action):
    notification: Notification

    def __init__(self, notification: Notification):
        super().__init__(notification=notification)
