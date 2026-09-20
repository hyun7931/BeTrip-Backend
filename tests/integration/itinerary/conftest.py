import asyncio
import sys
import uuid
from datetime import date

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models.itinerary import Itinerary


@pytest.fixture
async def db_session():
    # engine을 fixture 내부에서 생성 -> 현재 테스트의 이벤트 루프에 바인딩됨
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

    async with engine.connect() as connection:
        await connection.begin()

        async_session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        session = async_session_factory()

        yield session

        await session.close()
        await connection.rollback()

    await engine.dispose()  # 테스트 끝나면 엔진도 확실히 정리


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def signed_up_user(client):
    """회원가입 + 로그인 후 (access_token, user_id)를 반환한다."""
    payload = {
        "email": f"{uuid.uuid4()}@example.com",
        "password": "Passw0rd!",
        "nickname": "테스터",
    }
    signup_res = await client.post("/api/v1/auth/signup", json=payload)
    user_id = uuid.UUID(signup_res.json()["user_id"])

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    access_token = login_res.json()["access_token"]
    return access_token, user_id


async def create_itinerary(db_session, user_id, **overrides) -> Itinerary:
    defaults = {
        "itinerary_id": uuid.uuid4(),
        "user_id": user_id,
        "title": "제주도 3박4일",
        "status": "DRAFT",
        "region": "제주도",
        "start_date": date(2026, 8, 10),
        "end_date": date(2026, 8, 13),
        "arrival_time": "LUNCH",
        "departure_time": "MORNING",
        "transportation": "CAR",
        "purpose": "FAMILY",
        "styles": ["NATURE", "FOOD"],
    }
    defaults.update(overrides)
    itinerary = Itinerary(**defaults)
    db_session.add(itinerary)
    await db_session.commit()
    await db_session.refresh(itinerary)
    return itinerary
