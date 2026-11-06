FIXES = [
    ("alerts/jobs.py",
     '''"UPDATE jobs SET status = 'running', attempts = attempts + 1, updated_at = ? WHERE id = ?",''',
     '''"UPDATE jobs SET status = 'running', attempts = attempts + 1, updated_at = ? WHERE id = ? AND status = 'queued'",'''),
    ("alerts/jobs.py", "    return max(cap, base * 2 ** (attempt - 1))", "    return min(cap, base * 2 ** (attempt - 1))"),
    ("alerts/adapters/channels.py", "    if 400 <= result.status < 500:", "    if 400 <= result.status < 500 and result.status != 429:"),
    ("alerts/adapters/channels.py", "    if result.status >= 500:", "    if result.status >= 500 or result.status == 429:"),
    ("alerts/services/rules.py",
     '''        return self._rules.for_user(user_id or principal.user_id)''',
     '''        if user_id and user_id != principal.user_id:
            principal.require_role("support")
            target = self._users.get(user_id)
            if target is None or target.org_id != principal.org_id:
                raise Forbidden("not allowed to view this user's alerts")
        return self._rules.for_user(user_id or principal.user_id)'''),
    ("alerts/services/rules.py", "from ..errors import NotFound, ValidationError", "from ..errors import Forbidden, NotFound, ValidationError"),
    ("alerts/privacy.py",
     '''PHONE = re.compile(r"\\+?\\d{8,15}")''',
     '''PHONE = re.compile(r"\\+?\\d[\\d\\s().-]{6,}\\d")'''),
    ("alerts/privacy.py",
     '''    return PHONE.sub(lambda m: "*" * (len(m.group(0)) - 2) + m.group(0)[-2:], value)''',
     '''    def phone(m):
        digits = re.sub(r"\\D", "", m.group(0))
        return "*" * (len(digits) - 2) + digits[-2:]
    return PHONE.sub(phone, value)'''),
]
GROUPS = [[0], [1], [2, 3], [4, 5], [6, 7]]
