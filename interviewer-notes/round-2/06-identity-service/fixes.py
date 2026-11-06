FIXES = [
    ("identity/services/auth.py",
     '''        validate_new_password(new_password)
        self._users.set_password(row["user_id"], hash_password(new_password))''',
     '''        validate_new_password(new_password)
        if not self._resets.mark_used(_hash(token), iso(self._clock.now())):
            raise Unauthorized("this reset link is invalid or has expired")
        self._users.set_password(row["user_id"], hash_password(new_password))'''),
    ("identity/services/auth.py",
     '''        if session is None or session["revoked_at"] is not None or parse_iso(session["expires_at"]) <= now:
            raise Unauthorized("session expired")''',
     '''        if session is None or session["revoked_at"] is not None or parse_iso(session["expires_at"]) <= now:
            raise Unauthorized("session expired")
        hard_limit = parse_iso(session["created_at"]) + timedelta(hours=SESSION_ABSOLUTE_HOURS)
        if now >= hard_limit:
            raise Unauthorized("session expired")'''),
    ("identity/services/auth.py",
     '''        self._sessions.extend(_hash(token), iso(now + timedelta(minutes=SESSION_IDLE_MINUTES)))''',
     '''        self._sessions.extend(_hash(token), iso(min(now + timedelta(minutes=SESSION_IDLE_MINUTES), hard_limit)))'''),
    ("identity/services/auth.py", "        key = email.strip()\n", "        key = email.strip().lower()\n"),
    ("identity/services/auth.py", '''            raise NotFound("no account with that email")''',
     '''            raise Unauthorized("invalid email or password")'''),
    ("identity/services/auth.py", '''            raise Unauthorized("wrong password")''', '''            raise Unauthorized("invalid email or password")'''),
    ("identity/services/permissions.py",
     '''        self._users.grant(user_id, role)''',
     '''        self._users.grant(user_id, role)
        self._cache.delete(user_id)'''),
    ("identity/services/permissions.py",
     '''        self._users.revoke(user_id, role)''',
     '''        self._users.revoke(user_id, role)
        self._cache.delete(user_id)'''),
]
GROUPS = [[0], [1, 2], [3], [4, 5], [6, 7]]
