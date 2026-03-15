---
name: lexclaw-build-pipeline
description: Build and package LexClaw apps in this monorepo. Use when the user asks to build, typecheck, package containers, or validate release readiness across API, web, and on-prem services.
---

# LexClaw Build Pipeline

## Use when
- Building all services before release
- Verifying production bundles
- Validating Docker image build health

## Build Steps
1. API dependencies: `uv sync --project apps/api --frozen --group dev`
2. API tests: `uv run --project apps/api pytest apps/api/tests -q`
3. Web install: `npm install`
4. Web lint: `npm run lint --workspace @lexclaw/web`
5. Web tests: `npm run test --workspace @lexclaw/web`
6. Web build: `npm run build --workspace @lexclaw/web`
7. On-prem tests: `python -m pytest apps/onprem-core/tests -q`

## Container Build Checks
- API image: `docker build -f infra/docker/Dockerfile.api .`
- Web image: `docker build -f infra/docker/Dockerfile.web .`
- On-prem image: `docker build -f infra/docker/Dockerfile.onprem .`

## Guardrails
- Do not bypass failing tests for release builds.
- Do not log secrets or raw legal content in build/test output.
- Keep API contract changes reflected in `apps/api/openapi.json`.
