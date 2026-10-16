from datetime import datetime, timezone
from decimal import Decimal

from ..models import Client


def month_key(epoch_seconds: Decimal) -> str:
    return datetime.fromtimestamp(float(epoch_seconds), tz=timezone.utc).strftime("%Y-%m")


def record(client: Client, cost: int, now: Decimal) -> None:
    key = month_key(now)
    client.usage[key] = client.usage.get(key, 0) + cost


def usage(client: Client, month: str) -> int:
    return client.usage.get(month, 0)
