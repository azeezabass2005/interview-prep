SESSION_IDLE_MINUTES = 30          # a session expires after 30 minutes without activity...
SESSION_ABSOLUTE_HOURS = 12        # ...and never lives longer than 12 hours, active or not (security policy SP-7)
RESET_TOKEN_MINUTES = 30
MAX_FAILED_LOGINS = 5              # failed logins per account per window before it's locked for the rest of the window
FAILED_LOGIN_WINDOW_MINUTES = 15
PERMISSION_CACHE_SECONDS = 600
PBKDF2_ITERATIONS = 60_000
ROLE_PERMISSIONS = {
    "admin": {"users:read", "users:write", "roles:write"},
    "support": {"users:read"},
    "member": set(),
}
