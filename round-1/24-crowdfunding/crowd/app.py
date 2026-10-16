from .api import CrowdApi
from .payments import FakePayments
from .services.campaigns import CampaignService
from .services.pledges import PledgeService
from .services.settlement import SettlementService
from .store import InMemoryStore


def build_app(clock, payments=None):
    store = InMemoryStore()
    payments = payments or FakePayments()
    return CrowdApi(CampaignService(store), PledgeService(store, clock), SettlementService(store, payments, clock)), payments
