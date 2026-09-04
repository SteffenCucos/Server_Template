from fastapi.testclient import TestClient

from test_users_api import client


def test_health_reports_running_database(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200, response.text
    assert response.json() == {"running": True, "database": True}
