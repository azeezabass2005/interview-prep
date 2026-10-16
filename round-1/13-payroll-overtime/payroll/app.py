from .api import PayrollApi
from .services.paystub import PayrollService
from .services.timesheets import TimesheetService
from .store import InMemoryStore


def build_app():
    store = InMemoryStore()
    timesheets = TimesheetService(store)
    return PayrollApi(store, timesheets, PayrollService(store, timesheets))
