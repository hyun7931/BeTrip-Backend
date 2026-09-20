import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import PyJWTError

from app.core.config import settings

# ============================================================
# 비밀번호 해싱 (동기 함수)
# ============================================================


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ============================================================
# Access Token (JWT)
# ============================================================


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
        "jti": str(uuid.uuid4()),  # ← 매번 고유한 토큰 ID
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """
    유효하지 않거나 만료된 토큰이면 PyJWTError(혹은 하위 클래스)를 raise.
    호출부에서 잡아서 401로 변환할 것.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if payload.get("type") != "access":
        raise PyJWTError("Invalid token type")
    return payload


# ============================================================
# Refresh Token (opaque random token)
# ============================================================


def generate_refresh_token() -> str:
    # URL-safe 랜덤 문자열. 클라이언트에는 이 값 그대로 전달.
    return secrets.token_urlsafe(64)


def hash_refresh_token(raw_token: str) -> str:
    # DB에는 해시만 저장 (raw 값은 DB 유출 시에도 복구 불가해야 함)
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
