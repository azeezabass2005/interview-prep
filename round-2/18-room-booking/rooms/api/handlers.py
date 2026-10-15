from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from ..errors import RoomError
from ..services.availability import AvailabilityService
from ..services.booking import BookingService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class RoomsApi:
    def __init__(self, db):
        self._booking = BookingService(db)
        self._availability = AvailabilityService(db)

    def _run(self, fn):
        try:
            return fn()
        except RoomError as e:
            return Response(e.status, {"error": str(e)})

    def post_booking(self, organizer: str, body: dict) -> Response:
        return self._run(lambda: Response(201, {"booking_id": self._booking.book(
            body["room_id"], organizer, body.get("attendees", []), datetime.fromisoformat(body["start"]),
            datetime.fromisoformat(body["end"]))}))

    def post_series(self, organizer: str, body: dict) -> Response:
        return self._run(lambda: Response(201, {"booking_ids": self._booking.book_weekly(
            body["room_id"], organizer, body.get("attendees", []), datetime.fromisoformat(body["first_start"]),
            timedelta(minutes=body["minutes"]), date.fromisoformat(body["until"]))}))

    def get_schedule(self, room_id: str, day: str) -> Response:
        return self._run(lambda: Response(200, {"bookings": [
            {"booking_id": b.booking_id, "start": b.start.isoformat(), "organizer": b.organizer}
            for b in self._availability.day_schedule(room_id, date.fromisoformat(day))]}))
