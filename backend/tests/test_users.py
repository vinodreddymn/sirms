import pytest
from httpx import ASGITransport, AsyncClient

from main import create_app


@pytest.mark.asyncio
async def test_create_and_list_users():
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        user_payload = {
            "username": "testuser",
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "Password123!",
        }

        create_response = await client.post("/api/v1/users", json=user_payload)
        if create_response.status_code == 409:
            # If the test database already contains the user, proceed to listing only
            list_response = await client.get("/api/v1/users")
            assert list_response.status_code == 200
            list_body = list_response.json()
            assert list_body["total"] >= 1
            assert any(item["username"] == "testuser" for item in list_body["items"])
            return

        assert create_response.status_code == 200
        body = create_response.json()
        assert body["username"] == "testuser"
        assert body["email"] == "testuser@example.com"

        list_response = await client.get("/api/v1/users")
        assert list_response.status_code == 200
        list_body = list_response.json()
        assert list_body["total"] >= 1
        assert any(item["username"] == "testuser" for item in list_body["items"])
