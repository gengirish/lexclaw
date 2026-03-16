"""Cloud connector for LexClaw on-prem runtime (Phase 3 scaffold)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import request


@dataclass
class ConnectorConfig:
    control_plane_url: str
    org_id: str
    bootstrap_access_token: str
    node_display_name: str
    runtime_version: str
    public_key_fingerprint: str


class CloudConnector:
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.node_id: str | None = os.getenv("LEXCLAW_NODE_ID")
        self.node_token: str | None = os.getenv("LEXCLAW_NODE_TOKEN")

    def _request(self, method: str, path: str, headers: dict[str, str], payload: dict[str, Any] | None = None) -> dict:
        body = None
        req_headers = {"Content-Type": "application/json", **headers}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        req = request.Request(f"{self.config.control_plane_url}{path}", data=body, headers=req_headers, method=method)
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def register_node(self) -> dict:
        response = self._request(
            method="POST",
            path="/v1/nodes/register",
            headers={"Authorization": f"Bearer {self.config.bootstrap_access_token}"},
            payload={
                "org_id": self.config.org_id,
                "display_name": self.config.node_display_name,
                "runtime_version": self.config.runtime_version,
                "public_key_fingerprint": self.config.public_key_fingerprint,
            },
        )
        self.node_id = response["node_id"]
        self.node_token = response["issued_node_token"]
        return response

    def send_heartbeat(self, status: str, queue_depth: int) -> dict:
        if not self.node_id or not self.node_token:
            raise ValueError("node is not registered")
        return self._request(
            method="POST",
            path=f"/v1/nodes/heartbeat?node_id={self.node_id}",
            headers={"X-Node-Token": self.node_token},
            payload={
                "status": status,
                "runtime_version": self.config.runtime_version,
                "queue_depth": queue_depth,
            },
        )

    def pull_policy(self) -> dict:
        if not self.node_id or not self.node_token:
            raise ValueError("node is not registered")
        return self._request(
            method="GET",
            path=f"/v1/nodes/{self.node_id}/policy",
            headers={"X-Node-Token": self.node_token},
        )

    def sync_entitlements(self) -> dict:
        if not self.node_id or not self.node_token:
            raise ValueError("node is not registered")
        return self._request(
            method="GET",
            path=f"/v1/nodes/{self.node_id}/entitlements",
            headers={"X-Node-Token": self.node_token},
        )

    def publish_redacted_telemetry(self, metrics: dict[str, int]) -> dict:
        if not self.node_id or not self.node_token:
            raise ValueError("node is not registered")
        return self._request(
            method="POST",
            path="/v1/nodes/telemetry",
            headers={"X-Node-Token": self.node_token},
            payload={
                "node_id": self.node_id,
                "metrics": metrics,
                "redaction_level": "strict",
            },
        )

    def publish_audit_event(self, action: str, metadata: dict, previous_hash: str | None, event_hash: str) -> dict:
        if not self.node_id or not self.node_token:
            raise ValueError("node is not registered")
        return self._request(
            method="POST",
            path="/v1/nodes/audit-events",
            headers={"X-Node-Token": self.node_token},
            payload={
                "node_id": self.node_id,
                "action": action,
                "metadata": metadata,
                "previous_hash": previous_hash,
                "event_hash": event_hash,
            },
        )
