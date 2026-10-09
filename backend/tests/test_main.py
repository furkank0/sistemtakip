from collections.abc import Generator
from datetime import date, timedelta

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
    assert listed.json()["total"] == 1
    assert [item["id"] for item in listed.json()["items"]] == [asset["id"]]

    updated = client.patch(f"/api/assets/{asset['id']}", json={"status": "expired"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "expired"

    fetched = client.get(f"/api/assets/{asset['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["expires_at"] == date(2027, 1, 31).isoformat()

    deleted = client.delete(f"/api/assets/{asset['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/api/assets/{asset['id']}").status_code == 404


def test_asset_list_search_sort_and_pagination(client: TestClient) -> None:
    for name, vendor, owner in (
        ("charlie.example", "Third vendor", "Ops"),
        ("alpha.example", "First vendor", "Network"),
        ("bravo.example", "Second vendor", "Ops"),
    ):
        response = client.post(
            "/api/assets",
            json={"type": "domain", "name": name, "vendor": vendor, "owner": owner},
        )
        assert response.status_code == 201

    first_page = client.get(
        "/api/assets",
        params={"limit": 2, "sort_by": "name", "sort_direction": "asc"},
    )
    assert first_page.status_code == 200
    assert first_page.json()["total"] == 3
    assert first_page.json()["offset"] == 0
    assert [asset["name"] for asset in first_page.json()["items"]] == [
        "alpha.example",
        "bravo.example",
    ]

    second_page = client.get(
        "/api/assets",
        params={"limit": 2, "offset": 2, "sort_by": "name", "sort_direction": "asc"},
    )
    assert second_page.status_code == 200
    assert second_page.json()["offset"] == 2
    assert [asset["name"] for asset in second_page.json()["items"]] == ["charlie.example"]

    descending = client.get(
        "/api/assets",
        params={"limit": 2, "sort_by": "name", "sort_direction": "desc"},
    )
    assert [asset["name"] for asset in descending.json()["items"]] == [
        "charlie.example",
        "bravo.example",
    ]

    clamped_page = client.get("/api/assets", params={"limit": 2, "offset": 200})
    assert clamped_page.json()["offset"] == 2
    assert [asset["name"] for asset in clamped_page.json()["items"]] == ["charlie.example"]

    searched = client.get("/api/assets", params={"search": "SECOND VENDOR"})
    assert searched.status_code == 200
    assert searched.json()["total"] == 1
    assert [asset["name"] for asset in searched.json()["items"]] == ["bravo.example"]

    assert client.get("/api/assets", params={"sort_by": "unknown"}).status_code == 422
    assert client.get("/api/assets", params={"sort_direction": "sideways"}).status_code == 422


def test_contacts_can_be_managed_and_assigned_to_assets(client: TestClient) -> None:
    contact = client.post(
        "/api/contacts",
        json={
            "name": "  On-call Admin  ",
            "email": " admin@example.test ",
            "phone": " 555-0100 ",
            "role": " Operations ",
        },
    )
    assert contact.status_code == 201
    contact_data = contact.json()
    assert contact_data["name"] == "On-call Admin"
    assert contact_data["email"] == "admin@example.test"

    asset = client.post(
        "/api/assets",
        json={
            "type": "vds",
            "name": "server.example",
            "contact_ids": [contact_data["id"]],
        },
    )
    assert asset.status_code == 201
    assert asset.json()["contacts"] == [contact_data]

    listed = client.get("/api/contacts")
    assert listed.status_code == 200
    assert [entry["id"] for entry in listed.json()] == [contact_data["id"]]

    updated = client.patch(f"/api/assets/{asset.json()['id']}", json={"contact_ids": []})
    assert updated.status_code == 200
    assert updated.json()["contacts"] == []

    assigned = client.patch(
        f"/api/assets/{asset.json()['id']}", json={"contact_ids": [contact_data["id"]]}
    )
    assert assigned.status_code == 200
    assert client.delete(f"/api/contacts/{contact_data['id']}").status_code == 204
    assert client.get(f"/api/assets/{asset.json()['id']}").json()["contacts"] == []
    assert client.delete(f"/api/contacts/{contact_data['id']}").status_code == 404

    assert client.post("/api/contacts", json={"name": "   "}).status_code == 422
    assert (
        client.post(
            "/api/assets",
            json={
                "type": "domain",
                "name": "unknown-contact.example",
                "contact_ids": [999],
            },
        ).status_code
        == 422
    )


def test_renewal_notification_evaluation_is_idempotent_and_supports_overrides(
    client: TestClient,
) -> None:
    today = date(2026, 1, 1)
    default_asset = client.post(
        "/api/assets",
        json={"type": "domain", "name": "default.example", "expires_at": "2026-03-02"},
    ).json()
    custom_asset = client.post(
        "/api/assets",
        json={
            "type": "license",
            "name": "custom.example",
            "expires_at": "2026-01-04",
            "reminder_days": [3],
        },
    ).json()
    expired_asset = client.post(
        "/api/assets",
        json={
            "type": "hosting",
            "name": "expired.example",
            "expires_at": "2025-12-31",
            "reminder_days": [],
        },
    ).json()
    client.post(
        "/api/assets",
        json={
            "type": "vds",
            "name": "cancelled.example",
            "expires_at": "2026-01-02",
            "status": "cancelled",
        },
    )

    evaluation = client.post("/api/notifications/evaluate", params={"date": today.isoformat()})
    assert evaluation.status_code == 200
    result = evaluation.json()
    assert result["evaluated_on"] == today.isoformat()
    assert result["created_count"] == 3
    assert {
        (item["asset_id"], item["rule"], item["status"], item["channel"])
        for item in result["notifications"]
    } == {
        (default_asset["id"], "days:60", "pending", None),
        (custom_asset["id"], "days:3", "pending", None),
        (expired_asset["id"], "expired", "pending", None),
    }

    repeated = client.post("/api/notifications/evaluate", params={"date": today.isoformat()})
    assert repeated.status_code == 200
    assert repeated.json()["created_count"] == 0

    renewal = client.patch(f"/api/assets/{default_asset['id']}", json={"expires_at": "2026-03-03"})
    assert renewal.status_code == 200
    next_cycle = client.post("/api/notifications/evaluate", params={"date": "2026-01-02"})
    assert next_cycle.status_code == 200
    assert next_cycle.json()["created_count"] == 1

    assert (
        client.post(
            "/api/assets",
            json={
                "type": "domain",
                "name": "invalid-reminders.example",
                "reminder_days": [7, 7],
            },
        ).status_code
        == 422
    )
    assert (
        client.patch(f"/api/assets/{custom_asset['id']}", json={"reminder_days": [0]}).status_code
        == 422
    )

    assert client.get("/api/notifications").json()


def test_asset_crud_is_audited_and_note_values_are_redacted(client: TestClient) -> None:
    created = client.post(
        "/api/assets",
        json={
            "type": "domain",
            "name": "audit.example",
            "cost": "120.00",
            "notes": "private note should not be in audit",
        },
    )
    assert created.status_code == 201
    asset_id = created.json()["id"]

    updated = client.patch(
        f"/api/assets/{asset_id}",
        json={"name": "updated.example", "notes": "updated private note"},
    )
    assert updated.status_code == 200

    notes_updated = client.patch(f"/api/assets/{asset_id}", json={"notes": "another private note"})
    assert notes_updated.status_code == 200

    deleted = client.delete(f"/api/assets/{asset_id}")
    assert deleted.status_code == 204

    audit_log = client.get("/api/audit-log", params={"limit": 10})
    assert audit_log.status_code == 200
    events = audit_log.json()
    assert [event["action"] for event in events] == ["delete", "update", "update", "create"]
    assert all(event["actor"] == "anonymous" for event in events)
    assert all(event["entity"] == "asset" and event["entity_id"] == asset_id for event in events)
    assert events[0]["diff"]["deleted"]["name"] == "updated.example"
    assert events[1]["diff"] == {"notes": {"changed": True}}
    assert events[2]["diff"]["name"] == {
        "old": "audit.example",
        "new": "updated.example",
    }
    assert events[2]["diff"]["notes"] == {"changed": True}
    assert "notes" not in events[0]["diff"]["deleted"]
    assert "private note" not in str(events)
    assert events[3]["diff"]["created"]["cost"] == "120.00"
    assert "notes" not in events[3]["diff"]["created"]

    assert client.get("/api/audit-log", params={"limit": 101}).status_code == 422
    assert len(client.get("/api/audit-log", params={"limit": 1}).json()) == 1


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


def test_asset_csv_export_supports_filters(client: TestClient) -> None:
    contact = client.post("/api/contacts", json={"name": "CSV Contact"})
    assert contact.status_code == 201
    client.post(
        "/api/assets",
        json={
            "type": "domain",
            "name": "example.com",
            "vendor": "Example Registrar",
            "expires_at": "2027-01-31",
            "cost": "125.50",
            "cost_period": "yearly",
            "notes": "Yenileme notu",
            "contact_ids": [contact.json()["id"]],
        },
    )
    client.post(
        "/api/assets",
        json={"type": "hosting", "name": "hosting.example", "status": "cancelled"},
    )

    response = client.get("/api/assets/export.csv", params={"type": "domain"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert 'attachment; filename="assets-' in response.headers["content-disposition"]
    assert response.content.startswith(b"\xef\xbb\xbf")
    csv_body = response.content.decode("utf-8-sig")
    assert (
        "id,type,name,vendor,owner,cost,currency,cost_period,starts_at,expires_at,"
        "auto_renew,status,reminder_days,notes,tags,contacts" in csv_body
    )
    assert "example.com" in csv_body
    assert "hosting.example" not in csv_body
    assert "125.50,TRY,yearly,,2027-01-31" in csv_body
    assert "Yenileme notu" in csv_body
    assert "CSV Contact" in csv_body


def test_asset_tags_can_be_created_assigned_filtered_and_cleared(client: TestClient) -> None:
    created_tag = client.post("/api/tags", json={"name": "Üretim"})
    assert created_tag.status_code == 201
    tag = created_tag.json()

    created_asset = client.post(
        "/api/assets",
        json={"type": "vds", "name": "prod-vds-01", "tag_ids": [tag["id"]]},
    )
    assert created_asset.status_code == 201
    assert created_asset.json()["tags"] == [tag]

    filtered = client.get("/api/assets", params={"tag_id": tag["id"]})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    exported = client.get("/api/assets/export.csv", params={"tag_id": tag["id"]})
    assert exported.status_code == 200
    assert "prod-vds-01" in exported.content.decode("utf-8-sig")

    updated = client.patch(f"/api/assets/{created_asset.json()['id']}", json={"tag_ids": []})
    assert updated.status_code == 200
    assert updated.json()["tags"] == []

    unknown_tag = client.post(
        "/api/assets", json={"type": "domain", "name": "unknown.example", "tag_ids": [999]}
    )
    assert unknown_tag.status_code == 422


def test_vendor_can_be_managed_and_linked_to_assets(client: TestClient) -> None:
    created_vendor = client.post(
        "/api/vendors",
        json={
            "name": "Example Provider",
            "support_email": "support@example.test",
            "panel_url": "https://panel.example.test",
        },
    )
    assert created_vendor.status_code == 201
    vendor = created_vendor.json()

    created_asset = client.post(
        "/api/assets",
        json={"type": "hosting", "name": "linked-hosting", "vendor_id": vendor["id"]},
    )
    assert created_asset.status_code == 201
    assert created_asset.json()["vendor_id"] == vendor["id"]
    assert created_asset.json()["vendor"] == vendor["name"]

    filtered = client.get("/api/assets", params={"vendor_id": vendor["id"]})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    deleted = client.delete(f"/api/vendors/{vendor['id']}")
    assert deleted.status_code == 204


def test_dashboard_counts_assets_by_status_and_expiry(client: TestClient) -> None:
    today = date.today()
    for name, asset_type, asset_status, expires_at in (
        ("Active soon", "domain", "active", today + timedelta(days=10)),
        ("Active later", "hosting", "active", today + timedelta(days=70)),
        ("Expired", "license", "expired", today - timedelta(days=1)),
    ):
        response = client.post(
            "/api/assets",
            json={
                "type": asset_type,
                "name": name,
                "status": asset_status,
                "expires_at": expires_at.isoformat(),
            },
        )
        assert response.status_code == 201

    dashboard = client.get("/api/assets/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["total"] == 3
    assert dashboard.json()["active"] == 2
    assert dashboard.json()["expired"] == 1
    assert dashboard.json()["expiring_30_days"] == 1
    assert dashboard.json()["expiring_60_days"] == 1
    assert dashboard.json()["by_type"] == {"domain": 1, "hosting": 1, "license": 1}


def test_cost_periods_are_validated_and_currency_is_normalized(client: TestClient) -> None:
    created = client.post(
        "/api/assets",
        json={
            "type": "hosting",
            "name": "monthly-host",
            "cost": "19.99",
            "currency": "usd",
            "cost_period": "monthly",
        },
    )

    assert created.status_code == 201
    assert created.json()["currency"] == "USD"
    assert created.json()["cost_period"] == "monthly"

    invalid_period = client.post(
        "/api/assets",
        json={"type": "domain", "name": "bad-period", "cost_period": "quarterly"},
    )
    invalid_currency = client.post(
        "/api/assets",
        json={"type": "domain", "name": "bad-currency", "currency": "US"},
    )
    invalid_null_period = client.patch(
        f"/api/assets/{created.json()['id']}", json={"cost_period": None}
    )
    invalid_null_currency = client.patch(
        f"/api/assets/{created.json()['id']}", json={"currency": None}
    )
    assert invalid_period.status_code == 422
    assert invalid_currency.status_code == 422
    assert invalid_null_period.status_code == 422
    assert invalid_null_currency.status_code == 422


def test_dashboard_costs_are_annualized_and_grouped_by_currency(client: TestClient) -> None:
    costs = (
        ("monthly-usd", "10.00", "usd", "monthly"),
        ("yearly-usd", "120.00", "USD", "yearly"),
        ("one-time-usd", "30.00", "USD", "one_time"),
        ("legacy-usd", "50.00", "USD", "unspecified"),
        ("monthly-eur", "20.00", "EUR", "monthly"),
    )
    for name, cost, currency, cost_period in costs:
        response = client.post(
            "/api/assets",
            json={
                "type": "hosting",
                "name": name,
                "cost": cost,
                "currency": currency,
                "cost_period": cost_period,
            },
        )
        assert response.status_code == 201

    dashboard = client.get("/api/assets/dashboard")

    assert dashboard.status_code == 200
    assert dashboard.json()["costs_by_currency"] == [
        {
            "currency": "EUR",
            "monthly": "20.00",
            "yearly": "240.00",
            "one_time": "0",
            "unspecified": "0",
        },
        {
            "currency": "USD",
            "monthly": "20.00",
            "yearly": "240.00",
            "one_time": "30.00",
            "unspecified": "50.00",
        },
    ]

    legacy = client.post(
        "/api/assets", json={"type": "domain", "name": "legacy-without-period", "cost": "12"}
    )
    assert legacy.status_code == 201
    assert legacy.json()["cost_period"] == "unspecified"
