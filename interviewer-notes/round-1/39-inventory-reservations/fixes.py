FIXES = [
    ("stock.py", "if s == sku and cart != ignore_cart)", "if s == sku and cart != ignore_cart and r.expires_at > now)"),
    ("stock.py", "        wanted = quantity + (current.quantity if current else 0)", "        wanted = quantity"),
    ("stock.py", "        if self.available(sku, now) <= LOW_STOCK:\n            self.alerts.append(sku)",
     "        if self.available(sku, now) <= LOW_STOCK and sku not in self.alerted:\n            self.alerts.append(sku)\n            self.alerted.add(sku)"),
    ("stock.py", "        for r in items:\n            if r.expires_at <= now:\n                raise StockError(f\"reservation for {r.sku} expired\")\n",
     "        for r in items:\n            if r.expires_at <= now:\n                raise StockError(f\"reservation for {r.sku} expired\")\n        for r in items:\n            del self.reservations[(cart, r.sku)]\n"),
]
