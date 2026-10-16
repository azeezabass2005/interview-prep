from decimal import Decimal

from ..config import REARM_FRACTION
from ..db import Database
from ..index import AlertIndex
from ..models import Alert
from ..repositories.alerts import AlertRepository
from ..repositories.deliveries import DeliveryRepository
from ..repositories.users import UserRepository
from .quiet_hours import deliver_after


class Evaluator:

    def __init__(self, db: Database, clock):
        self._alerts = AlertRepository(db)
        self._users = UserRepository(db)
        self._deliveries = DeliveryRepository(db)
        self._index = AlertIndex(self._alerts, clock)
        self._clock = clock

    @staticmethod
    def reached(alert: Alert, price: Decimal) -> bool:
        return price >= alert.threshold if alert.direction == "ABOVE" else price <= alert.threshold

    @staticmethod
    def rearm_level(alert: Alert) -> Decimal:
        if alert.direction == "ABOVE":
            return alert.threshold * (1 - REARM_FRACTION)
        return alert.threshold * (1 + REARM_FRACTION)

    def on_tick(self, symbol: str, price) -> int:
        price = Decimal(str(price))
        enqueued = 0
        for alert in self._index.for_symbol(symbol.upper()):
            if self.reached(alert, price):
                self._fire(alert, price)
                enqueued += 1
        return enqueued

    def _fire(self, alert: Alert, price: Decimal) -> None:
        user = self._users.get(alert.user_id)
        now = self._clock.now()
        message = f"{alert.symbol} is {price} ({alert.direction.lower()} {alert.threshold})"
        self._deliveries.enqueue(alert.alert_id, alert.user_id, message, deliver_after(user, now))
