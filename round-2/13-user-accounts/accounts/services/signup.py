import re

from ..audit import Audit
from ..config import MIN_PASSWORD_LENGTH
from ..db import Database
from ..errors import AccountsError, EmailTaken
from ..repositories.users import UserRepository
from .passwords import hash_password

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SignupService:
    def __init__(self, db: Database, clock):
        self._users = UserRepository(db)
        self._audit = Audit(db, clock)

    def register(self, email: str, display_name: str, password: str) -> int:
        if not _EMAIL.match((email or "").strip()):
            raise AccountsError("invalid e-mail address")
        if len(password or "") < MIN_PASSWORD_LENGTH:
            raise AccountsError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
        if self._users.by_email(email) is not None:
            raise EmailTaken(email)
        password_hash, salt = hash_password(password)
        user_id = self._users.create(email, display_name.strip(), password_hash, salt)
        self._audit.log(user_id, "signup")
        return user_id
