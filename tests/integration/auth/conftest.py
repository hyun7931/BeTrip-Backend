import asyncio
import sys

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db
from app.main import app


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
