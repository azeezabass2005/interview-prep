from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class User:
    user_id: str
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Rule:
    position: int
    attribute: str
    equals: str
    value: bool


@dataclass(frozen=True)
class Flag:
    key: str
    enabled: bool
    rollout_percent: int
    archived: bool
    overrides: Dict[str, bool]
    rules: Tuple[Rule, ...]
