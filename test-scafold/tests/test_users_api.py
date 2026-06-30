from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


APP_ROOT = Path(os.environ.get("TEST_SCAFOLD_APP_ROOT", "test-scafold/app")).resolve()
SERVER_ROOT = APP_ROOT / "server"


def _clear_scaffold_modules() -> None:
    prefixes = ("api", "auth", "config", "db", "main", "models", "service")
    for module_name in list(sys.modules):
        if any(module_name == prefix or module_name.startswith(prefix + ".") for prefix in prefixes):
            sys.modules.pop(module_name, None)


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    assert APP_ROOT.exists(), f"scaffold app does not exist: {APP_ROOT}"
    assert SERVER_ROOT.exists(), f"scaffold server package does not exist: {SERVER_ROOT}"

    monkeypatch.setenv("APP_DB_NAME", f"api_tests_{uuid4().hex}")
    _clear_scaffold_modules()

    sys.path.insert(0, str(APP_ROOT))
    sys.path.insert(0, str(SERVER_ROOT))
    main = importlib.import_module("main")
    return TestClient(main.app)


def _unique_user_payload() -> dict[str, str]:
    suffix = uuid4().hex
    return {
        "user_name": f"user_{suffix}",
        "password": "correct-horse-battery-staple",
        "email": f"user_{suffix}@example.com",
    }


def _create_user(client: TestClient, payload: dict[str, str]) -> str:
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body
    return body["_id"] if isinstance(body, dict) else body


def test_create_and_list_users(client: TestClient) -> None:
    payload = _unique_user_payload()
    user_id = _create_user(client, payload)

    assert isinstance(user_id, str)
    assert user_id

    response = client.get("/api/v1/users")
    assert response.status_code == 200, response.text
    users = response.json()

    assert any(user["user_name"] == payload["user_name"] for user in users)
    assert any(user["email"] == payload["email"] for user in users)


def test_duplicate_user_name_is_rejected(client: TestClient) -> None:
    payload = _unique_user_payload()
    _create_user(client, payload)

    duplicate = dict(payload)
    duplicate["email"] = f"other_{uuid4().hex}@example.com"
    response = client.post("/api/v1/users", json=duplicate)

    assert response.status_code == 422, response.text
    assert "Username is already taken" in response.text


def test_login_creates_session_and_session_listing_shows_user(client: TestClient) -> None:
    payload = _unique_user_payload()
    _create_user(client, payload)

    login_response = client.post(
        "/api/v1/sessions/login",
        json={"user_name": payload["user_name"], "password": payload["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    session_id = login_response.json()
    assert isinstance(session_id, str)
    assert session_id

    sessions_response = client.get("/api/v1/sessions")
    assert sessions_response.status_code == 200, sessions_response.text
    assert payload["user_name"] in sessions_response.text


def test_login_rejects_bad_password(client: TestClient) -> None:
    payload = _unique_user_payload()
    _create_user(client, payload)

    response = client.post(
        "/api/v1/sessions/login",
        json={"user_name": payload["user_name"], "password": "wrong"},
    )

    assert response.status_code == 401, response.text
