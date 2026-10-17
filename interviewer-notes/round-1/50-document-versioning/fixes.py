FIXES = [
    ("docs.py", "        if doc.lock_holder not in (None, author):\n            raise DocError(f\"locked by {doc.lock_holder}\")\n",
     "        if doc.lock_holder not in (None, author) and doc.lock_until > self.clock.now():\n            raise DocError(f\"locked by {doc.lock_holder}\")\n"
     "        if base_version != doc.latest:\n            raise Conflict(f\"based on v{base_version}, latest is v{doc.latest}\")\n"),
    ("docs.py", "        doc.versions[doc.latest] = Version(doc.latest, author, old.content)\n        return doc.versions[doc.latest]",
     "        return self._add_version(doc, author, old.content)"),
    ("docs.py", "            del doc.versions[min(doc.versions)]",
     "            del doc.versions[min(n for n in doc.versions if n != doc.published)]"),
    ("docs.py", "        return doc.versions[doc.latest].content",
     "        return doc.versions[doc.published].content if doc.published is not None else None"),
]
