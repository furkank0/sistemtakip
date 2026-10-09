from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_get_db() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client: TestClient) -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}


def test_api_docs_are_available(client: TestClient) -> None:
    response = client.get("/api/docs")

    assert response.status_code == 200
    assert "sistemtakip API" in response.text


def test_asset_crud_and_filters(client: TestClient) -> None:
    payload = {
        "type": "domain",
        "name": "example.com",
        "vendor": "Example Registrar",
        "expires_at": "2027-01-31",
        "auto_renew": True,
    }

    created = client.post("/api/assets", json=payload)
    assert created.status_code == 201
    asset = created.json()
    assert asset["name"] == "example.com"
    assert asset["currency"] == "TRY"

    listed = client.get("/api/assets", params={"type": "domain"})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [asset["id"]]

    updated = client.patch(f"/api/assets/{asset['id']}", json={"status": "expired"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "expired"

    fetched = client.get(f"/api/assets/{asset['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["expires_at"] == date(2027, 1, 31).isoformat()

    deleted = client.delete(f"/api/assets/{asset['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/assets/{asset['id']}").status_code == 404


def test_asset_rejects_invalid_date_range(client: TestClient) -> None:
    response = client.post(
        "/api/assets",
        json={
            "type": "license",
            "name": "Invalid",
            "starts_at": "2027-02-01",
            "expires_at": "2027-01-01",
        },
    )

    assert response.status_code == 422
