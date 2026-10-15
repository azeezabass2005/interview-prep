# Meeting Room Booking

Books meeting rooms in Bloomberg-style offices worldwide (New York, London, Tokyo). Bookings are stored in **UTC**; each room has its
building's time zone. Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
rooms/api/handlers.py             RoomsApi
rooms/services/booking.py         BookingService: single bookings and weekly series
rooms/services/availability.py    a room's schedule for a local day
rooms/repositories/*.py           rooms, bookings (SQLite)
rooms/db.py, errors.py, models.py, config.py
```

## Rules

- A room can never have two bookings that overlap. Intervals are half-open `[start, end)`: back-to-back is fine.
- **Capacity:** the number of people in the room, **including the organizer**, must not exceed the room's capacity.
- **Weekly series:** a meeting repeated every 7 days from the first occurrence **up to and including** the `until` date.
- **Schedules** are shown per **local day in the room's time zone** (00:00–24:00 local).
