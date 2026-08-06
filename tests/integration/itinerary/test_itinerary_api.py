import uuid

from tests.integration.itinerary.conftest import create_itinerary


def _valid_conditions_payload(**overrides):
    payload = {
        "start_date": "2026-08-10",
        "end_date": "2026-08-13",
        "region": "제주도",
        "arrival_time": "LUNCH",
        "departure_time": "MORNING",
    }
    payload.update(overrides)
    return payload


class TestCreateItineraryAPI:
    async def test_create_with_required_fields_only(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "DRAFT"
        assert "itinerary_id" in data

    async def test_create_with_all_fields(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(
                transportation="CAR",
                purpose="FAMILY",
                styles=["NATURE", "FOOD"],
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

    async def test_created_itinerary_is_visible_in_detail(self, client, signed_up_user):
        access_token, _ = signed_up_user
        headers = {"Authorization": f"Bearer {access_token}"}

        create_response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(
                transportation="CAR", purpose="FAMILY", styles=["NATURE"]
            ),
            headers=headers,
        )
        itinerary_id = create_response.json()["itinerary_id"]

        detail_response = await client.get(
            f"/api/v1/itineraries/{itinerary_id}", headers=headers
        )

        assert detail_response.status_code == 200
        conditions = detail_response.json()["conditions"]
        assert conditions["region"] == "제주도"
        assert conditions["transportation"] == "CAR"
        assert conditions["styles"] == ["NATURE"]

    async def test_missing_required_field_returns_422(self, client, signed_up_user):
        access_token, _ = signed_up_user
        payload = _valid_conditions_payload()
        del payload["region"]

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_end_date_before_start_date_returns_422(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(
                start_date="2026-08-13", end_date="2026-08-10"
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_trip_longer_than_14_days_returns_422(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(
                start_date="2026-08-01", end_date="2026-08-20"
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_same_day_arrival_after_departure_returns_422(
        self, client, signed_up_user
    ):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(
                start_date="2026-08-10",
                end_date="2026-08-10",
                arrival_time="EVENING",
                departure_time="MORNING",
            ),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_invalid_style_returns_422(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.post(
            "/api/v1/itineraries/conditions",
            json=_valid_conditions_payload(styles=["UNKNOWN"]),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_requires_authentication(self, client):
        response = await client.post(
            "/api/v1/itineraries/conditions", json=_valid_conditions_payload()
        )
        assert response.status_code == 401


class TestListItinerariesAPI:
    async def test_returns_empty_list_when_none(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.get(
            "/api/v1/itineraries",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"itineraries": []}

    async def test_returns_only_owned_itineraries(
        self, client, db_session, signed_up_user
    ):
        access_token, user_id = signed_up_user
        await create_itinerary(db_session, user_id, title="첫번째")
        await create_itinerary(db_session, user_id, title="두번째")

        response = await client.get(
            "/api/v1/itineraries",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        titles = {it["title"] for it in response.json()["itineraries"]}
        assert titles == {"첫번째", "두번째"}

    async def test_does_not_expose_other_users_itineraries(
        self, client, db_session, signed_up_user
    ):
        access_token, _ = signed_up_user
        other_signup = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "other-list@example.com",
                "password": "Passw0rd!",
                "nickname": "다른사람",
            },
        )
        other_user_id = uuid.UUID(other_signup.json()["user_id"])
        await create_itinerary(db_session, other_user_id, title="다른사람 일정")

        response = await client.get(
            "/api/v1/itineraries",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        assert response.json() == {"itineraries": []}

    async def test_requires_authentication(self, client):
        response = await client.get("/api/v1/itineraries")
        assert response.status_code == 401


class TestGetItineraryDetailAPI:
    async def test_returns_detail_with_empty_places_and_null_schedule(
        self, client, db_session, signed_up_user
    ):
        access_token, user_id = signed_up_user
        itinerary = await create_itinerary(db_session, user_id)

        response = await client.get(
            f"/api/v1/itineraries/{itinerary.itinerary_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["itinerary_id"] == str(itinerary.itinerary_id)
        assert data["places"] == []
        assert data["schedule"] is None
        assert data["conditions"]["region"] == "제주도"
        assert data["conditions"]["styles"] == ["NATURE", "FOOD"]

    async def test_other_users_itinerary_returns_404(
        self, client, db_session, signed_up_user
    ):
        _, owner_id = signed_up_user
        itinerary = await create_itinerary(db_session, owner_id)

        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "other-detail@example.com",
                "password": "Passw0rd!",
                "nickname": "다른사람",
            },
        )
        other_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "other-detail@example.com", "password": "Passw0rd!"},
        )
        other_token = other_login.json()["access_token"]

        response = await client.get(
            f"/api/v1/itineraries/{itinerary.itinerary_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 404

    async def test_nonexistent_itinerary_returns_404(self, client, signed_up_user):
        access_token, _ = signed_up_user

        response = await client.get(
            f"/api/v1/itineraries/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

    async def test_requires_authentication(self, client):
        response = await client.get(f"/api/v1/itineraries/{uuid.uuid4()}")
        assert response.status_code == 401


class TestDeleteItineraryAPI:
    async def test_delete_success(self, client, db_session, signed_up_user):
        access_token, user_id = signed_up_user
        itinerary = await create_itinerary(db_session, user_id)

        response = await client.delete(
            f"/api/v1/itineraries/{itinerary.itinerary_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/itineraries/{itinerary.itinerary_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert get_response.status_code == 404

    async def test_other_users_itinerary_delete_returns_404(
        self, client, db_session, signed_up_user
    ):
        _, owner_id = signed_up_user
        itinerary = await create_itinerary(db_session, owner_id)

        await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "other-delete@example.com",
                "password": "Passw0rd!",
                "nickname": "다른사람",
            },
        )
        other_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "other-delete@example.com", "password": "Passw0rd!"},
        )
        other_token = other_login.json()["access_token"]

        response = await client.delete(
            f"/api/v1/itineraries/{itinerary.itinerary_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 404

    async def test_nonexistent_itinerary_delete_returns_404(
        self, client, signed_up_user
    ):
        access_token, _ = signed_up_user

        response = await client.delete(
            f"/api/v1/itineraries/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

    async def test_requires_authentication(self, client):
        response = await client.delete(f"/api/v1/itineraries/{uuid.uuid4()}")
        assert response.status_code == 401
