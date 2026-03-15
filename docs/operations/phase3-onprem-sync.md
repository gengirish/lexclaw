# Phase 3 On-Prem Sync Operations

## Flow
- Register node via `POST /v1/nodes/register` using bootstrap access token.
- Persist issued node token in local secure runtime store.
- Send heartbeats on a fixed interval via `POST /v1/nodes/heartbeat`.
- Pull policy and entitlements before skill execution.
- Publish only redacted telemetry metrics via `POST /v1/nodes/telemetry`.

## Failure handling
- On heartbeat failure, retry with exponential backoff.
- On token mismatch, re-register node and rotate local token.
- On policy pull failure, keep previous cached policy and run in safe mode.
