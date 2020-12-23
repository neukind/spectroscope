from pydantic import BaseModel
from spectroscope.model.base import Action


class Notification(BaseModel):
    pass


class Notify(Action):
    def __init__(self, notification: Notification):
        self.notification = notification
        super().__init__()
