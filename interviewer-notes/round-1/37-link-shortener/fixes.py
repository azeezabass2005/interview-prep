FIXES = [
    ("shortener.py", "    return \"\".join(digits).rjust(MIN_LENGTH, \"0\")", "    return \"\".join(reversed(digits)).rjust(MIN_LENGTH, \"0\")"),
    ("shortener.py", "            if not ALIAS_PATTERN.fullmatch(alias.lower()):\n                raise LinkError(\"bad alias\")",
     "            alias = alias.lower()\n            if not ALIAS_PATTERN.fullmatch(alias) or alias in RESERVED:\n                raise LinkError(\"bad alias\")"),
    ("shortener.py", "                if link.url == url and not link.deleted:", "                if link.url == url and link.owner == owner and not link.deleted:"),
    ("shortener.py", "self.clock.now() > link.expires_at:", "self.clock.now() >= link.expires_at:"),
]
