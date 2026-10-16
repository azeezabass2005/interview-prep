class FakePayments:
    def __init__(self, failing=()):
        self.failing = set(failing)
        self.charges = []

    def charge(self, backer: str, amount) -> bool:
        self.charges.append((backer, amount))
        return backer not in self.failing
