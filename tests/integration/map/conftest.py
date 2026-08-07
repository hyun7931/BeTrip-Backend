from app.models.place import Place


async def create_place(db_session, **overrides) -> Place:
    defaults = {
        "place_id": "test-place-1",
        "name": "테스트카페",
        "category": "CAFE",
        "address": "서울시 어딘가",
        "lat": 37.5,
        "lng": 127.0,
        "place_url": "http://place.map.kakao.com/test-place-1",
        "thumbnail_url": None,
    }
    defaults.update(overrides)
    place = Place(**defaults)
    db_session.add(place)
    await db_session.commit()
    await db_session.refresh(place)
    return place
