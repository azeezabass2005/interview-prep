FIXES = [
    ("flags/services/bucketing.py", "import random", "import hashlib"),
    ("flags/services/bucketing.py", "    return random.randrange(100)",
     "    digest = hashlib.sha256(f\"{flag_key}:{user_id}\".encode()).digest()\n"
     "    return int.from_bytes(digest[:8], \"big\") % 100"),
    ("flags/services/evaluator.py",
     """        if flag is None:
            return default
        if not flag.enabled:
            return False
        for rule in flag.rules:
            if user.attributes.get(rule.attribute) == rule.equals:
                return rule.value
        if user.user_id in flag.overrides:
            return flag.overrides[user.user_id]""",
     """        if flag is None or flag.archived:
            return default
        if not flag.enabled:
            return False
        if user.user_id in flag.overrides:
            return flag.overrides[user.user_id]
        for rule in flag.rules:
            if user.attributes.get(rule.attribute) == rule.equals:
                return rule.value"""),
    ("flags/services/admin.py", "        self._repo.upsert(key, enabled, rollout_percent)",
     "        self._repo.upsert(key, enabled, rollout_percent)\n        self._cache.invalidate()"),
    ("flags/services/admin.py", "        self._repo.set_override(key, user_id, value)",
     "        self._repo.set_override(key, user_id, value)\n        self._cache.invalidate()"),
    ("flags/services/admin.py", "        self._repo.add_rule(key, position, attribute, equals, value)",
     "        self._repo.add_rule(key, position, attribute, equals, value)\n        self._cache.invalidate()"),
    ("flags/services/admin.py", "        self._repo.archive(key)", "        self._repo.archive(key)\n        self._cache.invalidate()"),
]
