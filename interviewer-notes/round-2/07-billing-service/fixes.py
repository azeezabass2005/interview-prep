FIXES = [
    ("billing/services/invoicing.py",
     '''        for customer in self._customers.active():
            self._invoice_customer(customer, period, iso(start), iso(end))''',
     '''        for customer in self._customers.active():
            if self._invoices.find(customer["id"], period) is not None:
                continue
            self._invoice_customer(customer, period, iso(start), iso(end))'''),
    ("billing/repositories/ledger.py", '"WHERE customer_id = ? AND occurred_at BETWEEN ? AND ?",',
     '"WHERE customer_id = ? AND occurred_at >= ? AND occurred_at < ?",'),
    ("billing/services/seats.py", "        return round(added_seats * seat_price_cents * remaining / days)",
     "        numerator = added_seats * seat_price_cents * remaining\n        return (2 * numerator + days) // (2 * days)"),
    ("billing/services/invoicing.py",
     '''        tax = self._tax.tax_for(customer["country"], subtotal)
        invoice = {"id": self._ids.new("inv"), "customer_id": customer["id"], "period": period, "subtotal_cents": subtotal,
                   "tax_cents": tax, "total_cents": subtotal + tax, "status": "open", "created_at": iso(self._clock.now())}''',
     '''        status = "open"
        try:
            tax = self._tax.tax_for(customer["country"], subtotal)
        except TaxUnavailable as e:
            tax, status = 0, "pending_tax"
            self._logger.warning("tax_unavailable", customer_id=customer["id"], period=period, error=str(e))
        invoice = {"id": self._ids.new("inv"), "customer_id": customer["id"], "period": period, "subtotal_cents": subtotal,
                   "tax_cents": tax, "total_cents": subtotal + tax, "status": status, "created_at": iso(self._clock.now())}'''),
    ("billing/services/invoicing.py", "import math\n", "import math\n\nfrom ..adapters.taxly import TaxUnavailable\n"),
    ("billing/services/payments.py",
     '''        self._payments.add(self._ids.new("pmt"),''',
     '''        if self._payments.by_provider_id(str(data["payment_id"])) is not None:
            return
        self._payments.add(self._ids.new("pmt"),'''),
]
GROUPS = [[0], [1], [2], [3, 4], [5]]
