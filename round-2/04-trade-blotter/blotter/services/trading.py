from ..auth import Principal
from ..calendar import business_date
from ..clock import iso
from ..config import MAX_QUANTITY, POSITION_LIMIT
from ..errors import Conflict, Forbidden, NotFound, ValidationError
from ..models import Trade


class LimitBreached(Conflict):
    code = "position_limit"


class TradingService:
    def __init__(self, db, trades, positions, counterparties, audit, clock, ids, logger):
        self._db = db
        self._trades = trades
        self._positions = positions
        self._counterparties = counterparties
        self._audit = audit
        self._clock = clock
        self._ids = ids
        self._logger = logger

    def _check_limit(self, desk: str, symbol: str, delta: int, conn=None) -> None:
        after = self._positions.current(desk, symbol, conn) + delta
        if abs(after) > POSITION_LIMIT:
            raise LimitBreached(f"{desk} {symbol} position would be {after}, limit is {POSITION_LIMIT}")

    def book(self, principal: Principal, data: dict) -> Trade:
        principal.require_role("trader", "desk_head")
        side = data.get("side")
        if side not in ("buy", "sell"):
            raise ValidationError("side must be buy or sell")
        try:
            quantity, price_cents = int(data["quantity"]), int(data["price_cents"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("quantity and price_cents must be integers") from e
        if not 0 < quantity <= MAX_QUANTITY or price_cents <= 0:
            raise ValidationError(f"quantity must be 1-{MAX_QUANTITY} and price_cents positive")
        if self._counterparties.get(str(data.get("counterparty_id", ""))) is None:
            raise ValidationError("unknown counterparty")
        now = self._clock.now()
        trade = Trade(self._ids.new("trd"), principal.org_id, principal.user_id, data["counterparty_id"],
                      str(data.get("symbol", "")).upper(), side, quantity, price_cents, "live",
                      business_date(now).isoformat(), iso(now))
        if not trade.symbol:
            raise ValidationError("symbol is required")
        self._trades.insert(trade)
        with self._db.transaction() as conn:
            self._check_limit(trade.desk, trade.symbol, trade.signed_quantity, conn)
            self._positions.apply(trade.desk, trade.symbol, trade.signed_quantity, conn)
            self._audit.record(trade.id, principal.user_id, "book", f"{side} {quantity} {trade.symbol} @ {price_cents}",
                               iso(now), conn)
        self._logger.info("trade_booked", trade_id=trade.id, desk=trade.desk, symbol=trade.symbol)
        return trade

    def _can_change(self, principal: Principal, trade: Trade) -> bool:
        if principal.has_role("desk_head"):
            return True
        return principal.has_role("trader") and trade.trader_id == principal.user_id

    def get(self, principal: Principal, trade_id: str) -> Trade:
        trade = self._trades.get(trade_id)
        if trade is None or (trade.desk != principal.org_id and not principal.has_role("compliance") and
                             not principal.has_role("desk_head")):
            raise NotFound("trade not found")
        return trade

    def amend(self, principal: Principal, trade_id: str, quantity, price_cents) -> Trade:
        trade = self.get(principal, trade_id)
        if not self._can_change(principal, trade):
            raise Forbidden("you can't amend this trade")
        new = trade.amended(None if quantity is None else int(quantity), None if price_cents is None else int(price_cents))
        delta = new.signed_quantity - trade.signed_quantity
        with self._db.transaction() as conn:
            self._check_limit(trade.desk, trade.symbol, delta, conn)
            if not self._trades.save(new, trade.version, conn):
                raise Conflict("trade was changed by someone else; reload and retry")
            self._positions.apply(trade.desk, trade.symbol, delta, conn)
            self._audit.record(trade.id, principal.user_id, "amend",
                               f"qty {trade.quantity}->{new.quantity}, price {trade.price_cents}->{new.price_cents}",
                               iso(self._clock.now()), conn)
        return new

    def cancel(self, principal: Principal, trade_id: str) -> Trade:
        trade = self.get(principal, trade_id)
        principal.require_role("desk_head", "compliance")
        if not principal.has_role("compliance") and trade.desk != principal.org_id:
            raise Forbidden("desk heads can only cancel their own desk's trades")
        if trade.status == "cancelled":
            return trade
        cancelled = Trade(**{**trade.__dict__, "status": "cancelled", "version": trade.version + 1})
        with self._db.transaction() as conn:
            if not self._trades.save(cancelled, trade.version, conn):
                raise Conflict("trade was changed by someone else; reload and retry")
            self._positions.apply(trade.desk, trade.symbol, -trade.signed_quantity, conn)
            self._audit.record(trade.id, principal.user_id, "cancel", "", iso(self._clock.now()), conn)
        return cancelled

    def blotter(self, principal: Principal, desk: str | None, trade_date: str | None) -> list[dict]:
        desk = desk or principal.org_id
        if desk != principal.org_id and not principal.has_role("compliance"):
            raise Forbidden("you can only see your own desk")
        trade_date = trade_date or business_date(self._clock.now()).isoformat()
        rows = []
        for t in self._trades.for_desk(desk, trade_date):
            cp = self._counterparties.get(t.counterparty_id)
            rows.append({"trade": t, "counterparty": cp.name if cp else None})
        return rows

    def positions(self, principal: Principal) -> dict[str, int]:
        return self._positions.for_desk(principal.org_id)

    def audit(self, principal: Principal, trade_id: str) -> list:
        self.get(principal, trade_id)
        return [dict(r) for r in self._audit.for_trade(trade_id)]
