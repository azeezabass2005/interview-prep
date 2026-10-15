from collections import defaultdict
from typing import Dict, List

from .config import INDEX_REFRESH_SECONDS
from .models import Alert
from .repositories.alerts import AlertRepository


class AlertIndex:
    """Per-process index of active alerts by symbol. Refreshed from the DB every INDEX_REFRESH_SECONDS."""

    def __init__(self, alerts: AlertRepository, clock):
        self._alerts = alerts
        self._clock = clock
        self._by_symbol: Dict[str, List[Alert]] = {}
        self._loaded_at = None

    def _refresh_if_due(self) -> None:
        now = self._clock.now()
        if self._loaded_at is None or (now - self._loaded_at).total_seconds() >= INDEX_REFRESH_SECONDS:
            by_symbol = defaultdict(list)
            for alert in self._alerts.active():
                by_symbol[alert.symbol].append(alert)
            self._by_symbol = dict(by_symbol)
            self._loaded_at = now

    def for_symbol(self, symbol: str) -> List[Alert]:
        self._refresh_if_due()
        return list(self._by_symbol.get(symbol, []))
