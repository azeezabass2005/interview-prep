from datetime import date
from decimal import Decimal, InvalidOperation

from ..calendar import BusinessCalendar
from ..errors import BondError, NotFound
from ..models import ACT_360, THIRTY_360, Bond, Trade
from ..store import InMemoryStore
from .pricing import accrued_interest, settlement_amount

SETTLEMENT_LAG = 1


class BookingService:
    def __init__(self, store: InMemoryStore, calendar: BusinessCalendar):
        self._store = store
        self._calendar = calendar

    def load_bond(self, bond_id: str, coupon, frequency: int, maturity: date, day_count: str) -> Bond:
        if frequency not in (1, 2, 4) or day_count not in (THIRTY_360, ACT_360):
            raise BondError("unsupported frequency or day count")
        bond = Bond(bond_id, Decimal(str(coupon)), frequency, maturity, day_count)
        self._store.bonds[bond_id] = bond
        return bond

    def book(self, trade_id: str, bond_id: str, side: str, face, clean_price, trade_date: date) -> Trade:
        bond = self._store.bond(bond_id)
        if bond is None:
            raise NotFound(bond_id)
        if side not in ("BUY", "SELL"):
            raise BondError("side must be BUY or SELL")
        try:
            face, clean_price = Decimal(str(face)), Decimal(str(clean_price))
        except InvalidOperation:
            raise BondError("face and price must be numbers")
        if face <= 0 or clean_price <= 0:
            raise BondError("face and price must be positive")
        settle = self._calendar.add_business_days(trade_date, SETTLEMENT_LAG)
        if settle >= bond.maturity:
            raise BondError("trade settles on or after maturity")
        trade = Trade(trade_id, bond_id, side, face, clean_price, trade_date, settle,
                      accrued_interest(bond, face, settle), settlement_amount(bond, face, clean_price, settle))
        self._store.trades.append(trade)
        return trade
