# Threat Model (Initial)

## Trust boundaries
- Internet clients to cloud API
- Cloud API to metadata database
- On-prem node to cloud API (future mTLS)

## Initial attack vectors
- Token theft/replay
- Tenant breakout via missing org checks
- Webhook spoofing (future phases)

## Mitigations in this phase
- JWT auth scaffold
- Endpoint-level auth guards
- Metadata-only schema discipline

## Incident response baseline
1. Revoke compromised credentials
2. Rotate JWT signing keys
3. Audit metadata event review
4. Containment + postmortem
