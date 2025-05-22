import pytest
from httpx import AsyncClient, ASGITransport # Import ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Registro
        response = await ac.post("/api/v1/users/register", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        assert response.status_code == 201
        # Login
        response = await ac.post("/api/v1/users/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]
        # Acceso protegido
        response = await ac.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"
