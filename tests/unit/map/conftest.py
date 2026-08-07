from unittest.mock import AsyncMock

import pytest

from app.models.place import Place
from app.schemas.place import KakaoPlaceRaw


@pytest.fixture
def mock_place_repo():
    return AsyncMock()


@pytest.fixture
def mock_kakao_client():
    return AsyncMock()


@pytest.fixture
def mock_kakao_mobility_client():
    return AsyncMock()


@pytest.fixture
def sample_place():
    return Place(
        place_id="123",
        name="흑돼지식당",
        category="RESTAURANT",
        address="제주시 어딘가",
        lat=33.4,
        lng=126.5,
        place_url="https://place.map.kakao.com/123",
        thumbnail_url="https://example.com/thumb.jpg",
    )


@pytest.fixture
def sample_kakao_place_raw():
    return KakaoPlaceRaw(
        place_id="123",
        name="흑돼지식당",
        category="RESTAURANT",
        address="제주시 어딘가",
        lat=33.4,
        lng=126.5,
        place_url="https://place.map.kakao.com/123",
    )
