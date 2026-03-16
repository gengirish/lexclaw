# Phase 4 Legal Skills Operations

## Local execution boundaries
- Skills execute only within on-prem runtime.
- Inputs are processed locally and never sent to cloud.
- Cloud receives audit metadata digests only.

## Skill package lifecycle
- Verify signed manifests before install.
- Pin semantic versions for stable execution.
- Support rollback to prior installed version.

## Runtime guardrails
- Enforce entitlement before every execution.
- Enforce approval gates when policy requires human review.
- Emit deterministic output envelope and metadata-only audit record.
