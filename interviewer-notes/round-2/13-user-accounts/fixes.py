FIXES = [
    ("accounts/repositories/users.py",
     "class UserRepository:",
     "def normalize_email(email: str) -> str:\n    return (email or \"\").strip().lower()\n\n\nclass UserRepository:"),
    ("accounts/repositories/users.py",
     "    def by_email(self, email: str) -> Optional[User]:\n        with self._db.transaction() as conn:\n"
     "            r = conn.execute(\"SELECT * FROM users WHERE email = ?\", (email,)).fetchone()",
     "    def by_email(self, email: str) -> Optional[User]:\n        with self._db.transaction() as conn:\n"
     "            r = conn.execute(\"SELECT * FROM users WHERE email = ?\", (normalize_email(email),)).fetchone()"),
    ("accounts/repositories/users.py",
     "                                   (email, display_name, password_hash, salt))",
     "                                   (normalize_email(email), display_name, password_hash, salt))"),
    ("accounts/repositories/users.py",
     "\"SELECT * FROM users WHERE display_name LIKE ? ORDER BY display_name LIMIT ?\"",
     "\"SELECT * FROM users WHERE display_name LIKE ? AND deleted_at IS NULL ORDER BY display_name LIMIT ?\""),
    ("accounts/repositories/tokens.py",
     "    def get(self, token: str) -> Optional[ResetToken]:",
     "    def consume(self, token: str, at: datetime) -> bool:\n        with self._db.transaction() as conn:\n"
     "            cur = conn.execute(\"UPDATE reset_tokens SET used_at = ? WHERE token = ? AND used_at IS NULL\",\n"
     "                               (at.isoformat(), token))\n        return cur.rowcount == 1\n\n"
     "    def get(self, token: str) -> Optional[ResetToken]:"),
    ("accounts/services/reset.py",
     "            raise InvalidToken(\"token expired\")\n",
     "            raise InvalidToken(\"token expired\")\n"
     "        if not self._tokens.consume(token, self._clock.now()):\n            raise InvalidToken(\"invalid or used token\")\n"),
    ("accounts/services/auth.py",
     """        if not verify_password(password, user.password_hash, user.salt):
            if user.locked_until is not None and user.locked_until > now:
                self._audit.log(user.user_id, "login_locked")
                raise AccountLocked("account temporarily locked")
            failed""",
     """        if user.locked_until is not None and user.locked_until > now:
            self._audit.log(user.user_id, "login_locked")
            raise AccountLocked("account temporarily locked")

        if not verify_password(password, user.password_hash, user.salt):
            failed"""),
]
