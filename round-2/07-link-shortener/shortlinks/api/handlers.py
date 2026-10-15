from dataclasses import dataclass, field

from ..errors import LinkError
from ..services.links import LinkService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)


class LinkApi:
    def __init__(self, service: LinkService):
        self._service = service

    def post_link(self, owner: str, body: dict) -> Response:
        try:
            link = self._service.create(owner, body.get("target_url"), body.get("alias"), body.get("ttl_days"))
        except LinkError as e:
            return Response(e.status, {"error": str(e)})
        return Response(201, {"code": link.code, "short_url": f"https://bbg.link/{link.code}"})

    def get_redirect(self, code: str, referrer=None) -> Response:
        try:
            target = self._service.resolve(code, referrer)
        except LinkError as e:
            return Response(e.status, {"error": str(e)})
        return Response(302, headers={"Location": target})

    def get_info(self, code: str) -> Response:
        try:
            return Response(200, self._service.info(code))
        except LinkError as e:
            return Response(e.status, {"error": str(e)})
