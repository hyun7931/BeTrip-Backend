import asyncio
import sys

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.models  # noqa: F401 — Base.metadata에 전체 모델을 등록시키기 위한 import
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """
    통합테스트 세션 시작 시 한 번, 없는 테이블만 생성한다(create_all은 기본적으로
    checkfirst=True라 이미 있는 테이블은 건드리지 않음).
    Alembic이 아직 초기화되지 않아 CI의 새 DB에는 스키마가 전혀 없기 때문에
    필요한 임시 조치이며, 로컬처럼 이미 테이블이 있는 DB에는 영향이 없다.
    unit 테스트는 DB를 쓰지 않으므로 이 conftest(통합테스트 전용) 아래에만 둔다.
    """

    async def _create():
        engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create())


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
