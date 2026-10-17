from .api import TabApi
from .services.balances import BalanceService
from .services.expenses import ExpenseService
from .services.groups import GroupService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    groups = GroupService(store)
    return TabApi(groups, ExpenseService(store, groups), BalanceService(store, groups)), store
