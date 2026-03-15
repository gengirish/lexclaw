from cloud_connector import CloudConnector, ConnectorConfig


def test_connector_register_and_sync_methods():
    config = ConnectorConfig(
        control_plane_url="http://localhost:8000",
        org_id="org-1",
        bootstrap_access_token="token",
        node_display_name="Office Node",
        runtime_version="0.3.0",
        public_key_fingerprint="fp_12345678",
    )
    connector = CloudConnector(config)

    calls = []

    def fake_request(method, path, headers, payload=None):
        calls.append((method, path, headers, payload))
        if path == "/v1/nodes/register":
            return {"node_id": "node-1", "issued_node_token": "node-token-1"}
        if path.startswith("/v1/nodes/heartbeat"):
            return {"accepted": True}
        if path.endswith("/policy"):
            return {"policy_version": "phase3-v1"}
        if path.endswith("/entitlements"):
            return {"entitlement_codes": ["deposition-summarizer"]}
        if path == "/v1/nodes/telemetry":
            return {"ok": True}
        if path == "/v1/nodes/audit-events":
            return {"event_id": "evt-1"}
        return {}

    connector._request = fake_request

    reg = connector.register_node()
    hb = connector.send_heartbeat(status="healthy", queue_depth=0)
    pol = connector.pull_policy()
    ent = connector.sync_entitlements()
    telem = connector.publish_redacted_telemetry({"documents_processed_count": 1})
    audit = connector.publish_audit_event(
        action="skill.execute",
        metadata={"skill_id": "deposition-summarizer", "input_digest": "abc"},
        previous_hash=None,
        event_hash="hash-1",
    )

    assert reg["node_id"] == "node-1"
    assert hb["accepted"] is True
    assert pol["policy_version"] == "phase3-v1"
    assert ent["entitlement_codes"] == ["deposition-summarizer"]
    assert telem["ok"] is True
    assert audit["event_id"] == "evt-1"
    assert len(calls) == 6
