from decimal import ROUND_HALF_UP, Decimal

from .models import Trip
from .rates import BASE, BOOKING_FEE, CENT, MINIMUM_FARE, PER_MILE, PER_MINUTE
from .surge import SurgeFeed


def billable_minutes(duration_seconds: int) -> int:
    return duration_seconds // 60


def metered_subtotal(trip: Trip) -> Decimal:
    miles = trip.miles.quantize(CENT, rounding=ROUND_HALF_UP)
    return BASE + miles * PER_MILE + billable_minutes(trip.duration_seconds) * PER_MINUTE


class FareCalculator:
    def __init__(self, surge_feed: SurgeFeed):
        self._surge_feed = surge_feed

    def fare_for(self, trip: Trip) -> Decimal:
        surge = self._surge_feed.multiplier(trip.zone)
        fare = (metered_subtotal(trip) + BOOKING_FEE) * surge
        fare = fare + trip.tolls
        fare = max(fare, MINIMUM_FARE)
        return fare.quantize(CENT, rounding=ROUND_HALF_UP)
