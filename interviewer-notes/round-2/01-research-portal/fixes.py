FIXES = [
    ("portal/repositories/entitlements.py",
     '"WHERE org_id = ? AND starts_on <= ? AND ends_on > ? OR ends_on IS NULL"',
     '"WHERE org_id = ? AND starts_on <= ? AND (ends_on > ? OR ends_on IS NULL)"'),
    ("portal/services/reports.py",
     'key = f"reports:{sector or \'all\'}:{page}:{page_size}"',
     'key = f"reports:{principal.org_id}:{sector or \'all\'}:{page}:{page_size}"'),
    ("portal/services/reports.py",
     "result = Page(rows, page, page_size, has_more=len(rows) > page_size)",
     "result = Page(rows[:page_size], page, page_size, has_more=len(rows) > page_size)"),
    ("portal/middleware.py",
     "query=dict(request.query),",
     "query={k: ('[REDACTED]' if k.lower() in ('access_token', 'token', 'api_key') else v) for k, v in request.query.items()},"),
    ("portal/services/digest.py",
     '''        self._users.set_last_digest(user.id, iso(self._clock.now()))
        lines = "".join(f"<li><b>{r.title}</b> ({r.sector}): {r.summary}</li>" for r in new)
        try:
            self._email.send(user.email, f"Your research digest: {len(new)} new reports", f"<ul>{lines}</ul>")
        except Exception as e:
            self._logger.error("digest_failed", user_id=user.id, error=str(e))
''',
     '''        lines = "".join(f"<li><b>{r.title}</b> ({r.sector}): {r.summary}</li>" for r in new)
        self._email.send(user.email, f"Your research digest: {len(new)} new reports", f"<ul>{lines}</ul>")
        self._users.set_last_digest(user.id, max(r.published_at for r in new))
'''),
]
