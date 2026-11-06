from dataclasses import dataclass


@dataclass
class User:
    id: str
    org_id: str
    email: str
    name: str
    password_hash: str
    disabled: bool
    created_at: str
