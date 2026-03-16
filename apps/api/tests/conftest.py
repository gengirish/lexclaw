import pytest

from app.store import store


@pytest.fixture(autouse=True)
def reset_memory_store():
    store.users.clear()
    store.users_by_email.clear()
    store.orgs.clear()
    store.subscriptions_by_org.clear()
    store.entitlements.clear()
    store.billing_events_by_provider_id.clear()
    store.licenses_by_org.clear()
    store.nodes.clear()
    store.node_tokens.clear()
    store.node_heartbeats.clear()
    store.telemetry_events.clear()
    store.audit_events.clear()
    yield
