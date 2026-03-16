import hashlib
import json

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _bootstrap_node():
    register = client.post(
        "/v1/auth/register",
        json={
            "email": "phase4-owner@example.com",
            "password": "supersecure1",
            "full_name": "Phase Four Owner",
        },
    )
    token = register.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}
    org_id = client.post("/v1/orgs", json={"name": "Phase 4 Legal LLP"}, headers=auth_header).json()["id"]
    node = client.post(
        "/v1/nodes/register",
        json={
            "org_id": org_id,
            "display_name": "Office Node 4",
            "runtime_version": "0.4.0",
            "public_key_fingerprint": "fp_phase4_abcdef",
        },
        headers=auth_header,
    ).json()
    return auth_header, org_id, node["node_id"], {"X-Node-Token": node["issued_node_token"]}


def test_node_audit_hash_chain_and_org_view():
    auth_header, org_id, node_id, node_header = _bootstrap_node()

    meta_one = {"skill_id": "deadline-extractor", "input_digest": "aaa", "output_digest": "bbb"}
    payload_one = json.dumps(meta_one, sort_keys=True)
    hash_one = hashlib.sha256(f":{payload_one}".encode("utf-8")).hexdigest()

    created_one = client.post(
        "/v1/nodes/audit-events",
        json={
            "node_id": node_id,
            "action": "skill.execute",
            "metadata": meta_one,
            "previous_hash": None,
            "event_hash": hash_one,
        },
        headers=node_header,
    )
    assert created_one.status_code == 200

    meta_two = {"skill_id": "deposition-summarizer", "input_digest": "ccc", "output_digest": "ddd"}
    payload_two = json.dumps(meta_two, sort_keys=True)
    hash_two = hashlib.sha256(f"{hash_one}:{payload_two}".encode("utf-8")).hexdigest()
    created_two = client.post(
        "/v1/nodes/audit-events",
        json={
            "node_id": node_id,
            "action": "skill.execute",
            "metadata": meta_two,
            "previous_hash": hash_one,
            "event_hash": hash_two,
        },
        headers=node_header,
    )
    assert created_two.status_code == 200

    events = client.get(f"/v1/orgs/{org_id}/audit-events", headers=auth_header)
    assert events.status_code == 200
    payload = events.json()
    assert len(payload) == 2
    assert payload[0]["event_hash"] == hash_two
    assert payload[0]["previous_hash"] == hash_one


def test_rejects_content_like_audit_metadata_keys():
    _, _, node_id, node_header = _bootstrap_node()
    bad = client.post(
        "/v1/nodes/audit-events",
        json={
            "node_id": node_id,
            "action": "skill.execute",
            "metadata": {"content": "should not be accepted"},
            "previous_hash": None,
            "event_hash": "abc",
        },
        headers=node_header,
    )
    assert bad.status_code == 400


def test_rejects_invalid_audit_event_hash():
    _, _, node_id, node_header = _bootstrap_node()
    invalid = client.post(
        "/v1/nodes/audit-events",
        json={
            "node_id": node_id,
            "action": "skill.execute",
            "metadata": {"skill_id": "deadline-extractor", "input_digest": "aaa", "output_digest": "bbb"},
            "previous_hash": None,
            "event_hash": "not-a-real-chain-hash",
        },
        headers=node_header,
    )
    assert invalid.status_code == 400
