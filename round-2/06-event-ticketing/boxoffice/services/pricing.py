from typing import Tuple

from ..config import SERVICE_FEE_CENTS


def order_amounts(face_value_cents: int, seat_count: int) -> Tuple[int, int, int]:
    """(face total, fee total, grand total) in cents."""
    face = face_value_cents * seat_count
    fees = SERVICE_FEE_CENTS
    return face, fees, face + fees
