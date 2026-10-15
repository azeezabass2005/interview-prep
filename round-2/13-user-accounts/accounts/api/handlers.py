from dataclasses import dataclass, field

from ..errors import AccountsError
from ..services.auth import AuthService
from ..services.directory import DirectoryService
from ..services.reset import PasswordResetService
from ..services.signup import SignupService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


class AccountsApi:
    def __init__(self, db, clock):
        self.signup = SignupService(db, clock)
        self.auth = AuthService(db, clock)
        self.reset = PasswordResetService(db, clock)
        self.directory = DirectoryService(db)

    def _run(self, fn):
        try:
            return fn()
        except AccountsError as e:
            return Response(e.status, {"error": str(e)})

    def post_signup(self, body: dict) -> Response:
        return self._run(lambda: Response(201, {"user_id": self.signup.register(body.get("email"), body.get("name", ""),
                                                                                body.get("password"))}))

    def post_login(self, body: dict) -> Response:
        return self._run(lambda: Response(200, {"user_id": self.auth.login(body.get("email"), body.get("password")).user_id}))

    def post_reset(self, body: dict) -> Response:
        def go():
            self.reset.reset(body.get("token"), body.get("password"))
            return Response(200, {"status": "password updated"})
        return self._run(go)

    def get_directory(self, q: str) -> Response:
        return Response(200, {"results": self.directory.search(q)})
