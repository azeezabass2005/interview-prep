FIXES = [
    ("chat.py", "        self._seq += 1\n        message = Message(channel, self._seq, author, text, at, client_id)",
     "        message = Message(channel, len(c.messages) + 1, author, text, at, client_id)"),
    ("chat.py", "        return sum(1 for m in c.messages if m.seq > last)", "        return sum(1 for m in c.messages if m.seq > last and m.author != member)"),
    ("chat.py", "        m = self._message(channel, seq)\n        if at - m.posted_at > EDIT_WINDOW:",
     "        m = self._message(channel, seq)\n        if m.author != author:\n            raise ChatError(\"not your message\")\n        if at - m.posted_at > EDIT_WINDOW:"),
    ("chat.py", "before is None or m.seq <= before]", "before is None or m.seq < before]"),
    ("chat.py", "            if name != author:", "            if name != author and name in c.members:"),
]
