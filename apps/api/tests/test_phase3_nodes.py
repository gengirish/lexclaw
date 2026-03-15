from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _register_and_org():
    register = client.post(
        "/v1/auth/register",
        json={
            "email": "phase3-owner@example.com",
            "password": "supersecure1",
            "full_name": "Phase Three Owner",
        },
    )
    token = register.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}
    created_org = client.post("/v1/orgs", json={"name": "Phase 3 Legal LLP"}, headers=auth_header)
    return auth_header, created_org.json()["id"]


def test_node_register_heartbeat_policy_and_entitlements():
    auth_header, org_id = _register_and_org()

    # purchase one skill so node sync has content
    skills = client.get("/v1/skills", headers=auth_header).json()
    skill_id = skills[0]["id"]
    client.post(f"/v1/orgs/{org_id}/skills/{skill_id}/purchase", headers=auth_header)

    register_node = client.post(
        "/v1/nodes/register",
        json={
            "org_id": org_id,
            "display_name": "Office Node 1",
            "runtime_version": "0.3.0",
            "public_key_fingerprint": "fp_1234567890abcdef",
        },
        headers=auth_header,
    )
    assert register_node.status_code == 200
    node = register_node.json()
    node_id = node["node_id"]
    node_header = {"X-Node-Token": node["issued_node_token"]}

    heartbeat = client.post(
        f"/v1/nodes/heartbeat?node_id={node_id}",
        json={"status": "healthy", "runtime_version": "0.3.0", "queue_depth": 2},
        headers=node_header,
    )
    assert heartbeat.status_code == 200
    assert heartbeat.json()["accepted"] is True

    policy = client.get(f"/v1/nodes/{node_id}/policy", headers=node_header)
    assert policy.status_code == 200
    assert policy.json()["telemetry_mode"] == "redacted-only"

    entitlements = client.get(f"/v1/nodes/{node_id}/entitlements", headers=node_header)
    assert entitlements.status_code == 200
    assert len(entitlements.json()["entitlement_codes"]) == 1


def test_node_redacted_telemetry_ingest():
    auth_header, org_id = _register_and_org()
    register_node = client.post(
        "/v1/nodes/register",
        json={
            "org_id": org_id,
            "display_name": "Office Node 2",
            "runtime_version": "0.3.0",
            "public_key_fingerprint": "fp_abcdef1234567890",
        },
        headers=auth_header,
    )
    node = register_node.json()
    node_header = {"X-Node-Token": node["issued_node_token"]}

    telemetry = client.post(
        "/v1/nodes/telemetry",
        json={
            "node_id": node["node_id"],
            "metrics": {"documents_processed_count": 17, "policy_gate_approvals": 3},
            "redaction_level": "strict",
        },
        headers=node_header,
    )
    assert telemetry.status_code == 200
    assert telemetry.json()["ok"] is True
