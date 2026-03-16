from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


client = TestClient(app)


def _register_and_org():
    register = client.post(
        "/v1/auth/register",
        json={
            "email": "phase2-owner@example.com",
            "password": "supersecure1",
            "full_name": "Phase Two Owner",
        },
    )
    token = register.json()["access_token"]

    created_org = client.post(
        "/v1/orgs",
        json={"name": "Phase 2 Legal LLP"},
        headers={"Authorization": f"Bearer {token}"},
    )
    org_id = created_org.json()["id"]
    return token, org_id


def test_billing_checkout_webhook_and_subscription():
    token, org_id = _register_and_org()
    auth_header = {"Authorization": f"Bearer {token}"}

    checkout = client.post(
        "/v1/billing/checkout-session",
        json={"org_id": org_id, "plan_code": "professional", "seats": 5},
        headers=auth_header,
    )
    assert checkout.status_code == 200
    assert checkout.json()["status"] == "created"

    webhook = client.post(
        "/v1/billing/webhook",
        json={
            "provider_event_id": "evt_001",
            "event_type": "customer.subscription.updated",
            "org_id": org_id,
            "plan_code": "professional",
            "status": "active",
        },
        headers={"X-Lexclaw-Signature": settings.billing_webhook_secret},
    )
    assert webhook.status_code == 200
    assert webhook.json()["deduped"] is False

    webhook_dup = client.post(
        "/v1/billing/webhook",
        json={
            "provider_event_id": "evt_001",
            "event_type": "customer.subscription.updated",
            "org_id": org_id,
            "plan_code": "professional",
            "status": "active",
        },
        headers={"X-Lexclaw-Signature": settings.billing_webhook_secret},
    )
    assert webhook_dup.status_code == 200
    assert webhook_dup.json()["deduped"] is True

    sub = client.get(f"/v1/billing/subscription?org_id={org_id}", headers=auth_header)
    assert sub.status_code == 200
    assert sub.json()["plan_code"] == "professional"
    assert sub.json()["status"] == "active"


def test_skills_purchase_and_licenses():
    token, org_id = _register_and_org()
    auth_header = {"Authorization": f"Bearer {token}"}

    skills = client.get("/v1/skills", headers=auth_header)
    assert skills.status_code == 200
    skill_id = skills.json()[0]["id"]

    purchase = client.post(f"/v1/orgs/{org_id}/skills/{skill_id}/purchase", headers=auth_header)
    assert purchase.status_code == 200
    assert purchase.json()["org_id"] == org_id

    entitlements = client.get(f"/v1/orgs/{org_id}/entitlements", headers=auth_header)
    assert entitlements.status_code == 200
    assert len(entitlements.json()) == 1

    issued = client.post(
        "/v1/licenses/issue",
        json={"org_id": org_id, "node_id": "node-a", "ttl_days": 14},
        headers=auth_header,
    )
    assert issued.status_code == 200
    token_value = issued.json()["token"]

    validate = client.get(f"/v1/licenses/validate?token={token_value}")
    assert validate.status_code == 200
    assert validate.json()["valid"] is True
    assert validate.json()["org_id"] == org_id

    rotate = client.post(
        "/v1/licenses/rotate",
        json={"org_id": org_id, "node_id": "node-a", "ttl_days": 14},
        headers=auth_header,
    )
    assert rotate.status_code == 200
    assert rotate.json()["license_id"] != issued.json()["license_id"]
