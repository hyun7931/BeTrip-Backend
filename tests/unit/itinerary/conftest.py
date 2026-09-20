import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.itinerary import Itinerary
from app.models.itinerary_place import ItineraryPlace
from app.models.place import Place


@pytest.fixture
def mock_itinerary_repo():
    return AsyncMock()


@pytest.fixture
def sample_user_id():
    return uuid.uuid4()


@pytest.fixture
def sample_itinerary(sample_user_id):
    return Itinerary(
        itinerary_id=uuid.uuid4(),
        user_id=sample_user_id,
        title="제주도 3박4일",
        status="DRAFT",
        region="제주도",
        start_date=date(2026, 8, 10),
        end_date=date(2026, 8, 13),
        arrival_time="LUNCH",
        departure_time="MORNING",
        transportation="CAR",
        purpose="FAMILY",
        styles=["NATURE", "FOOD"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_place():
    return Place(
        place_id="123",
        name="협재해수욕장",
        category="ACTIVITY",
        address="제주시 어딘가",
        lat=33.4,
        lng=126.5,
    )


@pytest.fixture
def sample_itinerary_place(sample_itinerary):
    return ItineraryPlace(
        itinerary_place_id=uuid.uuid4(),
        itinerary_id=sample_itinerary.itinerary_id,
        place_id="123",
        day=1,
        time_slot="LUNCH",
        order_in_day=1,
    )
