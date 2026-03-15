---
name: lexclaw-spec-workflow
description: Plan LexClaw features using spec-driven workflow before implementation. Use when defining phase scope, writing acceptance criteria, and breaking work into testable tasks.
---

# LexClaw Spec Workflow

## Use when
- Starting a new phase or subsystem
- Requirements are broad or ambiguous
- You need clear acceptance criteria before coding

## Workflow
1. Define feature scope and privacy boundary impact.
2. Write acceptance criteria (functional + security + compliance).
3. Break into implementation tasks by service:
   - `apps/api`
   - `apps/web`
   - `apps/onprem-core`
   - `packages/*`
4. Define test plan:
   - unit
   - integration
   - boundary/security checks
5. Implement iteratively with runnable checkpoints.

## Spec Quality Rules
- Include explicit “no legal content in cloud” constraints.
- Include tenant isolation checks for all cloud endpoints.
- Include webhook signature/idempotency requirements for external integrations.
- Include rollback and migration safety notes for schema changes.
