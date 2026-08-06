import uuid

from tests.integration.itinerary.conftest import create_itinerary


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
