from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from .config import settings
from .deps import get_current_user, require_org_access
from .schemas import (
    AuditEventOut,
    BillingCheckoutOut,
    BillingCheckoutRequest,
    BillingWebhookRequest,
    EntitlementOut,
    LicenseIssueRequest,
    LicenseOut,
    LicenseRotateRequest,
    LicenseValidateOut,
    NodeEntitlementsOut,
    NodeAuditEventOut,
    NodeAuditEventRequest,
    NodeHeartbeatOut,
    NodeHeartbeatRequest,
    NodePolicyOut,
    NodeRegisterOut,
    NodeRegisterRequest,
    RedactedTelemetryRequest,
    LoginRequest,
    MeOut,
    OrganizationCreate,
    OrganizationOut,
    RefreshRequest,
    RegisterRequest,
    SkillOut,
    SubscriptionOut,
    TokenPair,
)
from .security import (
    decode_license_token,
    decode_token,
    hash_password,
    issue_access_token,
    issue_refresh_token,
    verify_password,
)
from .store import store

app = FastAPI(title="LexClaw Cloud API", version="0.1.0")


def require_node(node_id: str, x_node_token: str = Header(default="")):
    node = store.get_node_by_token(x_node_token)
    if not node:
        raise HTTPException(status_code=401, detail="invalid node token")
    if node.id != node_id:
        raise HTTPException(status_code=403, detail="node token does not match node")
    return node


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/auth/register", response_model=TokenPair)
def register(payload: RegisterRequest):
    try:
        user = store.create_user(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="email already exists") from exc

    return TokenPair(
        access_token=issue_access_token(user.id),
        refresh_token=issue_refresh_token(user.id),
    )


@app.post("/v1/auth/login", response_model=TokenPair)
def login(payload: LoginRequest):
    user = store.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    return TokenPair(
        access_token=issue_access_token(user.id),
        refresh_token=issue_refresh_token(user.id),
    )


