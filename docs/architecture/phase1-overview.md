# LexClaw Phase 1 Architecture

## Trust boundary
- Cloud control plane stores metadata only.
- On-prem runtime will process legal content locally in later phases.

## Components
- Next.js web app for control plane UI shell
- FastAPI `/v1` control plane API
- SQL migration for tenant-aware metadata schema
- On-prem core bootstrap module
