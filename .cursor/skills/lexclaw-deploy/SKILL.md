---
name: lexclaw-deploy
description: Deploy LexClaw services with environment-safe practices. Use when configuring deployment environments, validating runtime variables, shipping Docker artifacts, or troubleshooting deployment issues.
---

# LexClaw Deploy

## Use when
- Preparing dev/staging/prod deployment
- Verifying required environment variables
- Running post-deploy smoke checks

## Required Environment Checks
- API:
  - `JWT_SECRET`
  - `BILLING_WEBHOOK_SECRET`
  - `DATABASE_URL`
- Web:
  - `NEXT_PUBLIC_API_BASE_URL`
- On-prem:
  - `LEXCLAW_CONTROL_PLANE_URL`
  - `LEXCLAW_ORG_ID`
  - `LEXCLAW_BOOTSTRAP_ACCESS_TOKEN`

## Deployment Flow
1. Run full build/test pipeline.
2. Apply DB migrations in order (`001` -> latest).
3. Deploy API service and confirm `/health`.
4. Deploy web service and verify dashboard routes.
5. Validate node registration and heartbeat from on-prem runtime.
6. Validate audit event ingest and redacted telemetry ingest.

## Post-Deploy Smoke Checks
- `GET /health` returns 200
- Auth register/login flow works
- Skills + entitlements endpoints return expected metadata
- Node policy and telemetry endpoints enforce node token boundary

## Guardrails
- Never deploy with placeholder secrets.
- Never include legal content in cloud logs, traces, or DB.
