from unittest.mock import AsyncMock

from api.v1.routes import users
from auth.dependencies import get_authz_service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from users.dependencies import get_user_service
from users.user import User


def test_get_all_users_filters_by_read_access() -> None:
    app = FastAPI()
    app.include_router(users.router)

    # User should have permission to see himself and the "readable" user, but not the "hidden" user
    requester = _user("requester", "requester@example.com", "requester-id")
    readable = _user("readable", "readable@example.com", "readable-id")
    hidden = _user("hidden", "hidden@example.com", "hidden-id")

    user_service = AsyncMock()
    user_service.get_all_users.return_value = [requester, readable, hidden]

    authorization_service = AsyncMock()
    authorization_service.user_has_access.side_effect = (
        lambda _user_id, permission: True if permission in [f"read/users/{readable._id}", f"read/users/{requester._id}"] else False
    )

    app.dependency_overrides[get_user_service] = lambda: user_service
    app.dependency_overrides[get_authz_service] = lambda: authorization_service
    app.dependency_overrides[users.require_current_user] = lambda: requester

    response = TestClient(app).get("/api/v1/users")

    assert response.status_code == 200, response.text
    json = response.json()
    assert isinstance(json, list) and len(json) == 2, f"Expected 2 users, got {len(json)}: {json}"
    assert response.json() == [ # Should contain only the readable user and the requester
        {
            "_id": "requester-id",
            "_created_date": requester._created_date.isoformat(),
            "_updated_date": requester._updated_date.isoformat(),
            "user_name": "requester",
            "email": "requester@example.com",
            "email_verified": False,
        },
        {
            "_id": "readable-id",
            "_created_date": readable._created_date.isoformat(),
            "_updated_date": readable._updated_date.isoformat(),
            "user_name": "readable",
            "email": "readable@example.com",
            "email_verified": False,
        }
    ]
    authorization_service.user_has_access.assert_any_await(
        "requester-id",
        "read/users/readable-id",
    )
    authorization_service.user_has_access.assert_any_await(
        "requester-id",
        "read/users/readable-id",
    )
    authorization_service.user_has_access.assert_any_await(
        "requester-id",
        "read/users/hidden-id",
    )


def _user(user_name: str, email: str, user_id: str) -> User:
    user = User(user_name=user_name, password_hash="password", email=email)
    user._id = user_id
    return user
