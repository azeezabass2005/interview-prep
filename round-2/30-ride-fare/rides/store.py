from typing import Dict, List, Optional

from .models import Trip


class InMemoryStore:
    def __init__(self):
        self.trips: Dict[str, Trip] = {}

    def save(self, trip: Trip) -> None:
        self.trips[trip.trip_id] = trip

    def get(self, trip_id: str) -> Optional[Trip]:
        return self.trips.get(trip_id)

    def for_driver(self, driver: str) -> List[Trip]:
        return [t for t in self.trips.values() if t.driver == driver]
