from dataclasses import asdict

from ..errors import ValidationError
from ..http import Request, Response


class Handlers:
    def __init__(self, rules, engine, deliveries):
        self._rules = rules
        self._engine = engine
        self._deliveries = deliveries

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.get("/rules", self.list_rules)
        router.post("/rules", self.create_rule)
        router.delete("/rules/{rule_id}", self.delete_rule)
        router.get("/deliveries", self.deliveries)
        router.post("/internal/prices", self.price)

    def list_rules(self, request: Request) -> Response:
        rules = self._rules.list(request.principal, request.query.get("user_id"))
        return Response(200, {"rules": [asdict(r) for r in rules]})

    def create_rule(self, request: Request) -> Response:
        return Response(201, asdict(self._rules.create(request.principal, request.json())))

    def delete_rule(self, request: Request) -> Response:
        self._rules.delete(request.principal, request.params["rule_id"])
        return Response(204)

    def deliveries(self, request: Request) -> Response:
        items = self._deliveries.for_user(request.principal.user_id)
        return Response(200, {"deliveries": [{k: v for k, v in asdict(d).items() if k != "recipient"} for d in items]})

    def price(self, request: Request) -> Response:
        request.principal.require_role("feed")
        data = request.json()
        try:
            price = float(data["price"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValidationError("price must be a number") from e
        return Response(200, {"fired": self._engine.on_price(str(data.get("symbol", "")), price)})
