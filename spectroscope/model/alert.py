from pydantic import BaseModel
from spectroscope.model import Action, ValidatorIdentity


class Alert(BaseModel):
    validator: ValidatorIdentity
    alert_type: str

    def get_dict(self):
        vals = dict()
        vals["event"] = self.alert_type
        vals["pubkey"] = self.validator.pubkey
        vals["idx"] = self.validator.idx
        return vals


class AlertAction(Action):
    alert: Alert

    def __init__(self, alert: Alert):
        super().__init__(alert=alert)


class RaiseAlert(AlertAction):
    pass


class ClearAlert(AlertAction):
    pass
