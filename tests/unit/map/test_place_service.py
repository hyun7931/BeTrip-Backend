import pytest
from fastapi import HTTPException

from app.schemas.place import PlaceDetailResponse
from app.services.place_service import PlaceService


async def test_get_place_detail_returns_cached_place(mock_place_repo, sample_place):
    mock_place_repo.get_by_id.return_value = sample_place

    service = PlaceService(mock_place_repo)
    result = await service.get_place_detail("123")

    assert isinstance(result, PlaceDetailResponse)
    assert result.place_id == "123"
    assert result.name == "흑돼지식당"
    assert result.place_url == "https://place.map.kakao.com/123"
    mock_place_repo.get_by_id.assert_awaited_once_with("123")


async def test_get_place_detail_raises_404_when_not_cached(mock_place_repo):
    mock_place_repo.get_by_id.return_value = None

    service = PlaceService(mock_place_repo)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_place_detail("unknown")

    assert exc_info.value.status_code == 404
