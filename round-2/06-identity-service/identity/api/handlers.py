from ..clock import iso
from ..errors import Forbidden, NotFound, ValidationError
from ..http import Request, Response
from ..models import User
from ..passwords import hash_password, validate_new_password


def user_json(u: User, roles=None) -> dict:
    body = {"id": u.id, "org_id": u.org_id, "email": u.email, "name": u.name, "disabled": u.disabled}
    if roles is not None:
        body["roles"] = sorted(roles)
    return body


class Handlers:
    def __init__(self, auth, users, permissions, clock, ids):
        self._auth = auth
        self._users = users
        self._permissions = permissions
        self._clock = clock
        self._ids = ids

    def register(self, router) -> None:
        router.get("/health", lambda r: Response(200, {"status": "ok"}))
        router.post("/login", self.login)
        router.post("/logout", self.logout)
        router.get("/me", self.me)
        router.post("/password-reset", self.request_reset)
        router.post("/password-reset/confirm", self.confirm_reset)
        router.get("/admin/users", self.list_users)
        router.post("/admin/users", self.create_user)
        router.post("/admin/users/{user_id}/roles", self.grant)
        router.delete("/admin/users/{user_id}/roles/{role}", self.revoke)

    def login(self, request: Request) -> Response:
        data = request.json()
        return Response(200, self._auth.login(str(data.get("email", "")), str(data.get("password", ""))))

    def logout(self, request: Request) -> Response:
        self._auth.logout(request.headers.get("Authorization", "")[len("Bearer "):])
        return Response(204)

    def me(self, request: Request) -> Response:
        user = self._users.get(request.principal.user_id)
        return Response(200, {**user_json(user), "permissions": sorted(request.principal.roles)})

    def request_reset(self, request: Request) -> Response:
        self._auth.request_reset(str(request.json().get("email", "")))
        return Response(202, {"message": "If that address has an account, we've sent a reset link."})

    def confirm_reset(self, request: Request) -> Response:
        data = request.json()
        self._auth.confirm_reset(str(data.get("token", "")), str(data.get("password", "")))
        return Response(204)

    def _require(self, request: Request, permission: str) -> None:
        if not request.principal.has_role(permission):
            raise Forbidden(f"requires {permission}")

    def _same_org(self, request: Request, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None or user.org_id != request.principal.org_id:
            raise NotFound("user not found")
        return user

    def list_users(self, request: Request) -> Response:
        self._require(request, "users:read")
        return Response(200, {"users": [user_json(u, self._users.roles(u.id)) for u in self._users.in_org(request.principal.org_id)]})

    def create_user(self, request: Request) -> Response:
        self._require(request, "users:write")
        data = request.json()
        email = str(data.get("email", "")).strip().lower()
        if "@" not in email or self._users.by_email(email) is not None:
            raise ValidationError("a valid, unused email is required")
        password = str(data.get("password", ""))
        validate_new_password(password)
        user = User(self._ids.new("usr"), request.principal.org_id, email, str(data.get("name", email)), hash_password(password),
                    False, iso(self._clock.now()))
        self._users.add(user)
        self._permissions.grant(user.id, "member")
        return Response(201, user_json(user, {"member"}))

    def grant(self, request: Request) -> Response:
        self._require(request, "roles:write")
        user = self._same_org(request, request.params["user_id"])
        self._permissions.grant(user.id, str(request.json().get("role", "")))
        return Response(200, user_json(user, self._users.roles(user.id)))

    def revoke(self, request: Request) -> Response:
        self._require(request, "roles:write")
        user = self._same_org(request, request.params["user_id"])
        self._permissions.revoke(user.id, request.params["role"])
        return Response(200, user_json(user, self._users.roles(user.id)))
