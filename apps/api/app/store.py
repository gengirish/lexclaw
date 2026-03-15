"""In-memory metadata store for Phase 1-2 scaffold."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Dict
import secrets
from uuid import uuid4

from .security import issue_license_token


@dataclass
class UserRecord:
    id: str
    email: str
    password_hash: str
    full_name: str


@dataclass
class OrgRecord:
    id: str
    name: str
    created_at: datetime


@dataclass
class PlanRecord:
    id: str
    code: str
    name: str
    price_cents: int
    interval: str


@dataclass
class SubscriptionRecord:
    id: str
    org_id: str
    plan_code: str
    status: str
    current_period_end: datetime


@dataclass
class SkillRecord:
    id: str
    code: str
    display_name: str
    description: str
    price_cents: int
    is_active: bool


@dataclass
class EntitlementRecord:
    id: str
    org_id: str
    skill_id: str
    status: str
    granted_at: datetime


@dataclass
class BillingEventRecord:
    id: str
    provider_event_id: str
    event_type: str
    org_id: str
    status: str
    processed_at: datetime


@dataclass
class LicenseRecord:
    id: str
    org_id: str
    node_id: str
    token: str
    issued_at: datetime
    expires_at: datetime
    rotated_from: str | None = None


@dataclass
class NodeRecord:
    id: str
    org_id: str
    display_name: str
    runtime_version: str
    public_key_fingerprint: str
    status: str
    last_heartbeat_at: datetime | None = None


@dataclass
class NodeHeartbeatRecord:
    id: str
    node_id: str
    status: str
    runtime_version: str
    queue_depth: int
    observed_at: datetime


@dataclass
class NodeAuthRecord:
    token: str
    node_id: str
    org_id: str
    issued_at: datetime


@dataclass
class RedactedTelemetryRecord:
    id: str
    node_id: str
    org_id: str
    metrics: dict[str, int]
    redaction_level: str
    received_at: datetime


@dataclass
class AuditEventRecord:
    id: str
    org_id: str
    actor_type: str
    actor_id: str
    action: str
    metadata: dict
    previous_hash: str | None
    event_hash: str
    created_at: datetime


@dataclass
class MemoryStore:
    users: Dict[str, UserRecord] = field(default_factory=dict)
    users_by_email: Dict[str, str] = field(default_factory=dict)
    orgs: Dict[str, OrgRecord] = field(default_factory=dict)
    plans_by_code: Dict[str, PlanRecord] = field(default_factory=dict)
    subscriptions_by_org: Dict[str, SubscriptionRecord] = field(default_factory=dict)
    skills: Dict[str, SkillRecord] = field(default_factory=dict)
    entitlements: Dict[str, EntitlementRecord] = field(default_factory=dict)
    billing_events_by_provider_id: Dict[str, BillingEventRecord] = field(default_factory=dict)
    licenses_by_org: Dict[str, LicenseRecord] = field(default_factory=dict)
    nodes: Dict[str, NodeRecord] = field(default_factory=dict)
    node_tokens: Dict[str, NodeAuthRecord] = field(default_factory=dict)
    node_heartbeats: Dict[str, NodeHeartbeatRecord] = field(default_factory=dict)
    telemetry_events: Dict[str, RedactedTelemetryRecord] = field(default_factory=dict)
    audit_events: Dict[str, AuditEventRecord] = field(default_factory=dict)

    def __post_init__(self):
        self.seed_phase2_catalog()

    def create_user(self, email: str, password_hash: str, full_name: str) -> UserRecord:
        if email.lower() in self.users_by_email:
            raise ValueError("email already exists")

        user = UserRecord(id=str(uuid4()), email=email.lower(), password_hash=password_hash, full_name=full_name)
        self.users[user.id] = user
        self.users_by_email[user.email] = user.id
        return user

    def get_user_by_email(self, email: str) -> UserRecord | None:
        user_id = self.users_by_email.get(email.lower())
        return self.users.get(user_id) if user_id else None

    def get_user(self, user_id: str) -> UserRecord | None:
        return self.users.get(user_id)

    def create_org(self, name: str) -> OrgRecord:
        org = OrgRecord(id=str(uuid4()), name=name, created_at=datetime.now(timezone.utc))
        self.orgs[org.id] = org
        return org

    def get_org(self, org_id: str) -> OrgRecord | None:
        return self.orgs.get(org_id)

    def seed_phase2_catalog(self):
        if self.plans_by_code:
            return

        for code, name, price_cents in [
            ("starter", "Starter", 4900),
            ("professional", "Professional", 14900),
            ("enterprise", "Enterprise", 39900),
        ]:
            self.plans_by_code[code] = PlanRecord(
                id=str(uuid4()),
                code=code,
                name=name,
                price_cents=price_cents,
                interval="month",
            )

        for code, display, desc, price in [
            ("deposition-summarizer", "Deposition Summarizer", "Summarize deposition transcripts.", 2999),
            ("contract-clause-risk-flagger", "Clause Risk Flagger", "Flag risky contract clauses.", 3499),
            ("deadline-extractor", "Deadline Extractor", "Extract legal deadlines from text.", 2499),
            ("matter-intake-triage", "Matter Intake Triage", "Classify intake urgency and routing.", 1999),
            ("pacer-search-adapter", "PACER Search Adapter", "PACER integration-ready adapter stub.", 0),
        ]:
            skill_id = str(uuid4())
            self.skills[skill_id] = SkillRecord(
                id=skill_id,
                code=code,
                display_name=display,
                description=desc,
                price_cents=price,
                is_active=True,
            )

    def create_checkout_session(self, org_id: str, plan_code: str) -> tuple[str, str]:
        if plan_code not in self.plans_by_code:
            raise ValueError("unknown plan")
        checkout_session_id = f"cs_{uuid4().hex[:24]}"
        checkout_url = f"https://checkout.lexclaw.local/session/{checkout_session_id}"
        return checkout_session_id, checkout_url

    def process_billing_webhook(
        self,
        provider_event_id: str,
        event_type: str,
        org_id: str,
        plan_code: str,
        status: str,
    ) -> tuple[BillingEventRecord, bool]:
        existing = self.billing_events_by_provider_id.get(provider_event_id)
        if existing:
            return existing, True

        if plan_code not in self.plans_by_code:
            raise ValueError("unknown plan")

        event = BillingEventRecord(
            id=str(uuid4()),
            provider_event_id=provider_event_id,
            event_type=event_type,
            org_id=org_id,
            status=status,
            processed_at=datetime.now(timezone.utc),
        )
        self.billing_events_by_provider_id[provider_event_id] = event

        self.subscriptions_by_org[org_id] = SubscriptionRecord(
            id=str(uuid4()),
            org_id=org_id,
            plan_code=plan_code,
            status=status,
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
        )
        return event, False

    def get_subscription(self, org_id: str) -> SubscriptionRecord | None:
        return self.subscriptions_by_org.get(org_id)

    def list_skills(self) -> list[SkillRecord]:
        return [skill for skill in self.skills.values() if skill.is_active]

    def get_skill(self, skill_id: str) -> SkillRecord | None:
        return self.skills.get(skill_id)

    def purchase_skill(self, org_id: str, skill_id: str) -> EntitlementRecord:
        skill = self.get_skill(skill_id)
        if not skill or not skill.is_active:
            raise ValueError("skill not available")

        for entitlement in self.entitlements.values():
            if entitlement.org_id == org_id and entitlement.skill_id == skill_id:
                return entitlement

        entitlement = EntitlementRecord(
            id=str(uuid4()),
            org_id=org_id,
            skill_id=skill_id,
            status="active",
            granted_at=datetime.now(timezone.utc),
        )
        self.entitlements[entitlement.id] = entitlement
        return entitlement

    def list_entitlements(self, org_id: str) -> list[EntitlementRecord]:
        return [item for item in self.entitlements.values() if item.org_id == org_id]

    def issue_license(self, org_id: str, node_id: str, ttl_days: int, rotated_from: str | None = None) -> LicenseRecord:
        entitlement_ids = [item.id for item in self.list_entitlements(org_id)]
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(days=ttl_days)
        token = issue_license_token(org_id=org_id, node_id=node_id, entitlement_ids=entitlement_ids, ttl_days=ttl_days)

        license_record = LicenseRecord(
            id=str(uuid4()),
            org_id=org_id,
            node_id=node_id,
            token=token,
            issued_at=issued_at,
            expires_at=expires_at,
            rotated_from=rotated_from,
        )
        self.licenses_by_org[org_id] = license_record
        return license_record

    def rotate_license(self, org_id: str, node_id: str, ttl_days: int) -> LicenseRecord:
        previous = self.licenses_by_org.get(org_id)
        previous_id = previous.id if previous else None
        return self.issue_license(org_id=org_id, node_id=node_id, ttl_days=ttl_days, rotated_from=previous_id)

    def get_license(self, org_id: str) -> LicenseRecord | None:
        return self.licenses_by_org.get(org_id)

    def register_node(
        self,
        org_id: str,
        display_name: str,
        runtime_version: str,
        public_key_fingerprint: str,
    ) -> tuple[NodeRecord, str]:
        node = NodeRecord(
            id=str(uuid4()),
            org_id=org_id,
            display_name=display_name,
            runtime_version=runtime_version,
            public_key_fingerprint=public_key_fingerprint,
            status="registered",
        )
        self.nodes[node.id] = node
        token = secrets.token_urlsafe(32)
        self.node_tokens[token] = NodeAuthRecord(
            token=token,
            node_id=node.id,
            org_id=org_id,
            issued_at=datetime.now(timezone.utc),
        )
        return node, token

    def get_node(self, node_id: str) -> NodeRecord | None:
        return self.nodes.get(node_id)

    def get_node_by_token(self, token: str) -> NodeRecord | None:
        auth = self.node_tokens.get(token)
        if not auth:
            return None
        return self.nodes.get(auth.node_id)

    def heartbeat_node(self, node_id: str, status: str, runtime_version: str, queue_depth: int) -> NodeHeartbeatRecord:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("node not found")
        observed_at = datetime.now(timezone.utc)
        node.status = status
        node.runtime_version = runtime_version
        node.last_heartbeat_at = observed_at
        heartbeat = NodeHeartbeatRecord(
            id=str(uuid4()),
            node_id=node_id,
            status=status,
            runtime_version=runtime_version,
            queue_depth=queue_depth,
            observed_at=observed_at,
        )
        self.node_heartbeats[heartbeat.id] = heartbeat
        return heartbeat

    def get_node_policy(self, node_id: str) -> dict:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("node not found")
        return {
            "node_id": node.id,
            "policy_version": "phase3-v1",
            "require_human_approval": True,
            "max_case_documents": 10000,
            "telemetry_mode": "redacted-only",
        }

    def get_node_entitlement_codes(self, node_id: str) -> tuple[str, list[str]]:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("node not found")
        codes = []
        for ent in self.list_entitlements(node.org_id):
            skill = self.get_skill(ent.skill_id)
            if skill and ent.status == "active":
                codes.append(skill.code)
        return node.org_id, sorted(codes)

    def ingest_redacted_telemetry(self, node_id: str, metrics: dict[str, int], redaction_level: str) -> RedactedTelemetryRecord:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("node not found")
        event = RedactedTelemetryRecord(
            id=str(uuid4()),
            node_id=node_id,
            org_id=node.org_id,
            metrics=metrics,
            redaction_level=redaction_level,
            received_at=datetime.now(timezone.utc),
        )
        self.telemetry_events[event.id] = event
        return event

    def _last_event_hash(self, org_id: str) -> str | None:
        events = [event for event in self.audit_events.values() if event.org_id == org_id]
        if not events:
            return None
        events.sort(key=lambda item: item.created_at)
        return events[-1].event_hash

    def create_node_audit_event(
        self,
        node_id: str,
        action: str,
        metadata: dict,
        event_hash: str,
        previous_hash: str | None = None,
    ) -> AuditEventRecord:
        node = self.get_node(node_id)
        if not node:
            raise ValueError("node not found")
        # Guardrail: metadata-only audit payload
        banned_keys = {"content", "body", "document_text", "chat_text", "raw_email"}
        lowered_keys = {str(key).lower() for key in metadata.keys()}
        if lowered_keys.intersection(banned_keys):
            raise ValueError("metadata contains prohibited content-like keys")

        expected_previous = self._last_event_hash(node.org_id)
        if expected_previous and previous_hash != expected_previous:
            raise ValueError("invalid previous hash")
        if expected_previous is None and previous_hash is not None:
            raise ValueError("unexpected previous hash for first event")

        serialized = json.dumps(metadata, sort_keys=True)
        expected_hash = hashlib.sha256(f"{previous_hash or ''}:{serialized}".encode("utf-8")).hexdigest()
        if event_hash != expected_hash:
            raise ValueError("invalid event hash")

        event = AuditEventRecord(
            id=str(uuid4()),
            org_id=node.org_id,
            actor_type="node",
            actor_id=node.id,
            action=action,
            metadata=metadata,
            previous_hash=previous_hash,
            event_hash=event_hash,
            created_at=datetime.now(timezone.utc),
        )
        self.audit_events[event.id] = event
        return event

    def list_audit_events(self, org_id: str) -> list[AuditEventRecord]:
        events = [event for event in self.audit_events.values() if event.org_id == org_id]
        events.sort(key=lambda item: item.created_at, reverse=True)
        return events


store = MemoryStore()
