from uuid import uuid4

import pytest

from app.repositories.itinerary_place_repository import ItineraryPlaceRepository


@pytest.mark.asyncio
async def test_get_itinerary_returns_created_itinerary(db_session, sample_itinerary):
    repo = ItineraryPlaceRepository(db_session)

    result = await repo.get_itinerary(sample_itinerary.itinerary_id)

    assert result is not None
    assert result.itinerary_id == sample_itinerary.itinerary_id
    assert result.region == "제주"


@pytest.mark.asyncio
async def test_get_itinerary_returns_none_when_not_found(db_session):
    repo = ItineraryPlaceRepository(db_session)

    result = await repo.get_itinerary(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_create_and_get_itinerary_place(
    db_session, sample_itinerary, sample_place
):
    repo = ItineraryPlaceRepository(db_session)
    place = sample_place()
    db_session.add(place)
    await db_session.commit()

    created = await repo.create_itinerary_place(
        sample_itinerary.itinerary_id, place.place_id
    )

    assert created.itinerary_place_id is not None
    assert created.day is None
    assert created.time_slot is None
    assert created.order_in_day is None

    found = await repo.get_itinerary_place(created.itinerary_place_id)
    assert found is not None
    assert found.place_id == place.place_id


@pytest.mark.asyncio
async def test_get_existing_place_ids_excludes_already_added(
    db_session, sample_itinerary, sample_place
):
    repo = ItineraryPlaceRepository(db_session)
    place = sample_place()
    db_session.add(place)
    await db_session.commit()

    await repo.create_itinerary_place(sample_itinerary.itinerary_id, place.place_id)

    existing_ids = await repo.get_existing_place_ids(sample_itinerary.itinerary_id)

    assert existing_ids == {place.place_id}


@pytest.mark.asyncio
async def test_get_itinerary_place_by_place_id_detects_duplicate(
    db_session, sample_itinerary, sample_place
):
    repo = ItineraryPlaceRepository(db_session)
    place = sample_place()
    db_session.add(place)
    await db_session.commit()

    await repo.create_itinerary_place(sample_itinerary.itinerary_id, place.place_id)

    found = await repo.get_itinerary_place_by_place_id(
        sample_itinerary.itinerary_id, place.place_id
    )

    assert found is not None


@pytest.mark.asyncio
async def test_get_recommended_places_filters_region_and_excludes_added(
    db_session, sample_itinerary, sample_place
):
    repo = ItineraryPlaceRepository(db_session)

    jeju_place = sample_place(address="제주특별자치도 제주시 A로 1")
    seoul_place = sample_place(address="서울특별시 강남구 B로 2")
    already_added = sample_place(address="제주특별자치도 서귀포시 C로 3")
    db_session.add_all([jeju_place, seoul_place, already_added])
    await db_session.commit()

    await repo.create_itinerary_place(
        sample_itinerary.itinerary_id, already_added.place_id
    )

    results = await repo.get_recommended_places(
        region="제주",
        exclude_place_ids={already_added.place_id},
    )
    result_ids = {p.place_id for p in results}

    assert jeju_place.place_id in result_ids
    assert seoul_place.place_id not in result_ids
    assert already_added.place_id not in result_ids


@pytest.mark.asyncio
async def test_get_recommended_places_filters_by_category(
    db_session, sample_itinerary, sample_place
):
    repo = ItineraryPlaceRepository(db_session)

    cafe = sample_place(category="CAFE", address="제주특별자치도 제주시 A로 1")
    restaurant = sample_place(
        category="RESTAURANT", address="제주특별자치도 제주시 B로 2"
    )
    db_session.add_all([cafe, restaurant])
    await db_session.commit()

    results = await repo.get_recommended_places(
        region="제주", exclude_place_ids=set(), category="CAFE"
    )
    result_ids = {p.place_id for p in results}

    assert cafe.place_id in result_ids
    assert restaurant.place_id not in result_ids


@pytest.mark.asyncio
async def test_delete_itinerary_place(db_session, sample_itinerary, sample_place):
    repo = ItineraryPlaceRepository(db_session)
    place = sample_place()
    db_session.add(place)
    await db_session.commit()

    created = await repo.create_itinerary_place(
        sample_itinerary.itinerary_id, place.place_id
    )

    await repo.delete_itinerary_place(created)

    found = await repo.get_itinerary_place(created.itinerary_place_id)
    assert found is None
