import uuid

import pytest
from fastapi import HTTPException

from app.services.itinerary_service import ItineraryService


class TestListItineraries:
    async def test_list_returns_owned_itineraries(
        self, mock_itinerary_repo, sample_itinerary, sample_user_id
    ):
        mock_itinerary_repo.find_all_by_user.return_value = [sample_itinerary]

        service = ItineraryService(mock_itinerary_repo)
        result = await service.list_itineraries(sample_user_id)

        assert len(result) == 1
        assert result[0].itinerary_id == sample_itinerary.itinerary_id
        assert result[0].region == "제주도"
        mock_itinerary_repo.find_all_by_user.assert_awaited_once_with(sample_user_id)

    async def test_list_returns_empty_when_no_itineraries(
        self, mock_itinerary_repo, sample_user_id
    ):
        mock_itinerary_repo.find_all_by_user.return_value = []

        service = ItineraryService(mock_itinerary_repo)
        result = await service.list_itineraries(sample_user_id)

        assert result == []


class TestGetItineraryDetail:
    async def test_get_detail_success_with_places(
        self,
        mock_itinerary_repo,
        sample_itinerary,
        sample_place,
        sample_itinerary_place,
        sample_user_id,
    ):
        mock_itinerary_repo.find_by_id.return_value = sample_itinerary
        mock_itinerary_repo.find_places.return_value = [
            (sample_itinerary_place, sample_place)
        ]

        service = ItineraryService(mock_itinerary_repo)
        result = await service.get_itinerary_detail(
            sample_user_id, sample_itinerary.itinerary_id
        )

        assert result.itinerary_id == sample_itinerary.itinerary_id
        assert result.schedule is None
        assert len(result.places) == 1
        assert result.places[0].place_id == "123"
        assert result.conditions.region == "제주도"

    async def test_get_detail_no_places_returns_empty_list_and_null_schedule(
        self, mock_itinerary_repo, sample_itinerary, sample_user_id
    ):
        mock_itinerary_repo.find_by_id.return_value = sample_itinerary
        mock_itinerary_repo.find_places.return_value = []

        service = ItineraryService(mock_itinerary_repo)
        result = await service.get_itinerary_detail(
            sample_user_id, sample_itinerary.itinerary_id
        )

        assert result.places == []
        assert result.schedule is None

    async def test_get_detail_not_found_raises_404(
        self, mock_itinerary_repo, sample_user_id
    ):
        mock_itinerary_repo.find_by_id.return_value = None

        service = ItineraryService(mock_itinerary_repo)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_itinerary_detail(sample_user_id, uuid.uuid4())

        assert exc_info.value.status_code == 404

    async def test_get_detail_other_users_itinerary_raises_404(
        self, mock_itinerary_repo, sample_itinerary
    ):
        mock_itinerary_repo.find_by_id.return_value = sample_itinerary

        service = ItineraryService(mock_itinerary_repo)

        with pytest.raises(HTTPException) as exc_info:
            await service.get_itinerary_detail(
                uuid.uuid4(), sample_itinerary.itinerary_id
            )

        assert exc_info.value.status_code == 404


class TestDeleteItinerary:
    async def test_delete_success(
        self, mock_itinerary_repo, sample_itinerary, sample_user_id
    ):
        mock_itinerary_repo.find_by_id.return_value = sample_itinerary

        service = ItineraryService(mock_itinerary_repo)
        await service.delete_itinerary(
            sample_itinerary.user_id, sample_itinerary.itinerary_id
        )

        mock_itinerary_repo.delete.assert_awaited_once_with(sample_itinerary)

    async def test_delete_not_found_raises_404(
        self, mock_itinerary_repo, sample_user_id
    ):
        mock_itinerary_repo.find_by_id.return_value = None

        service = ItineraryService(mock_itinerary_repo)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_itinerary(sample_user_id, uuid.uuid4())

        assert exc_info.value.status_code == 404
        mock_itinerary_repo.delete.assert_not_awaited()

    async def test_delete_other_users_itinerary_raises_404(
        self, mock_itinerary_repo, sample_itinerary
    ):
        mock_itinerary_repo.find_by_id.return_value = sample_itinerary

        service = ItineraryService(mock_itinerary_repo)

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_itinerary(uuid.uuid4(), sample_itinerary.itinerary_id)

        assert exc_info.value.status_code == 404
        mock_itinerary_repo.delete.assert_not_awaited()
