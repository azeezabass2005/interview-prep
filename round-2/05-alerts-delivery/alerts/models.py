from dataclasses import dataclass


@dataclass
class User:
    id: str
    org_id: str
    name: str
    email: str
    phone: str | None


@dataclass
class Rule:
    id: str
    user_id: str
    symbol: str
    direction: str
    threshold: float
    channel: str
    active: bool
    created_at: str
    triggered_at: str | None

    def fires_at(self, price: float) -> bool:
        return price >= self.threshold if self.direction == "above" else price <= self.threshold


@dataclass
class Delivery:
    id: str
    rule_id: str
    user_id: str
    channel: str
    recipient: str
    message: str
    status: str
    provider_id: str | None
    error: str | None
    created_at: str
    sent_at: str | None
