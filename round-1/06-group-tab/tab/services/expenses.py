from ..errors import NotFound, ValidationError
from ..models import EQUAL, Expense
from ..splitting import compute_shares
from ..store import InMemoryStore
from .groups import GroupService


class ExpenseService:
    def __init__(self, store: InMemoryStore, groups: GroupService):
        self._store = store
        self._groups = groups

    def _build(self, expense_id: int, group_id: str, payload: dict) -> Expense:
        group = self._groups.get(group_id)
        payer = payload.get("payer", "").lower()
        split_type = payload.get("split", EQUAL)
        details = payload.get("details")
        try:
            amount = int(payload["amount_cents"])
        except (KeyError, TypeError, ValueError):
            raise ValidationError("amount_cents required")
        if split_type == EQUAL:
            details = [d.lower() for d in details]
            people = details
        else:
            details = {k.lower(): v for k, v in details.items()}
            people = list(details)
        self._groups.require_members(group, payer, *people)
        shares = compute_shares(split_type, amount, details)
        return Expense(expense_id, group_id, payer, amount, payload.get("description", ""), split_type, shares)

    def add(self, group_id: str, payload: dict) -> Expense:
        expense = self._build(self._store.new_expense_id(), group_id, payload)
        self._store.save_expense(expense)
        return expense

    def edit(self, expense_id: int, payload: dict) -> Expense:
        old = self._get(expense_id)
        expense = self._build(expense_id, old.group_id, payload)
        self._store.save_expense(expense)
        return expense

    def delete(self, expense_id: int) -> Expense:
        expense = self._get(expense_id)
        expense.deleted = True
        return expense

    def _get(self, expense_id: int) -> Expense:
        expense = self._store.expense(expense_id)
        if expense is None or expense.deleted:
            raise NotFound(f"expense {expense_id}")
        return expense
