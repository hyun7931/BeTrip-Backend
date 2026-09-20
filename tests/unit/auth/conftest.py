import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_token_repo():
    return AsyncMock()


@pytest.fixture
def sample_user():
    from app.core.security import hash_password

    return User(
        user_id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("Passw0rd!"),
        nickname="테스터",
        provider="LOCAL",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_refresh_token(sample_user):
    from app.core.security import hash_refresh_token

    raw_token = "sample-raw-refresh-token"
    return raw_token, RefreshToken(
        token_id=uuid.uuid4(),
        user_id=sample_user.user_id,
        token_hash=hash_refresh_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=14),
        revoked_at=None,
        created_at=datetime.now(timezone.utc),
    )
