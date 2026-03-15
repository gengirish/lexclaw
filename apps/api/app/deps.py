from fastapi import Depends, Header, HTTPException

from .security import decode_token
from .store import store


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc

    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="invalid token kind")

    user = store.get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="user not found")

    return user


def require_org_access(org_id: str, _current_user=Depends(get_current_user)):
    org = store.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="organization not found")
    return org
