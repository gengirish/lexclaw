from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    full_name: str = Field(min_length=2, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class OrganizationOut(BaseModel):
    id: str
    name: str
    created_at: datetime


class MeOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str


class BillingCheckoutRequest(BaseModel):
    org_id: str
    plan_code: str
    seats: int = Field(ge=1, le=200)


class BillingCheckoutOut(BaseModel):
    checkout_session_id: str
    checkout_url: str
    status: str


class BillingWebhookRequest(BaseModel):
    provider_event_id: str
    event_type: str
    org_id: str
    plan_code: str
    status: str


class SubscriptionOut(BaseModel):
    id: str
    org_id: str
    plan_code: str
    status: str
    current_period_end: datetime


class SkillOut(BaseModel):
    id: str
    code: str
    display_name: str
    description: str
    price_cents: int
    is_active: bool


class EntitlementOut(BaseModel):
    id: str
    org_id: str
    skill_id: str
    skill_code: str
    status: str
    granted_at: datetime


class LicenseIssueRequest(BaseModel):
    org_id: str
    node_id: str = Field(min_length=3, max_length=120)
    ttl_days: int = Field(default=30, ge=1, le=365)


class LicenseRotateRequest(BaseModel):
    org_id: str
    node_id: str = Field(min_length=3, max_length=120)
    ttl_days: int = Field(default=30, ge=1, le=365)


class LicenseOut(BaseModel):
    license_id: str
    token: str
    org_id: str
    node_id: str
    issued_at: datetime
    expires_at: datetime


class LicenseValidateOut(BaseModel):
    valid: bool
    org_id: str | None = None
    node_id: str | None = None
    expires_at: datetime | None = None
    reason: str | None = None


class NodeRegisterRequest(BaseModel):
    org_id: str
    display_name: str = Field(min_length=2, max_length=120)
    runtime_version: str = Field(min_length=1, max_length=50)
    public_key_fingerprint: str = Field(min_length=8, max_length=128)


class NodeRegisterOut(BaseModel):
    node_id: str
    org_id: str
    status: str
    issued_node_token: str


class NodeHeartbeatRequest(BaseModel):
    status: str = Field(pattern="^(healthy|degraded|offline)$")
    runtime_version: str = Field(min_length=1, max_length=50)
    queue_depth: int = Field(ge=0, le=100000)


class NodeHeartbeatOut(BaseModel):
    node_id: str
    accepted: bool
    observed_at: datetime


class NodePolicyOut(BaseModel):
    node_id: str
    policy_version: str
    require_human_approval: bool
    max_case_documents: int
    telemetry_mode: str


class NodeEntitlementsOut(BaseModel):
    node_id: str
    org_id: str
    entitlement_codes: list[str]
    synced_at: datetime


class RedactedTelemetryRequest(BaseModel):
    node_id: str
    metrics: dict[str, int]
    redaction_level: str = Field(pattern="^(strict)$")


class NodeAuditEventRequest(BaseModel):
    node_id: str
    action: str = Field(min_length=3, max_length=120)
    metadata: dict
    previous_hash: str | None = None
    event_hash: str


class NodeAuditEventOut(BaseModel):
    event_id: str
    org_id: str
    node_id: str
    action: str
    event_hash: str
    created_at: datetime


class AuditEventOut(BaseModel):
    event_id: str
    org_id: str
    actor_type: str
    actor_id: str
    action: str
    metadata: dict
    previous_hash: str | None = None
    event_hash: str
    created_at: datetime
