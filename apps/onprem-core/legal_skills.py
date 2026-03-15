"""Local legal skill runtime with entitlement and approval gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path


SIGNING_NAMESPACE = "lexclaw-signed"
PRODUCTION_SKILLS = {"deposition-summarizer", "contract-clause-risk-flagger", "deadline-extractor"}
STUB_SKILLS = {"matter-intake-triage", "pacer-search-adapter"}


@dataclass
class SkillManifest:
    id: str
    version: str
    requires_entitlement: bool
    execution_policy: dict
    package_checksum: str
    signature: str


@dataclass
class SkillExecutionRequest:
    org_id: str
    node_id: str
    skill_id: str
    input_text: str
    approved_by: str | None = None


@dataclass
class SkillExecutionResult:
    skill_id: str
    version: str
    output_json: dict
    human_summary: str
    audit_metadata: dict


@dataclass
class AuditMetadataChain:
    events: list[dict] = field(default_factory=list)
    previous_hash: str | None = None

    def append(self, event: dict) -> dict:
        serialized = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(f"{self.previous_hash or ''}:{serialized}".encode("utf-8")).hexdigest()
        stored = {**event, "previous_hash": self.previous_hash, "event_hash": event_hash}
        self.events.append(stored)
        self.previous_hash = event_hash
        return stored


def _manifest_signature(skill_id: str, version: str, package_checksum: str) -> str:
    raw = f"{skill_id}:{version}:{package_checksum}:{SIGNING_NAMESPACE}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _content_digest(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


class SkillRegistry:
    def __init__(self):
        self.manifests: dict[str, SkillManifest] = {}
        self.install_history: dict[str, list[SkillManifest]] = {}
        self.audit_chain = AuditMetadataChain()

    def load_manifests(self, package_dir: str) -> list[SkillManifest]:
        loaded = []
        for path in sorted(Path(package_dir).glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            manifest = SkillManifest(**payload)
            self._verify_manifest(manifest)
            loaded.append(manifest)
        return loaded

    def _verify_manifest(self, manifest: SkillManifest) -> None:
        expected = _manifest_signature(manifest.id, manifest.version, manifest.package_checksum)
        if manifest.signature != expected:
            raise ValueError(f"invalid signature for {manifest.id}")

    def install_skill(self, manifest: SkillManifest) -> None:
        self._verify_manifest(manifest)
        previous = self.manifests.get(manifest.id)
        if previous and previous.version == manifest.version:
            return
        self.manifests[manifest.id] = manifest
        history = self.install_history.setdefault(manifest.id, [])
        history.append(manifest)

    def rollback_skill(self, skill_id: str) -> None:
        history = self.install_history.get(skill_id, [])
        if len(history) < 2:
            raise ValueError("no rollback target")
        history.pop()
        self.manifests[skill_id] = history[-1]

    def execute(
        self,
        request: SkillExecutionRequest,
        entitlement_codes: set[str],
        policy_require_human_approval: bool,
    ) -> SkillExecutionResult:
        manifest = self.manifests.get(request.skill_id)
        if not manifest:
            raise ValueError("skill not installed")

        if manifest.requires_entitlement and request.skill_id not in entitlement_codes:
            raise ValueError("missing entitlement")

        requires_approval = policy_require_human_approval or bool(
            manifest.execution_policy.get("requires_human_approval")
        )
        if requires_approval and not request.approved_by:
            raise ValueError("human approval required")

        output_json, human_summary = _execute_skill_logic(request.skill_id, request.input_text)
        audit_event = self.audit_chain.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "org_id": request.org_id,
                "node_id": request.node_id,
                "action": "skill.execute",
                "skill_id": request.skill_id,
                "skill_version": manifest.version,
                "input_digest": _content_digest(request.input_text),
                "output_digest": _content_digest(json.dumps(output_json, sort_keys=True)),
                "approved_by": request.approved_by or "n/a",
            }
        )
        return SkillExecutionResult(
            skill_id=request.skill_id,
            version=manifest.version,
            output_json=output_json,
            human_summary=human_summary,
            audit_metadata=audit_event,
        )


def _execute_skill_logic(skill_id: str, input_text: str) -> tuple[dict, str]:
    normalized = " ".join(input_text.split())
    lower_text = normalized.lower()
    digest = _content_digest(normalized)[:12]

    if skill_id == "deposition-summarizer":
        sentence_count = max(1, len(re.findall(r"[.!?]+", normalized)))
        names_detected = len(re.findall(r"\b[A-Z][a-z]+\b", normalized))
        output = {
            "case_overview": f"deposition-{digest}",
            "sentence_count": sentence_count,
            "named_entity_count": names_detected,
            "confidence": "high",
        }
        return output, f"Generated deterministic deposition summary fingerprint {digest}."

    if skill_id == "contract-clause-risk-flagger":
        risk_terms = ["indemnify", "penalty", "liability", "exclusive", "termination"]
        hits = [term for term in risk_terms if term in lower_text]
        output = {
            "risk_fingerprint": f"contract-{digest}",
            "risk_terms_detected": sorted(hits),
            "risk_score": min(100, len(hits) * 20),
            "review_required": len(hits) > 0,
        }
        return output, f"Flagged {len(hits)} risk indicators for contract digest {digest}."

    if skill_id == "deadline-extractor":
        dates = sorted(set(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", normalized)))
        output = {
            "deadline_fingerprint": f"deadline-{digest}",
            "date_candidates": dates,
            "deadline_count": len(dates),
            "timezone": "local-case-time",
        }
        return output, f"Extracted {len(dates)} potential deadlines for digest {digest}."

    if skill_id == "matter-intake-triage":
        urgency = "normal"
        if any(keyword in lower_text for keyword in ["urgent", "injunction", "arrest", "emergency"]):
            urgency = "critical"
        output = {
            "triage_fingerprint": f"intake-{digest}",
            "urgency": urgency,
            "routing_queue": "attorney-review",
            "stub": True,
        }
        return output, f"Stub triage produced urgency={urgency} for digest {digest}."

    if skill_id == "pacer-search-adapter":
        output = {
            "adapter_fingerprint": f"pacer-{digest}",
            "status": "stub-integration-ready",
            "next_action": "configure-pacer-credentials-locally",
            "stub": True,
        }
        return output, "PACER adapter stub executed in integration-ready mode."

    raise ValueError("unknown skill")
