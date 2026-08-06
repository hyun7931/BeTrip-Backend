class TestSignupAPI:
    async def test_signup_success(self, client):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "new@example.com",
                "password": "Passw0rd!",
                "nickname": "새유저",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "password_hash" not in data  # 민감정보 노출 안 되는지 확인

    async def test_signup_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "password": "Passw0rd!",
            "nickname": "중복",
        }
        await client.post("/api/v1/auth/signup", json=payload)

        response = await client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 409

    async def test_signup_weak_password_rejected(self, client):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "weak@example.com",
                "password": "weakpass",
                "nickname": "약함",
            },
        )
        assert response.status_code == 422  # 특수문자/대문자 없음


class TestLoginAPI:
    async def test_login_success_sets_refresh_cookie(self, client):
        signup_payload = {
            "email": "login@example.com",
            "password": "Passw0rd!",
            "nickname": "로그인",
        }
        await client.post("/api/v1/auth/signup", json=signup_payload)

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "Passw0rd!"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.cookies

    async def test_login_wrong_password(self, client):
        signup_payload = {
            "email": "wrongpw@example.com",
            "password": "Passw0rd!",
            "nickname": "테스트",
        }
        await client.post("/api/v1/auth/signup", json=signup_payload)

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrongpw@example.com", "password": "WrongOne!"},
        )
        assert response.status_code == 401


class TestRefreshAPI:
    async def test_refresh_flow_issues_new_token(self, client):
        signup_payload = {
            "email": "refresh@example.com",
            "password": "Passw0rd!",
            "nickname": "리프레시",
        }
        await client.post("/api/v1/auth/signup", json=signup_payload)

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "refresh@example.com", "password": "Passw0rd!"},
        )
        old_access_token = login_response.json()["access_token"]

        # client가 쿠키를 자동으로 들고 있으므로 별도 전달 불필요
        refresh_response = await client.post("/api/v1/auth/refresh")

        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        assert new_access_token != old_access_token

    async def test_refresh_without_cookie_fails(self, client):
        response = await client.post("/api/v1/auth/refresh")
        assert response.status_code == 401

    async def test_reused_refresh_token_revokes_session(self, client):
        signup_payload = {
            "email": "reuse@example.com",
            "password": "Passw0rd!",
            "nickname": "재사용",
        }
        await client.post("/api/v1/auth/signup", json=signup_payload)
        await client.post(
            "/api/v1/auth/login",
            json={"email": "reuse@example.com", "password": "Passw0rd!"},
        )

        old_refresh_token = client.cookies.get("refresh_token")

        # 정상 refresh -> 기존 토큰 폐기, 새 토큰 발급
        await client.post("/api/v1/auth/refresh")

        # 이미 폐기된(첫 번째) refresh token으로 재시도 -> 탈취 의심 처리돼야 함
        client.cookies.set("refresh_token", old_refresh_token)
        response = await client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
