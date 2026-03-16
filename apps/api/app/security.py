from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def issue_token(subject: str, token_kind: str, ttl: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "typ": token_kind,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def issue_access_token(subject: str) -> str:
    return issue_token(subject, "access", timedelta(minutes=settings.jwt_access_ttl_minutes))


def issue_refresh_token(subject: str) -> str:
    return issue_token(subject, "refresh", timedelta(days=settings.jwt_refresh_ttl_days))


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


def issue_license_token(org_id: str, node_id: str, entitlement_ids: list[str], ttl_days: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    ttl = timedelta(days=ttl_days or settings.license_token_ttl_days)
    payload = {
        "iss": settings.jwt_issuer,
        "aud": "lexclaw-license",
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "typ": "license",
        "org_id": org_id,
        "node_id": node_id,
        "entitlements": entitlement_ids,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_license_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        audience="lexclaw-license",
        issuer=settings.jwt_issuer,
    )
