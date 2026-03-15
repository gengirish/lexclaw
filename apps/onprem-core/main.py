"""LexClaw on-prem core scaffold (Phase 3)."""

from dataclasses import dataclass
import os
from pathlib import Path

from cloud_connector import CloudConnector, ConnectorConfig
from legal_skills import SkillExecutionRequest, SkillRegistry

@dataclass
class ConnectorState:
    connected: bool
    node_id: str


def bootstrap() -> ConnectorState:
    control_plane_url = os.getenv("LEXCLAW_CONTROL_PLANE_URL", "http://localhost:8000")
    org_id = os.getenv("LEXCLAW_ORG_ID", "")
    bootstrap_token = os.getenv("LEXCLAW_BOOTSTRAP_ACCESS_TOKEN", "")
    node_display_name = os.getenv("LEXCLAW_NODE_DISPLAY_NAME", "Office Node")
    runtime_version = os.getenv("LEXCLAW_RUNTIME_VERSION", "0.3.0")
    public_key_fingerprint = os.getenv("LEXCLAW_PUBLIC_KEY_FINGERPRINT", "dev-fingerprint")

    if not org_id or not bootstrap_token:
        return ConnectorState(connected=False, node_id="unconfigured")

    connector = CloudConnector(
        ConnectorConfig(
            control_plane_url=control_plane_url,
            org_id=org_id,
            bootstrap_access_token=bootstrap_token,
            node_display_name=node_display_name,
            runtime_version=runtime_version,
            public_key_fingerprint=public_key_fingerprint,
        )
    )
    registered = connector.register_node()
    connector.send_heartbeat(status="healthy", queue_depth=0)
    connector.pull_policy()
    connector.sync_entitlements()
    connector.publish_redacted_telemetry({"startup_events": 1})

    registry = SkillRegistry()
    package_dir = Path(__file__).parent / "skill-packages"
    for manifest in registry.load_manifests(str(package_dir)):
        registry.install_skill(manifest)

    entitlement_payload = connector.sync_entitlements()
    entitlement_codes = set(entitlement_payload.get("entitlement_codes", []))
    if "deposition-summarizer" in entitlement_codes:
        result = registry.execute(
            SkillExecutionRequest(
                org_id=org_id,
                node_id=registered["node_id"],
                skill_id="deposition-summarizer",
                input_text="Witness testified on 2026-04-01 regarding filing timeline.",
                approved_by="operator@example.com",
            ),
            entitlement_codes=entitlement_codes,
            policy_require_human_approval=True,
        )
        connector.publish_audit_event(
            action=result.audit_metadata["action"],
            metadata={
                "skill_id": result.audit_metadata["skill_id"],
                "skill_version": result.audit_metadata["skill_version"],
                "input_digest": result.audit_metadata["input_digest"],
                "output_digest": result.audit_metadata["output_digest"],
                "approved_by": result.audit_metadata["approved_by"],
            },
            previous_hash=result.audit_metadata["previous_hash"],
            event_hash=result.audit_metadata["event_hash"],
        )
    return ConnectorState(connected=True, node_id=registered["node_id"])


if __name__ == "__main__":
    state = bootstrap()
    print(f"On-prem core initialized: connected={state.connected}, node_id={state.node_id}")
