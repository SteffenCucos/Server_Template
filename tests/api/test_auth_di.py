from types import SimpleNamespace

from api.auth.dependencies import get_request_context
from api.auth.route import AuthzRoute
from api.auth.route_permissions import get_auth_required, get_permission_requirement
from api.decorators.authenticated import authenticated
from api.decorators.check_permissions import check_permission
from api.router import Router
from auth.dependencies import get_authz_service
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient


class StubAuthorizationService:
    def __init__(self, allowed: set[str]):
        self.allowed = allowed
        self.checked: list[str] = []

    def user_has_access(self, user_id: object, permission: str) -> bool:
        self.checked.append(permission)
        return permission in self.allowed


def test_authenticated_marks_endpoint():
    def endpoint():
        pass

    decorated = authenticated()(endpoint)

    assert decorated is endpoint
    assert get_auth_required(endpoint)
    assert get_permission_requirement(endpoint) is None


def test_check_permission_stores_metadata_and_requires_auth():
    def endpoint():
        pass

    decorated = check_permission("read/users/{user_id}")(endpoint)

    assert decorated is endpoint
    assert get_auth_required(endpoint)
    assert get_permission_requirement(endpoint).permission == "read/users/{user_id}"


def test_router_uses_authz_route_and_keeps_public_routes_public():
    app, client, _ = _build_client(lambda endpoint: endpoint, authenticated=False)

    registered_router = getattr(app.routes[-1], "original_router", None)
    registered_route = (
        registered_router.routes[0]
        if registered_router is not None
        else app.routes[-1]
    )
    assert isinstance(registered_route, AuthzRoute)
    assert client.get("/items/42").status_code == 200


def test_authenticated_rejects_missing_user():
    _, client, _ = _build_client(authenticated(), authenticated=False)

    assert client.get("/items/42").status_code == 401


def test_check_permission_rejects_missing_user_before_authorization():
    _, client, authorization_service = _build_client(
        check_permission("read/items/{item_id}"),
        authenticated=False,
        allowed={"read/items/42"},
    )

    assert client.get("/items/42").status_code == 401
    assert authorization_service.checked == []


def test_check_permission_denies_missing_grant():
    _, client, authorization_service = _build_client(
        check_permission("read/items/{item_id}"),
        allowed=set(),
    )

    assert client.get("/items/42").status_code == 403
    assert authorization_service.checked == ["read/items/42"]


def test_check_permission_allows_grant_and_resolves_path_params():
    _, client, authorization_service = _build_client(
        check_permission("read/items/{item_id}"),
        allowed={"read/items/42"},
    )

    assert client.get("/items/42").status_code == 200
    assert authorization_service.checked == ["read/items/42"]


def _build_client(
    annotation,
    *,
    authenticated: bool = True,
    allowed: set[str] | None = None,
):
    app = FastAPI()
    router = Router(prefix="/items")

    def endpoint(item_id: str):
        return HTMLResponse("ok")

    router.get("/{item_id}")(annotation(endpoint))
    app.include_router(router)

    user = SimpleNamespace(_id="user-1") if authenticated else None
    request_context = SimpleNamespace(
        current_user=user,
        session=object() if authenticated else None,
        session_expired=False if authenticated else None,
    )
    authorization_service = StubAuthorizationService(allowed or set())

    app.dependency_overrides[get_request_context] = lambda: request_context
    app.dependency_overrides[get_authz_service] = lambda: authorization_service

    return app, TestClient(app), authorization_service
