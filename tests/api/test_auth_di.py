from types import SimpleNamespace

from api.auth import (
    get_auth_required,
    get_permission_requirement,
    requires_all_permissions,
    requires_any_permission,
    requires_auth,
    requires_permission,
)
from api.auth.dependencies import get_request_context
from api.auth.route import AuthzRoute
from api.decorators.authenticated import authenticated
from api.decorators.check_permissions import check_permission
from api.router import Router
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient
from service.dependencies import get_authz_service


class StubAuthorizationService:
    def __init__(self, allowed: set[str]):
        self.allowed = allowed
        self.checked: list[str] = []

    def user_has_access(self, user_id: object, permission: str) -> bool:
        self.checked.append(permission)
        return permission in self.allowed


def test_requires_auth_marks_endpoint():
    @requires_auth
    def endpoint():
        pass

    assert get_auth_required(endpoint)
    assert get_permission_requirement(endpoint) is None


def test_permission_annotations_store_metadata():
    @requires_permission("read/users/{user_id}")
    def single():
        pass

    @requires_any_permission("read/users/{user_id}", "manage/users/**")
    def any_permission():
        pass

    @requires_all_permissions("read/users/{user_id}", "audit/users/{user_id}")
    def all_permissions():
        pass

    assert get_permission_requirement(single).permissions == ("read/users/{user_id}",)
    assert get_permission_requirement(single).mode == "all"
    assert get_permission_requirement(any_permission).mode == "any"
    assert get_permission_requirement(all_permissions).mode == "all"


def test_compatibility_annotations_are_metadata_only():
    def auth_endpoint():
        pass

    def permission_endpoint():
        pass

    decorated_auth = authenticated()(auth_endpoint)
    decorated_permission = check_permission("read/users/{user_id}")(
        permission_endpoint
    )

    assert decorated_auth is auth_endpoint
    assert decorated_permission is permission_endpoint
    assert get_auth_required(decorated_auth)
    assert get_permission_requirement(decorated_permission).permissions == (
        "read/users/{user_id}",
    )


def test_router_uses_authz_route_and_keeps_public_routes_public():
    app, client, _ = _build_client(lambda endpoint: endpoint, authenticated=False)

    assert isinstance(app.routes[-1], AuthzRoute)
    assert client.get("/items/42").status_code == 200


def test_requires_auth_rejects_missing_user():
    _, client, _ = _build_client(requires_auth, authenticated=False)

    assert client.get("/items/42").status_code == 401


def test_permission_rejects_missing_user_before_authorization():
    _, client, authorization_service = _build_client(
        requires_permission("read/items/{item_id}"),
        authenticated=False,
        allowed={"read/items/42"},
    )

    assert client.get("/items/42").status_code == 401
    assert authorization_service.checked == []


def test_permission_denies_missing_grant():
    _, client, authorization_service = _build_client(
        requires_permission("read/items/{item_id}"),
        allowed=set(),
    )

    assert client.get("/items/42").status_code == 403
    assert authorization_service.checked == ["read/items/42"]


def test_permission_allows_matching_grant_and_resolves_path_params():
    _, client, authorization_service = _build_client(
        requires_permission("read/items/{item_id}"),
        allowed={"read/items/42"},
    )

    assert client.get("/items/42").status_code == 200
    assert authorization_service.checked == ["read/items/42"]


def test_any_permission_passes_when_one_grant_matches():
    _, client, _ = _build_client(
        requires_any_permission(
            "read/items/{item_id}",
            "manage/items/**",
        ),
        allowed={"manage/items/**"},
    )

    assert client.get("/items/42").status_code == 200


def test_all_permissions_requires_every_grant():
    _, client, _ = _build_client(
        requires_all_permissions(
            "read/items/{item_id}",
            "audit/items/{item_id}",
        ),
        allowed={"read/items/42"},
    )

    assert client.get("/items/42").status_code == 403


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
