import itertools
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Optional
from zoneinfo import ZoneInfo

DAILY_CAP = 3
DEFAULT_QUIET = (time(22, 0), time(7, 0))


class AlertError(Exception):
    pass


@dataclass
class Alert:
    alert_id: str
    user: str
    symbol: str
    condition: str
    threshold: Decimal
    recurring: bool
    armed: bool = True
    active: bool = True


@dataclass
class Notification:
    notification_id: int
    user: str
    alert_id: str
    price: Decimal
    created_at: datetime
    deliver_at: Optional[datetime]
    status: str


class AlertService:
    def __init__(self):
        self.users = {}
        self.alerts = {}
        self.last_price = {}
        self.notifications = []
        self._ids = itertools.count(1)

    def add_user(self, user, tz, quiet=DEFAULT_QUIET):
        self.users[user] = (ZoneInfo(tz), quiet)

    def create(self, alert_id, user, symbol, condition, threshold, recurring=False):
        if user not in self.users or condition not in ("ABOVE", "BELOW"):
            raise AlertError("bad alert")
        alert = Alert(alert_id, user, symbol, condition, Decimal(str(threshold)), recurring)
        self.alerts[alert_id] = alert
        return alert

    @staticmethod
    def _holds(alert, price):
        if alert.condition == "ABOVE":
            return price > alert.threshold
        return price <= alert.threshold

    def _deliver_at(self, user, at):
        tz, (start, end) = self.users[user]
        local = at.astimezone(tz)
        if start <= local.time() < end:
            release = local.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
            if release <= local:
                release += timedelta(days=1)
            return release
        return at

    def _notify(self, alert, price, at):
        today = [n for n in self.notifications if n.created_at.date() == at.date() and n.status != "SUPPRESSED"]
        status = "SUPPRESSED" if len(today) >= DAILY_CAP else "SCHEDULED"
        deliver_at = self._deliver_at(alert.user, at) if status == "SCHEDULED" else None
        n = Notification(next(self._ids), alert.user, alert.alert_id, price, at, deliver_at, status)
        self.notifications.append(n)
        return n

    def on_tick(self, symbol, price, at):
        price = Decimal(str(price))
        fired = []
        for alert in self.alerts.values():
            if alert.symbol != symbol or not alert.active:
                continue
            if self._holds(alert, price):
                if alert.armed:
                    fired.append(self._notify(alert, price, at))
                    alert.armed = False
            else:
                alert.armed = True
        self.last_price[symbol] = price
        return fired
