import math

from ..clock import iso
from ..config import INCLUDED_API_CALLS, OVERAGE_CENTS_PER_1000
from ..periods import bounds


class InvoiceRun:
    """Monthly invoicing. On the 1st, the scheduler enqueues one `invoice_run` job for the previous month; the worker
    runs it and may retry it if it fails."""

    def __init__(self, customers, usage, charges, invoices, tax, queue, clock, ids, logger):
        self._customers = customers
        self._usage = usage
        self._charges = charges
        self._invoices = invoices
        self._tax = tax
        self._queue = queue
        self._clock = clock
        self._ids = ids
        self._logger = logger

    def schedule(self, period: str) -> str:
        return self._queue.enqueue("invoice_run", {"period": period}, max_attempts=3)

    def run(self, payload: dict) -> None:
        period = payload["period"]
        start, end = bounds(period)
        for customer in self._customers.active():
            self._invoice_customer(customer, period, iso(start), iso(end))
        self._logger.info("invoice_run_done", period=period)

    def _invoice_customer(self, customer, period: str, start: str, end: str) -> None:
        lines = [(f"{customer['seats']} seats × ${customer['seat_price_cents'] / 100:.2f}",
                  customer["seats"] * customer["seat_price_cents"])]
        calls = self._usage.total(customer["id"], start, end)
        over = max(0, calls - INCLUDED_API_CALLS)
        if over:
            lines.append((f"API calls over allowance: {over:,}", math.ceil(over / 1000) * OVERAGE_CENTS_PER_1000))
        charges = self._charges.uninvoiced(customer["id"], end)
        lines.extend((c["description"], c["amount_cents"]) for c in charges)
        subtotal = sum(amount for _, amount in lines)
        tax = self._tax.tax_for(customer["country"], subtotal)
        invoice = {"id": self._ids.new("inv"), "customer_id": customer["id"], "period": period, "subtotal_cents": subtotal,
                   "tax_cents": tax, "total_cents": subtotal + tax, "status": "open", "created_at": iso(self._clock.now())}
        self._invoices.create(invoice, lines, [c["id"] for c in charges])
        self._logger.info("invoice_created", invoice_id=invoice["id"], customer_id=customer["id"], total=invoice["total_cents"])
