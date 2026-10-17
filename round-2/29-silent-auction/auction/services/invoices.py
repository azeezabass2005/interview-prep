from decimal import ROUND_HALF_UP, Decimal
from typing import Dict

from ..config import PREMIUM_RATE
from ..models import Invoice, InvoiceLine
from ..store import InMemoryStore
from .pricing import leading_bids


def build_invoices(store: InMemoryStore) -> Dict[int, Invoice]:
    invoices: Dict[int, Invoice] = {}
    for lot in sorted(store.lots.values(), key=lambda l: l.lot_id):
        if not lot.closed or lot.winner is None:
            continue
        winning_bid = leading_bids(store.bids_for(lot.lot_id))[0]
        premium = (winning_bid.maximum * PREMIUM_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        deductible = lot.hammer - lot.fmv
        invoice = invoices.setdefault(lot.winner, Invoice(lot.winner))
        invoice.lines.append(InvoiceLine(lot.lot_id, lot.hammer, premium, deductible))
    return invoices
