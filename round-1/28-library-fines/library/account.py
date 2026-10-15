from decimal import Decimal

BLOCK_THRESHOLD = Decimal("10.00")


class PatronAccount:
    def __init__(self, patron_id: str):
        self.patron_id = patron_id
        self.fines = Decimal("0.00")

    def charge(self, amount: Decimal) -> None:
        self.fines += amount

    def pay(self, amount: Decimal) -> None:
        if amount <= 0 or amount > self.fines:
            raise ValueError("invalid payment")
        self.fines -= amount

    def can_borrow(self) -> bool:
        return self.fines <= BLOCK_THRESHOLD
