# Day 0 to Day 7 Deployment Playbook

## Day 0
- Provision Neon Postgres, Stripe, and cloud runtime placeholders.
- Set environment variables from `.env.example` files.

## Day 1
- Deploy API and web baseline containers.
- Run `apps/api/migrations/001_phase1_foundation.sql`.

## Day 2-3
- Verify auth/org flows and tenant metadata integrity.
- Execute API tests and web smoke tests.

## Day 4-5
- Integrate observability stubs and alert routes.
- Validate no content fields exist in cloud schema.

## Day 6
- Security review for tenant isolation controls.

## Day 7
- Final readiness review for Phase 2 (billing + marketplace).
