from tab.models import Bill, Item


def example_bill(**overrides):
    items = [
        Item("pizza", 3000, ("alice", "bob", "carol")),
        Item("wine", 2000, ("alice", "bob")),
        Item("salad", 1200, ("carol",)),
    ]
    return Bill(items=items, payer="alice", **overrides)
