---
name: lexclaw-testing-e2e
description: Run and expand LexClaw testing, including API integration and browser E2E smoke coverage. Use when adding tests, debugging failures, or validating critical release paths.
---

# LexClaw Testing and E2E

## Use when
- Adding regression coverage
- Running release validation
- Investigating failures in auth, billing, node sync, or audit flows

## Test Layers
- API integration: `uv run --project apps/api pytest apps/api/tests -q`
- On-prem runtime unit tests: `python -m pytest apps/onprem-core/tests -q`
- Web smoke: `npm run test --workspace @lexclaw/web`
- Web lint/type safety: `npm run lint --workspace @lexclaw/web`

## Critical Flow Checklist
- Auth register/login/refresh
- Org create/read
- Billing webhook signature + idempotency
- Skill purchase + entitlement retrieval
- License issue/validate/rotate
- Node register/heartbeat/policy/entitlements
- Redacted telemetry and hash-linked audit event ingest

## Optional Browser E2E (Playwright)
```bash
npm install -D @playwright/test
npx playwright install chromium
npx playwright test
```

Use role-based selectors first (`getByRole`, `getByLabel`) and avoid brittle CSS selectors.

## Guardrails
- Tests must never assert on raw legal content leaving on-prem boundaries.
- Prefer deterministic fixtures and explicit idempotency keys/events.
