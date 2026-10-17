FIXES = [
    ("accounts.py", "        return email.strip()", "        return email.strip().lower()"),
    ("accounts.py", "            raise AccountError(\"password needs a letter and a digit\")",
     "            raise AccountError(\"password needs a letter and a digit\")\n        if email.split(\"@\")[0].lower() in password.lower():\n            raise AccountError(\"password contains your e-mail name\")"),
    ("accounts.py", "            return True\n        user.failures += 1", "            user.failures = 0\n            return True\n        user.failures += 1"),
    ("accounts.py", "        user.salt = os.urandom(16)\n        user.password_hash = _hash(new_password, user.salt)",
     "        user.salt = os.urandom(16)\n        user.password_hash = _hash(new_password, user.salt)\n        user.tokens = {}\n        user.failures, user.locked_until = 0, None"),
]
