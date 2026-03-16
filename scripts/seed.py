"""Phase 1 seed utility for local/dev metadata only."""

from datetime import datetime


def run() -> None:
    print("Seeding metadata-only defaults for LexClaw...")
    print(f"Seed completed at {datetime.utcnow().isoformat()}Z")


if __name__ == "__main__":
    run()
