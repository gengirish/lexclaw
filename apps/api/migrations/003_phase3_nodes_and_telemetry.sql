-- LexClaw Phase 3 node connector + telemetry metadata schema additions

CREATE TABLE IF NOT EXISTS node_auth_tokens (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL REFERENCES organizations(id),
  node_id UUID NOT NULL REFERENCES onprem_nodes(id),
  token_hash TEXT NOT NULL,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  revoked_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS redacted_telemetry_events (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL REFERENCES organizations(id),
  node_id UUID NOT NULL REFERENCES onprem_nodes(id),
  metric_bundle JSONB NOT NULL DEFAULT '{}'::jsonb,
  redaction_level TEXT NOT NULL CHECK (redaction_level IN ('strict')),
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
