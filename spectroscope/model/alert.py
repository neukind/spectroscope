from pydantic import BaseModel
from spectroscope.model import Action


class Alert(BaseModel):
    pass


class AlertAction(Action):
    def __init__(self, alert: Alert):
        self.alert = alert
        super().__init__()


class RaiseAlert(AlertAction):
    pass


class ClearAlert(AlertAction):
    pass
