from .errors import TabError
from .services.balances import BalanceService
from .services.expenses import ExpenseService
from .services.groups import GroupService
from .services.settle import suggest_transfers


class TabApi:
    def __init__(self, groups: GroupService, expenses: ExpenseService, balances: BalanceService):
        self._groups = groups
        self._expenses = expenses
        self._balances = balances

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except TabError as exc:
            return exc.status, {"error": str(exc)}

    def create_group(self, body: dict):
        return self._call(lambda: {"members": self._groups.create(body["group_id"], body.get("name", ""), body["members"]).members}, 201)

    def add_expense(self, group_id: str, body: dict):
        def go():
            e = self._expenses.add(group_id, body)
            return {"expense_id": e.expense_id, "shares": e.shares}
        return self._call(go, 201)

    def edit_expense(self, expense_id: int, body: dict):
        return self._call(lambda: {"shares": self._expenses.edit(expense_id, body).shares})

    def delete_expense(self, expense_id: int):
        return self._call(lambda: {"deleted": self._expenses.delete(expense_id).deleted})

    def pay(self, group_id: str, body: dict):
        return self._call(lambda: {"payment_id": self._balances.record_payment(
            group_id, body["from"], body["to"], int(body["amount_cents"])).payment_id}, 201)

    def balances(self, group_id: str):
        return self._call(lambda: self._balances.balances(group_id))

    def settle_up(self, group_id: str):
        return self._call(lambda: {"transfers": [
            {"from": t.sender, "to": t.receiver, "amount_cents": t.amount_cents}
            for t in suggest_transfers(self._balances.balances(group_id))]})
