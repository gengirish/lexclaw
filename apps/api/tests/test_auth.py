from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_login_and_me_flow():
    register = client.post(
        "/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "supersecure1",
            "full_name": "Owner One",
        },
    )
    assert register.status_code == 200
    tokens = register.json()

    me = client.get("/v1/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "owner@example.com"

    login = client.post(
        "/v1/auth/login",
        json={"email": "owner@example.com", "password": "supersecure1"},
    )
    assert login.status_code == 200


def test_create_and_fetch_org():
    register = client.post(
        "/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "supersecure2",
            "full_name": "Admin One",
        },
    )
    token = register.json()["access_token"]

    created = client.post(
        "/v1/orgs",
        json={"name": "LexClaw Legal"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert created.status_code == 200
    org_id = created.json()["id"]

    fetched = client.get(
        f"/v1/orgs/{org_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "LexClaw Legal"
