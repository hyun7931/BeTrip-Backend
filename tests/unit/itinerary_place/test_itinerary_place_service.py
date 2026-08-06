from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services import itinerary_place_service as service


@pytest.fixture
def db():
    return MagicMock()


# ------------------------------------------------------------------
# get_place_recommendations
# ------------------------------------------------------------------
class TestGetPlaceRecommendations:
    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_itinerary_not_found_raises_404(self, mock_repo, db):
        mock_repo.get_itinerary.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.get_place_recommendations(db, uuid4())

        assert exc_info.value.status_code == 404

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_success_excludes_already_added_places(self, mock_repo, db):
        itinerary_id = uuid4()
        mock_itinerary = MagicMock(region="제주")
        mock_repo.get_itinerary.return_value = mock_itinerary
        mock_repo.get_existing_place_ids.return_value = {"place_1"}
        mock_repo.get_recommended_places.return_value = [MagicMock()]

        result = service.get_place_recommendations(db, itinerary_id, category="CAFE")

        assert result == mock_repo.get_recommended_places.return_value
        mock_repo.get_recommended_places.assert_called_once_with(
            db,
            region="제주",
            exclude_place_ids={"place_1"},
            category="CAFE",
        )


# ------------------------------------------------------------------
# add_place_to_itinerary
# ------------------------------------------------------------------
class TestAddPlaceToItinerary:
    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_itinerary_not_found_raises_404(self, mock_repo, db):
        mock_repo.get_itinerary.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.add_place_to_itinerary(db, uuid4(), "place_1")

        assert exc_info.value.status_code == 404

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_place_not_found_raises_404(self, mock_repo, db):
        mock_repo.get_itinerary.return_value = MagicMock()
        mock_repo.get_place.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.add_place_to_itinerary(db, uuid4(), "place_1")

        assert exc_info.value.status_code == 404

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_duplicate_place_raises_409(self, mock_repo, db):
        mock_repo.get_itinerary.return_value = MagicMock()
        mock_repo.get_place.return_value = MagicMock()
        mock_repo.get_itinerary_place_by_place_id.return_value = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            service.add_place_to_itinerary(db, uuid4(), "place_1")

        assert exc_info.value.status_code == 409

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_success_creates_itinerary_place(self, mock_repo, db):
        itinerary_id = uuid4()
        mock_repo.get_itinerary.return_value = MagicMock()
        mock_repo.get_place.return_value = MagicMock()
        mock_repo.get_itinerary_place_by_place_id.return_value = None
        mock_repo.create_itinerary_place.return_value = MagicMock()

        result = service.add_place_to_itinerary(db, itinerary_id, "place_1")

        assert result == mock_repo.create_itinerary_place.return_value
        mock_repo.create_itinerary_place.assert_called_once_with(
            db, itinerary_id, "place_1"
        )


# ------------------------------------------------------------------
# remove_place_from_itinerary
# ------------------------------------------------------------------
class TestRemovePlaceFromItinerary:
    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_not_found_raises_404(self, mock_repo, db):
        mock_repo.get_itinerary_place.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.remove_place_from_itinerary(db, uuid4(), uuid4())

        assert exc_info.value.status_code == 404

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_belongs_to_other_itinerary_raises_404(self, mock_repo, db):
        other_itinerary_id = uuid4()
        mock_repo.get_itinerary_place.return_value = MagicMock(
            itinerary_id=other_itinerary_id
        )

        with pytest.raises(HTTPException) as exc_info:
            service.remove_place_from_itinerary(db, uuid4(), uuid4())

        assert exc_info.value.status_code == 404

    @patch("app.services.itinerary_place_service.itinerary_place_repo")
    def test_success_deletes_itinerary_place(self, mock_repo, db):
        itinerary_id = uuid4()
        mock_itinerary_place = MagicMock(itinerary_id=itinerary_id)
        mock_repo.get_itinerary_place.return_value = mock_itinerary_place

        service.remove_place_from_itinerary(db, itinerary_id, uuid4())

        mock_repo.delete_itinerary_place.assert_called_once_with(
            db, mock_itinerary_place
        )
