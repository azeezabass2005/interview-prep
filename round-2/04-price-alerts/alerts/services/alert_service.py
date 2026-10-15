from decimal import Decimal, InvalidOperation

from ..config import DIRECTIONS
from ..db import Database
from ..errors import NotFound, ValidationError
from ..repositories.alerts import AlertRepository


class AlertService:
    def __init__(self, db: Database, clock):
        self._alerts = AlertRepository(db)
        self._clock = clock

    def create_alert(self, user_id: str, payload: dict):
        try:
            threshold = Decimal(str(payload["threshold"]))
            symbol = payload["symbol"].upper()
            direction = payload["direction"]
        except (KeyError, InvalidOperation):
            raise ValidationError("symbol, direction and numeric threshold are required")
        if direction not in DIRECTIONS or threshold <= 0:
            raise ValidationError("direction must be ABOVE or BELOW and threshold positive")
        return self._alerts.create(user_id, symbol, direction, threshold, self._clock.now())

    def delete_alert(self, user_id: str, alert_id: int) -> None:
        alert = self._alerts.get(alert_id)
        if alert is None or alert.user_id != user_id or not alert.active:
            raise NotFound(str(alert_id))
        self._alerts.deactivate(alert_id)

    def list_alerts(self, user_id: str):
        return self._alerts.for_user(user_id)
