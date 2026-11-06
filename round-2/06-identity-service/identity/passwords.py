import hashlib
import hmac
import secrets

from .config import PBKDF2_ITERATIONS
from .errors import ValidationError


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ITERATIONS).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def check_password(password: str, stored: str) -> bool:
    _, iterations, salt, digest = stored.split("$")
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations)).hex()
    return hmac.compare_digest(candidate, digest)


def validate_new_password(password: str) -> None:
    if len(password) < 12:
        raise ValidationError("password must be at least 12 characters")
    if password.lower() == password or password.upper() == password:
        raise ValidationError("password needs upper and lower case letters")