@app.post("/v1/auth/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid refresh token") from exc

    if decoded.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="invalid refresh token kind")

    user = store.get_user(decoded["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="user not found")

    return TokenPair(
        access_token=issue_access_token(user.id),
        refresh_token=issue_refresh_token(user.id),
    )


@app.get("/v1/me", response_model=MeOut)
def me(current_user=Depends(get_current_user)):
    return MeOut(id=current_user.id, email=current_user.email, full_name=current_user.full_name)


@app.post("/v1/orgs", response_model=OrganizationOut)
def create_org(payload: OrganizationCreate, _current_user=Depends(get_current_user)):
    org = store.create_org(payload.name)
    return OrganizationOut(id=org.id, name=org.name, created_at=org.created_at)


@app.get("/v1/orgs/{org_id}", response_model=OrganizationOut)
def get_org(org=Depends(require_org_access)):
    return OrganizationOut(id=org.id, name=org.name, created_at=org.created_at)


@app.post("/v1/billing/checkout-session", response_model=BillingCheckoutOut)
def billing_checkout(payload: BillingCheckoutRequest, _current_user=Depends(get_current_user)):
    if not store.get_org(payload.org_id):
        raise HTTPException(status_code=404, detail="organization not found")
    try:
        session_id, checkout_url = store.create_checkout_session(payload.org_id, payload.plan_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BillingCheckoutOut(checkout_session_id=session_id, checkout_url=checkout_url, status="created")


@app.post("/v1/billing/webhook")
def billing_webhook(payload: BillingWebhookRequest, x_lexclaw_signature: str = Header(default="")):
    if x_lexclaw_signature != settings.billing_webhook_secret:
        raise HTTPException(status_code=401, detail="invalid webhook signature")
    try:
        event, deduped = store.process_billing_webhook(
            provider_event_id=payload.provider_event_id,
            event_type=payload.event_type,
            org_id=payload.org_id,
            plan_code=payload.plan_code,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "event_id": event.id, "deduped": deduped}


@app.get("/v1/billing/subscription", response_model=SubscriptionOut)
def billing_subscription(org_id: str = Query(...), _current_user=Depends(get_current_user)):
    if not store.get_org(org_id):
        raise HTTPException(status_code=404, detail="organization not found")
    sub = store.get_subscription(org_id)
    if not sub:
        raise HTTPException(status_code=404, detail="subscription not found")
    return SubscriptionOut(
        id=sub.id,
        org_id=sub.org_id,
        plan_code=sub.plan_code,
        status=sub.status,
        current_period_end=sub.current_period_end,
    )


@app.get("/v1/skills", response_model=list[SkillOut])
def list_skills(_current_user=Depends(get_current_user)):
    return [
        SkillOut(
            id=item.id,
            code=item.code,
            display_name=item.display_name,
            description=item.description,
            price_cents=item.price_cents,
            is_active=item.is_active,
        )
        for item in store.list_skills()
    ]


@app.get("/v1/skills/{skill_id}", response_model=SkillOut)
def get_skill(skill_id: str, _current_user=Depends(get_current_user)):
    skill = store.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")
    return SkillOut(
        id=skill.id,
        code=skill.code,
        display_name=skill.display_name,
        description=skill.description,
        price_cents=skill.price_cents,
        is_active=skill.is_active,
    )


@app.post("/v1/orgs/{org_id}/skills/{skill_id}/purchase", response_model=EntitlementOut)
def purchase_skill(org_id: str, skill_id: str, _current_user=Depends(get_current_user), _org=Depends(require_org_access)):
    try:
        ent = store.purchase_skill(org_id=org_id, skill_id=skill_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    skill = store.get_skill(skill_id)
    return EntitlementOut(
        id=ent.id,
        org_id=ent.org_id,
        skill_id=ent.skill_id,
        skill_code=skill.code if skill else "unknown",
        status=ent.status,
        granted_at=ent.granted_at,
    )


@app.get("/v1/orgs/{org_id}/entitlements", response_model=list[EntitlementOut])
def get_entitlements(org_id: str, _current_user=Depends(get_current_user), _org=Depends(require_org_access)):
    results = []
    for ent in store.list_entitlements(org_id):
        skill = store.get_skill(ent.skill_id)
        results.append(
            EntitlementOut(
                id=ent.id,
                org_id=ent.org_id,
                skill_id=ent.skill_id,
                skill_code=skill.code if skill else "unknown",
                status=ent.status,
                granted_at=ent.granted_at,
            )
        )
    return results


@app.post("/v1/licenses/issue", response_model=LicenseOut)
def issue_license(payload: LicenseIssueRequest, _current_user=Depends(get_current_user)):
    if not store.get_org(payload.org_id):
        raise HTTPException(status_code=404, detail="organization not found")
    record = store.issue_license(org_id=payload.org_id, node_id=payload.node_id, ttl_days=payload.ttl_days)
    return LicenseOut(
        license_id=record.id,
        token=record.token,
        org_id=record.org_id,
        node_id=record.node_id,
        issued_at=record.issued_at,
        expires_at=record.expires_at,
    )


@app.post("/v1/licenses/rotate", response_model=LicenseOut)
def rotate_license(payload: LicenseRotateRequest, _current_user=Depends(get_current_user)):
    if not store.get_org(payload.org_id):
        raise HTTPException(status_code=404, detail="organization not found")
    record = store.rotate_license(org_id=payload.org_id, node_id=payload.node_id, ttl_days=payload.ttl_days)
    return LicenseOut(
        license_id=record.id,
        token=record.token,
        org_id=record.org_id,
        node_id=record.node_id,
        issued_at=record.issued_at,
        expires_at=record.expires_at,
    )


@app.get("/v1/licenses/validate", response_model=LicenseValidateOut)
def validate_license(token: str = Query(...)):
    try:
        payload = decode_license_token(token)
    except Exception:
        return LicenseValidateOut(valid=False, reason="invalid_or_expired_token")

    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    return LicenseValidateOut(
        valid=True,
        org_id=payload.get("org_id"),
        node_id=payload.get("node_id"),
        expires_at=expires_at,
    )


@app.post("/v1/nodes/register", response_model=NodeRegisterOut)
def register_node(payload: NodeRegisterRequest, _current_user=Depends(get_current_user)):
    if not store.get_org(payload.org_id):
        raise HTTPException(status_code=404, detail="organization not found")
    node, issued_token = store.register_node(
        org_id=payload.org_id,
        display_name=payload.display_name,
        runtime_version=payload.runtime_version,
        public_key_fingerprint=payload.public_key_fingerprint,
    )
    return NodeRegisterOut(node_id=node.id, org_id=node.org_id, status=node.status, issued_node_token=issued_token)


@app.post("/v1/nodes/heartbeat", response_model=NodeHeartbeatOut)
def heartbeat_node(node_id: str = Query(...), payload: NodeHeartbeatRequest = ..., _node=Depends(require_node)):
    try:
        hb = store.heartbeat_node(
            node_id=node_id,
            status=payload.status,
            runtime_version=payload.runtime_version,
            queue_depth=payload.queue_depth,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return NodeHeartbeatOut(node_id=node_id, accepted=True, observed_at=hb.observed_at)


@app.get("/v1/nodes/{node_id}/policy", response_model=NodePolicyOut)
def node_policy(node_id: str, _node=Depends(require_node)):
    try:
        policy = store.get_node_policy(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return NodePolicyOut(**policy)


@app.get("/v1/nodes/{node_id}/entitlements", response_model=NodeEntitlementsOut)
def node_entitlements(node_id: str, _node=Depends(require_node)):
    try:
        org_id, entitlement_codes = store.get_node_entitlement_codes(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return NodeEntitlementsOut(
        node_id=node_id,
        org_id=org_id,
        entitlement_codes=entitlement_codes,
        synced_at=datetime.now(timezone.utc),
    )


@app.post("/v1/nodes/telemetry")
def ingest_telemetry(payload: RedactedTelemetryRequest, x_node_token: str = Header(default="")):
    node = store.get_node_by_token(x_node_token)
    if not node:
        raise HTTPException(status_code=401, detail="invalid node token")
    if node.id != payload.node_id:
        raise HTTPException(status_code=403, detail="node token does not match node")
    try:
        event = store.ingest_redacted_telemetry(
            node_id=payload.node_id,
            metrics=payload.metrics,
            redaction_level=payload.redaction_level,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "event_id": event.id, "received_at": event.received_at}


@app.post("/v1/nodes/audit-events", response_model=NodeAuditEventOut)
def ingest_node_audit_event(payload: NodeAuditEventRequest, x_node_token: str = Header(default="")):
    node = store.get_node_by_token(x_node_token)
    if not node:
        raise HTTPException(status_code=401, detail="invalid node token")
    if node.id != payload.node_id:
        raise HTTPException(status_code=403, detail="node token does not match node")
    try:
        event = store.create_node_audit_event(
            node_id=payload.node_id,
            action=payload.action,
            metadata=payload.metadata,
            previous_hash=payload.previous_hash,
            event_hash=payload.event_hash,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return NodeAuditEventOut(
        event_id=event.id,
        org_id=event.org_id,
        node_id=payload.node_id,
        action=event.action,
        event_hash=event.event_hash,
        created_at=event.created_at,
    )


@app.get("/v1/orgs/{org_id}/audit-events", response_model=list[AuditEventOut])
def get_org_audit_events(org_id: str, _current_user=Depends(get_current_user), _org=Depends(require_org_access)):
    events = store.list_audit_events(org_id)
    return [
        AuditEventOut(
            event_id=item.id,
            org_id=item.org_id,
            actor_type=item.actor_type,
            actor_id=item.actor_id,
            action=item.action,
            metadata=item.metadata,
            previous_hash=item.previous_hash,
            event_hash=item.event_hash,
            created_at=item.created_at,
        )
        for item in events
    ]
