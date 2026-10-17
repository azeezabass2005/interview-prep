from datetime import datetime

from .errors import CrowdError
from .services.campaigns import CampaignService
from .services.pledges import PledgeService
from .services.settlement import SettlementService


class CrowdApi:
    def __init__(self, campaigns: CampaignService, pledges: PledgeService, settlement: SettlementService):
        self._campaigns = campaigns
        self._pledges = pledges
        self._settlement = settlement

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except CrowdError as exc:
            return exc.status, {"error": str(exc)}

    def create(self, body: dict):
        return self._call(lambda: {"id": self._campaigns.create(body["id"], body["goal"], datetime.fromisoformat(body["deadline"]),
                                                                body["tiers"]).campaign_id}, 201)

    def pledge(self, campaign_id: str, body: dict):
        return self._call(lambda: {"pledge_id": self._pledges.pledge(campaign_id, body["backer"], body["tier"], body["amount"]).pledge_id}, 201)

    def change(self, campaign_id: str, pledge_id: int, body: dict):
        return self._call(lambda: {"tier": self._pledges.change(campaign_id, pledge_id, body["tier"], body["amount"]).tier})

    def cancel(self, campaign_id: str, pledge_id: int):
        return self._call(lambda: {"status": self._pledges.cancel(campaign_id, pledge_id).status})

    def settle(self, campaign_id: str):
        def go():
            r = self._settlement.settle(campaign_id)
            return {k: (str(v) if not isinstance(v, (bool, list)) else v) for k, v in r.items()}
        return self._call(go)
