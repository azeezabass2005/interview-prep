FIXES = [
    ("quotes.py", "        if entry and now - entry.fetched_at <= TTL:\n            self.hits += 1\n",
     "        if entry and now - entry.fetched_at < TTL:\n            self.hits += 1\n            self.entries.move_to_end(key)\n"),
    ("quotes.py", "        return symbol.strip()", "        return symbol.strip().upper()"),
    ("quotes.py", "            if entry:\n", "            if entry and now - entry.fetched_at < STALE_LIMIT:\n"),
    ("quotes.py", "        self.entries[key] = Entry(quote, quote.timestamp)", "        self.entries[key] = Entry(quote, now)"),
]
