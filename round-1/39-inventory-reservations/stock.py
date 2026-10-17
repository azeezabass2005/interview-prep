from dataclasses import dataclass
from datetime import datetime, timedelta

RESERVATION_TTL = timedelta(minutes=15)
LOW_STOCK = 5


class StockError(Exception):
    pass


@dataclass
class Reservation:
    cart: str
    sku: str
    quantity: int
    expires_at: datetime


class StockService:
    def __init__(self):
        self.on_hand = {}
        self.reservations = {}
        self.alerts = []
        self.alerted = set()

    def restock(self, sku, quantity):
        self.on_hand[sku] = self.on_hand.get(sku, 0) + quantity
        if self.on_hand[sku] > LOW_STOCK:
            self.alerted.discard(sku)

    def available(self, sku, now, ignore_cart=None):
        held = sum(r.quantity for (cart, s), r in self.reservations.items() if s == sku and cart != ignore_cart)
        return self.on_hand.get(sku, 0) - held

    def _check_low(self, sku, now):
        if self.available(sku, now) <= LOW_STOCK:
            self.alerts.append(sku)

    def reserve(self, cart, sku, quantity, now):
        if quantity <= 0 or sku not in self.on_hand:
            raise StockError("bad reservation")
        key = (cart, sku)
        current = self.reservations.get(key)
        wanted = quantity + (current.quantity if current else 0)
        if self.available(sku, now, ignore_cart=cart) < wanted:
            raise StockError("not enough stock")
        self.reservations[key] = Reservation(cart, sku, wanted, now + RESERVATION_TTL)
        self._check_low(sku, now)

    def release(self, cart, sku):
        self.reservations.pop((cart, sku), None)

    def checkout(self, cart, now):
        items = sorted((r for (c, _), r in self.reservations.items() if c == cart), key=lambda r: r.sku)
        if not items:
            raise StockError("nothing reserved")
        for r in items:
            if r.expires_at <= now:
                raise StockError(f"reservation for {r.sku} expired")
            self.on_hand[r.sku] -= r.quantity
            self._check_low(r.sku, now)
        return {r.sku: r.quantity for r in items}

    def cart(self, cart, now):
        items = {}
        for (c, sku), r in self.reservations.items():
            if c == cart:
                items[sku] = {"quantity": r.quantity, "expires_in": max(0, int((r.expires_at - now).total_seconds())),
                              "expired": r.expires_at <= now}
        return items

    def sweep(self, now):
        expired = [key for key, r in self.reservations.items() if r.expires_at <= now]
        for key in expired:
            del self.reservations[key]
        return len(expired)

    def adjust(self, sku, counted, now):
        if counted < 0:
            raise StockError("count can't be negative")
        difference = counted - self.on_hand.get(sku, 0)
        self.on_hand[sku] = counted
        if counted > LOW_STOCK:
            self.alerted.discard(sku)
        else:
            self._check_low(sku, now)
        return difference
