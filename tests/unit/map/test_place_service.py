from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.schemas.place import PlaceDetailResponse
from app.services.place_service import PlaceService


async def test_get_place_detail_returns_cached_place(
    mock_place_repo, mock_kakao_client, sample_place
):
    mock_place_repo.get_by_id.return_value = sample_place

    service = PlaceService(mock_place_repo, mock_kakao_client)
    result = await service.get_place_detail("123")

    assert isinstance(result, PlaceDetailResponse)
    assert result.place_id == "123"
    assert result.name == "흑돼지식당"
    assert result.place_url == "https://place.map.kakao.com/123"
    mock_place_repo.get_by_id.assert_awaited_once_with("123")


async def test_get_place_detail_raises_404_when_not_cached(
    mock_place_repo, mock_kakao_client
):
    mock_place_repo.get_by_id.return_value = None

    service = PlaceService(mock_place_repo, mock_kakao_client)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_place_detail("unknown")

    assert exc_info.value.status_code == 404


async def test_search_places_with_keyword_upserts_and_returns_result(
    mock_place_repo, mock_kakao_client, sample_kakao_place_raw, monkeypatch
):
    mock_kakao_client.search_by_keyword.return_value = [sample_kakao_place_raw]
    monkeypatch.setattr(
        "app.services.place_service.fetch_og_image",
        AsyncMock(return_value="https://example.com/thumb.jpg"),
    )

    service = PlaceService(mock_place_repo, mock_kakao_client)
    result = await service.search_places(
        q="흑돼지", x=None, y=None, radius=None, rect=None, category=None
    )

    assert len(result.places) == 1
    assert result.places[0].place_id == "123"
    assert result.places[0].thumbnail_url == "https://example.com/thumb.jpg"
    mock_kakao_client.search_by_keyword.assert_awaited_once()
    mock_place_repo.upsert_many.assert_awaited_once()


async def test_search_places_category_only_requires_location(
    mock_place_repo, mock_kakao_client
):
    service = PlaceService(mock_place_repo, mock_kakao_client)

    with pytest.raises(HTTPException) as exc_info:
        await service.search_places(
            q=None, x=None, y=None, radius=None, rect=None, category="RESTAURANT"
        )

    assert exc_info.value.status_code == 422
    mock_kakao_client.search_by_category.assert_not_awaited()


async def test_search_places_without_q_or_category_raises_422(
    mock_place_repo, mock_kakao_client
):
    service = PlaceService(mock_place_repo, mock_kakao_client)

    with pytest.raises(HTTPException) as exc_info:
        await service.search_places(
            q=None, x=None, y=None, radius=None, rect=None, category=None
        )

    assert exc_info.value.status_code == 422
