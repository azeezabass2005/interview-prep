from dataclasses import dataclass


@dataclass
class Payment:
    id: str
    merchant_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    description: str
    status: str
    psp_charge_id: str | None
    failure_code: str | None
    created_at: str
    updated_at: str


@dataclass
class Refund:
    id: str
    payment_id: str
    amount_minor: int
    status: str
    psp_refund_id: str | None
    created_at: str
