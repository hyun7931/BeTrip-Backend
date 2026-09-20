import pytest
from fastapi import HTTPException

from app.schemas.transit import TransitResponse
from app.services.transit_service import TransitService


async def test_get_transit_car_success(
    mock_place_repo, mock_kakao_client, mock_kakao_mobility_client, sample_place
):
    destination = sample_place.__class__(
        place_id="456",
        name="협재해수욕장",
        category="ACTIVITY",
        address="제주시 어딘가",
        lat=33.5,
        lng=126.6,
    )
    mock_place_repo.get_by_id.side_effect = [sample_place, destination]
    mock_kakao_mobility_client.get_driving_route.return_value = {
        "duration_sec": 600,
        "distance_m": 5000,
    }

    service = TransitService(
        mock_place_repo, mock_kakao_client, mock_kakao_mobility_client
    )
    result = await service.get_transit("123", "456", "CAR")

    assert isinstance(result, TransitResponse)
    assert result.duration_min == 10
    assert result.distance_km == 5.0
    assert result.mode == "CAR"
    mock_kakao_mobility_client.get_driving_route.assert_awaited_once()
    mock_kakao_client.get_walking_route.assert_not_awaited()


async def test_get_transit_walk_success(
    mock_place_repo, mock_kakao_client, mock_kakao_mobility_client, sample_place
):
    destination = sample_place.__class__(
        place_id="456",
        name="협재해수욕장",
        category="ACTIVITY",
        address="제주시 어딘가",
        lat=33.5,
        lng=126.6,
    )
    mock_place_repo.get_by_id.side_effect = [sample_place, destination]
    mock_kakao_client.get_walking_route.return_value = {
        "duration_sec": 300,
        "distance_m": 400,
    }

    service = TransitService(
        mock_place_repo, mock_kakao_client, mock_kakao_mobility_client
    )
    result = await service.get_transit("123", "456", "WALK")

    assert result.duration_min == 5
    assert result.distance_km == 0.4
    assert result.mode == "WALK"
    mock_kakao_mobility_client.get_driving_route.assert_not_awaited()


async def test_get_transit_raises_404_when_place_missing(
    mock_place_repo, mock_kakao_client, mock_kakao_mobility_client
):
    mock_place_repo.get_by_id.return_value = None

    service = TransitService(
        mock_place_repo, mock_kakao_client, mock_kakao_mobility_client
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.get_transit("unknown", "unknown2", "CAR")

    assert exc_info.value.status_code == 404
