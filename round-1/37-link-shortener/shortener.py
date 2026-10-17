import re
import string
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
MIN_LENGTH = 6
ALIAS_PATTERN = re.compile(r"[a-z0-9-]{3,20}")
RESERVED = {"admin", "api", "login"}


class LinkError(Exception):
    pass


@dataclass
class Link:
    code: str
    url: str
    owner: str
    expires_at: Optional[datetime]
    clicks: int = 0
    deleted: bool = False


def encode(number):
    digits = []
    while number:
        number, rem = divmod(number, len(ALPHABET))
        digits.append(ALPHABET[rem])
    return "".join(digits).rjust(MIN_LENGTH, "0")


class Shortener:
    def __init__(self, clock):
        self.clock = clock
        self.links = {}
        self.counter = 0

    def shorten(self, owner, url, alias=None, expires_at=None):
        if not url.startswith(("http://", "https://")):
            raise LinkError("bad url")
        if alias is not None:
            if not ALIAS_PATTERN.fullmatch(alias.lower()):
                raise LinkError("bad alias")
            if alias in self.links:
                raise LinkError("alias taken")
            code = alias
        else:
            for link in self.links.values():
                if link.url == url and not link.deleted:
                    return link
            self.counter += 1
            code = encode(self.counter)
        link = Link(code, url, owner, expires_at)
        self.links[code] = link
        return link

    def resolve(self, code):
        link = self.links.get(code) or self.links.get(code.lower())
        if link is None or link.deleted:
            return 404, None
        if link.expires_at is not None and self.clock.now() > link.expires_at:
            return 410, None
        link.clicks += 1
        return 301, link.url

    def delete(self, code, user):
        link = self.links.get(code)
        if link is None or link.deleted:
            raise LinkError("no such link")
        if link.owner != user:
            raise LinkError("not your link")
        link.deleted = True

    def links_of(self, owner):
        return sorted((l for l in self.links.values() if l.owner == owner and not l.deleted), key=lambda l: l.code)

    def extend(self, code, user, new_expiry):
        link = self.links.get(code)
        if link is None or link.deleted or link.owner != user:
            raise LinkError("no such link of yours")
        if new_expiry is not None and new_expiry <= self.clock.now():
            raise LinkError("expiry must be in the future")
        link.expires_at = new_expiry
        return link

    def top(self, n=10):
        live = [l for l in self.links.values() if not l.deleted]
        return [(l.code, l.clicks) for l in sorted(live, key=lambda l: (-l.clicks, l.code))[:n]]
