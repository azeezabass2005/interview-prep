"""Demo team: python -m expenses.seed"""
import os

from .adapters.transport import UrllibTransport
from .clock import SystemClock
from .db import Database
from .ids import IdGenerator
from .models import Employee
from .wiring import build

if __name__ == "__main__":
    c = build(Database(os.environ.get("DB_PATH", "expenses.db")), SystemClock(), IdGenerator(), UrllibTransport(), UrllibTransport())
    for e in (Employee("emp_maria", "org_acme", "Maria (manager)", "emp_dir"), Employee("emp_eli", "org_acme", "Eli", "emp_maria")):
        if c.employees.get(e.id) is None:
            c.employees.add(e)
    print("Eli (employee):  ", c.auth.issue("emp_eli", "org_acme", {"employee"}, ttl_hours=24 * 30))
    print("Maria (manager): ", c.auth.issue("emp_maria", "org_acme", {"employee", "manager"}, ttl_hours=24 * 30))
