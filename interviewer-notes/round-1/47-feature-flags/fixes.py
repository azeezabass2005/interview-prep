FIXES = [
    ("flags.py", "        if user_id in flag.allow:\n            return True\n        if user_id in flag.deny:\n            return False",
     "        if any(not self.is_on(p, user_id, country) for p in flag.prerequisites):\n            return False\n"
     "        if user_id in flag.deny:\n            return False\n        if user_id in flag.allow:\n            return True"),
    ("flags.py", "    digest = hashlib.sha256(f\"{user_id}\".encode()).hexdigest()", "    digest = hashlib.sha256(f\"{flag_key}:{user_id}\".encode()).hexdigest()"),
    ("flags.py", "        return bucket(key, user_id) <= flag.percentage", "        return bucket(key, user_id) < flag.percentage"),
    ("flags.py", "        if country is not None and country in flag.countries:",
     "        if country is not None and country.upper() in {c.upper() for c in flag.countries}:"),
]
