FIXES = [
    ("blotter/services/trading.py",
     '''        if principal.has_role("desk_head"):
            return True''',
     '''        if principal.has_role("desk_head"):
            return trade.desk == principal.org_id'''),
    ("blotter/services/trading.py",
     '''        self._trades.insert(trade)
        with self._db.transaction() as conn:
            self._check_limit(trade.desk, trade.symbol, trade.signed_quantity, conn)''',
     '''        with self._db.transaction() as conn:
            self._check_limit(trade.desk, trade.symbol, trade.signed_quantity, conn)
            self._trades.insert(trade, conn)'''),
    ("blotter/services/trading.py",
     '''        rows = []
        for t in self._trades.for_desk(desk, trade_date):
            cp = self._counterparties.get(t.counterparty_id)
            rows.append({"trade": t, "counterparty": cp.name if cp else None})
        return rows''',
     '''        trades = self._trades.for_desk(desk, trade_date)
        names = self._counterparties.get_many(t.counterparty_id for t in trades)
        return [{"trade": t, "counterparty": names[t.counterparty_id].name if t.counterparty_id in names else None}
                for t in trades]'''),
    ("blotter/services/eod.py", "        label = now.date().isoformat()", "        label = business_date(now).isoformat()"),
    ("blotter/services/eod.py", "from ..clock import iso\n", "from ..calendar import business_date\nfrom ..clock import iso\n"),
    ("blotter/services/trading.py",
     '''        new = trade.amended(None if quantity is None else int(quantity), None if price_cents is None else int(price_cents))''',
     '''        try:
            new = trade.amended(None if quantity is None else int(quantity),
                                None if price_cents is None else int(price_cents))
        except ValueError as e:
            raise ValidationError(str(e)) from e'''),
]
GROUPS = [[0], [1], [2], [3, 4], [5]]
