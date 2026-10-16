from .cache import FlagCache
from .repositories.flags import FlagRepository
from .services.admin import FlagAdmin
from .services.evaluator import Evaluator


class Instance:

    def __init__(self, db, clock):
        self.repo = FlagRepository(db)
        self.cache = FlagCache(self.repo, clock)
        self.evaluator = Evaluator(self.cache)
        self.admin = FlagAdmin(self.repo, self.cache)
