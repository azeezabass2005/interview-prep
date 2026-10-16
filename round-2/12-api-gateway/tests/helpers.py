import os
import tempfile

from gateway.app import build_gateway
from gateway.clock import FakeClock
from gateway.db import Database
from gateway.proxy import Request
from gateway.repositories.keys import ApiKeyRepository
from gateway.repositories.tenants import TenantRepository

T0 = 1772452800.0


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "gw.db"))
        self.db.initialize()
        self.clock = FakeClock(T0)
        self.tenants = TenantRepository(self.db)
        keys = ApiKeyRepository(self.db)
        self.tenants.upsert("acme", "free")
        self.tenants.upsert("globex", "free")
        self.tenants.upsert("initech", "free")
        keys.add("k-acme-admin", "acme", "admin")
        keys.add("k-globex-admin", "globex", "admin")
        keys.add("k-initech", "initech", "svc")

    def gateway(self):
        return build_gateway(self.db, self.clock)

    def cleanup(self):
        self._dir.cleanup()


def call(gw, key, path="/v1/prices"):
    return gw.handle(Request(path, key))
