import hashlib
from dataclasses import dataclass, field
from typing import List, Set


class FlagError(Exception):
    pass


@dataclass
class Flag:
    key: str
    enabled: bool = True
    allow: Set[str] = field(default_factory=set)
    deny: Set[str] = field(default_factory=set)
    countries: Set[str] = field(default_factory=set)
    percentage: int = 0
    prerequisites: List[str] = field(default_factory=list)


def bucket(flag_key, user_id):
    digest = hashlib.sha256(f"{user_id}".encode()).hexdigest()
    return int(digest[:8], 16) % 100


class FlagService:
    def __init__(self):
        self.flags = {}
        self.exposures = {}

    def define(self, key, **settings):
        flag = Flag(key, **settings)
        if not 0 <= flag.percentage <= 100:
            raise FlagError("percentage must be 0-100")
        self.flags[key] = flag
        return flag

    def is_on(self, key, user_id, country=None):
        flag = self.flags.get(key)
        if flag is None or not flag.enabled:
            return False
        if user_id in flag.allow:
            return True
        if user_id in flag.deny:
            return False
        if country is not None and country in flag.countries:
            return True
        return bucket(key, user_id) <= flag.percentage

    def evaluate(self, key, user_id, country=None):
        result = self.is_on(key, user_id, country)
        counts = self.exposures.setdefault(key, {"on": 0, "off": 0})
        counts["on" if result else "off"] += 1
        return result

    def evaluate_all(self, user_id, country=None):
        return {key: self.evaluate(key, user_id, country) for key in sorted(self.flags)}

    def set_rollout(self, key, percentage):
        flag = self.flags.get(key)
        if flag is None:
            raise FlagError("unknown flag")
        if not 0 <= percentage <= 100:
            raise FlagError("percentage must be 0-100")
        flag.percentage = percentage

    def kill(self, key):
        if key not in self.flags:
            raise FlagError("unknown flag")
        self.flags[key].enabled = False

    def dependents(self, key):
        return sorted(k for k, f in self.flags.items() if key in f.prerequisites)

    def remove(self, key):
        if self.dependents(key):
            raise FlagError(f"{key} is a prerequisite of {', '.join(self.dependents(key))}")
        self.flags.pop(key, None)
        self.exposures.pop(key, None)
