from typing import Dict, List

from ..models import Confirm, Trade


def reconcile(trades: List[Trade], confirms: List[Confirm]) -> List[dict]:
    """Return a list of breaks. A trade without a confirm, or a confirm without a trade, is a break too."""
    by_trade: Dict[str, Trade] = {t.trade_id: t for t in trades}
    breaks, seen = [], set()
    for c in confirms:
        trade = by_trade.get(c.trade_id)
        if trade is None:
            breaks.append({"type": "UNKNOWN_TRADE", "broker_ref": c.broker_ref})
            continue
        seen.add(trade.trade_id)
        if c.side != trade.side or c.quantity != trade.quantity:
            breaks.append({"type": "QTY_OR_SIDE", "trade_id": trade.trade_id})
        elif float(c.price) != float(trade.price):
            breaks.append({"type": "PRICE", "trade_id": trade.trade_id, "ours": str(trade.price), "theirs": c.price})
    for trade_id in by_trade.keys() - seen:
        breaks.append({"type": "MISSING_CONFIRM", "trade_id": trade_id})
    return breaks
