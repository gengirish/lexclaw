-- Phase 4 audit chain hardening indexes/constraints

CREATE INDEX IF NOT EXISTS idx_audit_events_org_created_at
  ON audit_events (org_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_events_event_hash
  ON audit_events (event_hash);
