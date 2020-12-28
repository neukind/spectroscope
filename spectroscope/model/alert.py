from pydantic import BaseModel
from spectroscope.model import Action


class Alert(BaseModel):
    pass


class AlertAction(Action):
    alert: Alert

    def __init__(self, alert: Alert):
        super().__init__(alert=alert)


class RaiseAlert(AlertAction):
    pass


class ClearAlert(AlertAction):
    pass
