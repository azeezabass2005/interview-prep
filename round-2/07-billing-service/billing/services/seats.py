from ..clock import iso
from ..errors import NotFound, ValidationError
from ..periods import days_in_month


class SeatService:
    """Seat changes. Adding seats mid-month charges for the rest of the month (prorated); removing seats takes effect next
    month with no refund."""

    def __init__(self, customers, charges, clock, ids):
        self._customers = customers
        self._charges = charges
        self._clock = clock
        self._ids = ids

    def prorated_cents(self, added_seats: int, seat_price_cents: int, today) -> int:
        days = days_in_month(today)
        remaining = days - today.day + 1
        return round(added_seats * seat_price_cents * remaining / days)

    def change(self, customer_id: str, seats: int) -> dict:
        customer = self._customers.get(customer_id)
        if customer is None:
            raise NotFound("customer not found")
        if not 1 <= seats <= 10_000:
            raise ValidationError("seats must be between 1 and 10,000")
        added = seats - customer["seats"]
        charge = 0
        now = self._clock.now()
        if added > 0:
            charge = self.prorated_cents(added, customer["seat_price_cents"], now.date())
            self._charges.add(self._ids.new("chg"), customer_id, f"{added} seat(s) added on {now.date().isoformat()}", charge,
                              iso(now))
        self._customers.set_seats(customer_id, seats)
        return {"seats": seats, "prorated_charge_cents": charge}
