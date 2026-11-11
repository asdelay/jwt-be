import secrets
import hashlib
import hmac
import jwt
from datetime import datetime, timedelta, timezone

from app.credentials import settings
from app.schemas import SUser
from app.constants import ACCESS_EXPIRATION

ACCESS_TTL = timedelta(minutes=ACCESS_EXPIRATION)


def generate_otp():
    code = f"{secrets.randbelow(1_000_000):06d}"
    return code

def hash_otp(user_id: int, code: str) -> str:
    return hmac.new(
        settings.otp_secret.encode(),
        f"{user_id}:{code}".encode(),
        hashlib.sha256,
    ).hexdigest()

def create_access_token(user: SUser) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "username": user.username,
        "iat": now,
        "exp": now + ACCESS_TTL,
    }
    return jwt.encode(payload, settings.access_token_secret, algorithm="HS256")