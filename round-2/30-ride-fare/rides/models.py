from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

REQUESTED, ASSIGNED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED = (
    "REQUESTED", "ASSIGNED", "ARRIVED", "IN_PROGRESS", "COMPLETED", "CANCELLED")


@dataclass
class Trip:
    trip_id: str
    rider: str
    zone: str
    locked_surge: Decimal
    requested_at: datetime
    status: str = REQUESTED
    promo: Optional[str] = None
    driver: Optional[str] = None
    assigned_at: Optional[datetime] = None
    eta_seconds: Optional[int] = None
    arrived_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    dropped_off_at: Optional[datetime] = None
    miles: Optional[Decimal] = None
    tolls: Decimal = Decimal("0")
    fare: Optional[Decimal] = None
    driver_payout: Optional[Decimal] = None
    cancel_fee: Optional[Decimal] = None


@dataclass(frozen=True)
class FareBreakdown:
    metered: Decimal
    surged: Decimal
    wait: Decimal
    subtotal: Decimal
    discount: Decimal
    tolls: Decimal
    total: Decimal
