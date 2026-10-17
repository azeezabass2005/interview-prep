from collections import defaultdict

from .store import InMemoryStore


def spending_by_member(store: InMemoryStore, group_id: str) -> dict:
    spent = defaultdict(int)
    for expense in store.group_expenses(group_id):
        if expense.deleted:
            continue
        for member, share in expense.shares.items():
            spent[member] += share
    return dict(sorted(spent.items()))
