import os
import tempfile

from rooms.api.handlers import RoomsApi
from rooms.db import Database
from rooms.models import Room
from rooms.repositories.bookings import BookingRepository
from rooms.repositories.rooms import RoomRepository
from rooms.services.booking import BookingService


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "rooms.db"))
        self.db.initialize()
        rooms = RoomRepository(self.db)
        rooms.add(Room("thames4", "Thames 4", 10, "Europe/London"))
        rooms.add(Room("shibuya2", "Shibuya 2", 6, "Asia/Tokyo"))
        self.api = RoomsApi(self.db)
        self.bookings = BookingRepository(self.db)

    def service(self):
        return BookingService(self.db)

    def book(self, start, end, room="thames4", organizer="ann", attendees=("bob",)):
        return self.api.post_booking(organizer, {"room_id": room, "start": start, "end": end, "attendees": list(attendees)})

    def cleanup(self):
        self._dir.cleanup()
