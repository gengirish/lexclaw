# LexClaw Monorepo

Phase 1 foundation for LexClaw hybrid micro-SaaS.

## Workspace
- `apps/web`: Next.js control plane dashboard shell
- `apps/api`: FastAPI control plane API (`/v1`)
- `apps/onprem-core`: On-prem connector scaffold
- `packages/*`: shared contracts and policies
- `infra/*`: docker, k8s, terraform scaffolds
- `docs/*`: architecture, security, operations, compliance

## Quick Start

### 1) Prerequisites
- Node.js 20+
- Python 3.11+
- `uv` (Python package/dependency manager)

### 2) Install
```bash
npm install
uv sync --project apps/api --frozen --group dev
```

### 3) Run API
```bash
uv run --project apps/api uvicorn app.main:app --reload --app-dir apps/api
```

### 4) Run Web
```bash
npm run dev:web
```

### 5) Run tests
```bash
npm run test:web
uv run --project apps/api pytest apps/api/tests -q
```

## Phase 2 API Coverage

- Billing:
  - `POST /v1/billing/checkout-session`
  - `POST /v1/billing/webhook` (signature + idempotent dedupe)
  - `GET /v1/billing/subscription`
- Skills Marketplace:
  - `GET /v1/skills`
  - `GET /v1/skills/{skill_id}`
  - `POST /v1/orgs/{org_id}/skills/{skill_id}/purchase`
  - `GET /v1/orgs/{org_id}/entitlements`
- Licensing:
  - `POST /v1/licenses/issue`
  - `POST /v1/licenses/rotate`
  - `GET /v1/licenses/validate`

## Phase 3 API Coverage

- On-prem Node:
  - `POST /v1/nodes/register`
  - `POST /v1/nodes/heartbeat`
  - `GET /v1/nodes/{node_id}/policy`
  - `GET /v1/nodes/{node_id}/entitlements`
  - `POST /v1/nodes/telemetry` (redacted telemetry only)

## Phase 4 Legal Skills MVP

- Local on-prem skill runtime with signed package verification and version pinning
- 3 production-ready skills:
  - `deposition-summarizer`
  - `contract-clause-risk-flagger`
  - `deadline-extractor`
- 2 integration-ready stubs:
  - `matter-intake-triage`
  - `pacer-search-adapter`
- Execution controls:
  - entitlement check before execution
  - policy/human approval gate enforcement
  - deterministic JSON output envelope + human summary
  - hash-linked audit metadata chain
- Cloud metadata ingest:
  - `POST /v1/nodes/audit-events`
  - `GET /v1/orgs/{org_id}/audit-events`

## On-Prem Local Run (Phase 3)

```bash
python apps/onprem-core/main.py
```
