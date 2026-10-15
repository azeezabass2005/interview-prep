FIXES = [
    # OMS-204: Decimal tick check
    ("oms/services/validation.py",
     """    tick = tick_for(price)
    steps = price * round(1 / tick)
    if int(steps) != steps:
        raise ValidationError(f"price {payload['limit_price']} is not on a valid tick")
    try:
        limit = Decimal(str(payload["limit_price"]))
    except InvalidOperation:
        raise ValidationError("limit_price must be a number")""",
     """    try:
        limit = Decimal(str(payload["limit_price"]))
    except InvalidOperation:
        raise ValidationError("limit_price must be a number")
    tick = Decimal(str(tick_for(price)))
    if limit % tick != 0:
        raise ValidationError(f"price {payload['limit_price']} is not on a valid tick")"""),
    # OMS-203: only cancel open orders, atomically
    ("oms/repositories/orders.py",
     "    def for_account(self, account: str) -> List[Order]:",
     """    def cancel_if_open(self, order_id: str, at: datetime) -> bool:
        with self._db.transaction() as conn:
            cur = conn.execute(
                "UPDATE orders SET status = 'CANCELLED', updated_at = ? "
                "WHERE order_id = ? AND status IN ('NEW', 'PARTIALLY_FILLED')",
                (at.isoformat(), order_id))
        return cur.rowcount == 1

    def recompute_fill_state(self, order_id: str, at: datetime) -> None:
        \"\"\"Derive filled_qty/avg_price/status from the executions table under the DB write lock.\"\"\"
        with self._db.transaction() as conn:
            conn.execute("BEGIN IMMEDIATE")
            quantity = conn.execute("SELECT quantity FROM orders WHERE order_id = ?", (order_id,)).fetchone()[0]
            rows = conn.execute("SELECT quantity, price FROM executions WHERE order_id = ?", (order_id,)).fetchall()
            filled = sum(r[0] for r in rows)
            if filled == 0:
                return
            avg = sum(r[0] * Decimal(r[1]) for r in rows) / filled
            avg = avg.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            status = "FILLED" if filled >= quantity else "PARTIALLY_FILLED"
            conn.execute(
                "UPDATE orders SET filled_qty = ?, avg_price = ?, "
                "status = CASE WHEN status = 'CANCELLED' THEN status ELSE ? END, updated_at = ? WHERE order_id = ?",
                (filled, str(avg), status, at.isoformat(), order_id))

    def for_account(self, account: str) -> List[Order]:"""),
    ("oms/repositories/orders.py", "from decimal import Decimal", "from decimal import ROUND_HALF_UP, Decimal"),
    ("oms/services/orders.py", "from ..errors import NotFound", "from ..errors import InvalidState, NotFound"),
    ("oms/services/orders.py",
     "        self._orders.set_status(order_id, CANCELLED, self._clock.now())\n",
     "        if not self._orders.cancel_if_open(order_id, self._clock.now()):\n"
     "            raise InvalidState(f\"order {order_id} is {order.status} and cannot be cancelled\")\n"),
    # OMS-201 + OMS-202: derive state from executions atomically
    ("oms/services/executions.py",
     """        filled = order.filled_qty + execution.quantity
        if order.avg_price is None:
            avg = execution.price
        else:
            avg = (order.avg_price + execution.price) / 2
        avg = avg.quantize(PRICE_PLACES, rounding=ROUND_HALF_UP)
        status = FILLED if filled >= order.quantity else PARTIALLY_FILLED

        self._orders.save_fill_state(order.order_id, filled, avg, status, self._clock.now())
""",
     """        self._orders.recompute_fill_state(order.order_id, self._clock.now())
"""),
]
