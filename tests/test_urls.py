import pytest
from httpx import AsyncClient
from app.main import app
import pytest_asyncio # Import the correct decorator
from httpx import ASGITransport # Import ASGITransport

@pytest_asyncio.fixture(scope="function") # Corrected decorator
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture # Corrected decorator
async def url_manager(ac: AsyncClient):
    created_url_ids = []

    async def _create_url(original_url: str):
        response = await ac.post("/api/v1/urls/", json={"original_url": original_url})
        response.raise_for_status()  # Ensure it was created, raises HTTPStatusError for 4xx/5xx
        url_data = response.json()
        created_url_ids.append(url_data["id"])
        return url_data

    yield _create_url

    # Cleanup
    for url_id in created_url_ids:
        try:
            await ac.delete(f"/api/v1/urls/{url_id}")
        except Exception as e:
            # Log or handle deletion errors if necessary, but don't let them fail other tests
            print(f"Error during cleanup, deleting URL ID {url_id}: {e}")


@pytest.mark.asyncio
async def test_create_url_success(ac: AsyncClient, url_manager): # Use url_manager to ensure cleanup
    original_url = "https://www.example.com"
    data = await url_manager(original_url) # Creates and registers for cleanup
    
    assert "id" in data
    assert isinstance(data["id"], int)
    assert "code" in data
    assert isinstance(data["code"], str)
    assert data["original_url"] == original_url
    assert "created_at" in data
    assert isinstance(data["created_at"], str)
    assert data["access_count"] == 0

@pytest.mark.asyncio
async def test_create_url_invalid(ac: AsyncClient): # No URL created, no manager needed
    response = await ac.post("/api/v1/urls/", json={"original_url": "not-a-url"})
    assert response.status_code == 422

    response = await ac.post("/api/v1/urls/", json={"original_url": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_urls_empty(ac: AsyncClient): # Relies on url_manager from other tests for cleanup
    response = await ac.get("/api/v1/urls/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_list_urls_after_creation(ac: AsyncClient, url_manager):
    url1_data = await url_manager("https://www.example1.com")
    url2_data = await url_manager("https://www.example2.com")

    list_response = await ac.get("/api/v1/urls/")
    assert list_response.status_code == 200
    urls_list = list_response.json()
    
    # Now we can expect exactly 2 URLs if url_manager cleans up properly from other tests
    assert len(urls_list) == 2 

    found_url1 = any(item["id"] == url1_data["id"] and item["original_url"] == url1_data["original_url"] for item in urls_list)
    found_url2 = any(item["id"] == url2_data["id"] and item["original_url"] == url2_data["original_url"] for item in urls_list)
    assert found_url1, "Created URL1 not found in list"
    assert found_url2, "Created URL2 not found in list"

    for item in urls_list:
        assert "id" in item
        assert isinstance(item["id"], int)
        assert "code" in item
        assert isinstance(item["code"], str)
        assert "original_url" in item
        assert isinstance(item["original_url"], str)
        assert "created_at" in item
        assert isinstance(item["created_at"], str)
        assert "access_count" in item
        assert isinstance(item["access_count"], int)

@pytest.mark.asyncio
async def test_list_urls_pagination(ac: AsyncClient, url_manager):
    created_urls_data = []
    for i in range(3):
        url_data = await url_manager(f"https://www.pagination-test.com/page{i+1}")
        created_urls_data.append(url_data)

    # Test limit: Get only the first URL
    response_limit1 = await ac.get("/api/v1/urls/", params={"limit": 1})
    assert response_limit1.status_code == 200
    data_limit1 = response_limit1.json()
    assert len(data_limit1) == 1
    # The order might not be guaranteed, so check against one of the created ones.
    # To be more precise, we could sort or fetch all and then slice.
    # Given the fixture, the DB state is clean, so the first one returned should be one of ours.
    assert data_limit1[0]["id"] == created_urls_data[0]["id"]


    # Test skip: Skip the first URL, get the next two
    response_skip1 = await ac.get("/api/v1/urls/", params={"skip": 1})
    assert response_skip1.status_code == 200
    data_skip1 = response_skip1.json()
    assert len(data_skip1) == 2 # Since 3 were created, skipping 1 leaves 2
    assert created_urls_data[0]["id"] not in [item["id"] for item in data_skip1]
    assert created_urls_data[1]["id"] in [item["id"] for item in data_skip1]
    assert created_urls_data[2]["id"] in [item["id"] for item in data_skip1]
        
    # Test skip and limit: Skip 1, Limit 1 (effectively getting the second URL)
    response_skip_limit = await ac.get("/api/v1/urls/", params={"skip": 1, "limit": 1})
    assert response_skip_limit.status_code == 200
    data_skip_limit = response_skip_limit.json()
    assert len(data_skip_limit) == 1
    assert data_skip_limit[0]["id"] == created_urls_data[1]["id"]


@pytest.mark.asyncio
async def test_get_url_by_id_success(ac: AsyncClient, url_manager):
    original_url_to_create = "https://www.getmebyid.com"
    created_url_data = await url_manager(original_url_to_create)
    url_id = created_url_data["id"]

    get_response = await ac.get(f"/api/v1/urls/{url_id}")
    assert get_response.status_code == 200
    retrieved_url_data = get_response.json()
    
    assert retrieved_url_data["id"] == url_id
    assert retrieved_url_data["code"] == created_url_data["code"] 
    assert retrieved_url_data["original_url"] == original_url_to_create
    assert retrieved_url_data["created_at"] == created_url_data["created_at"]
    assert retrieved_url_data["access_count"] == created_url_data["access_count"] 

@pytest.mark.asyncio
async def test_get_url_by_id_not_found(ac: AsyncClient):
    non_existent_id = 9999999 
    response = await ac.get(f"/api/v1/urls/{non_existent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_url_by_id_success(ac: AsyncClient, url_manager):
    original_url_to_create = "https://www.deleteme.com"
    # Create URL using manager, but we will manually delete for this test
    # The manager will try to delete it again, which should result in a 404, handled by the try-except in manager
    created_url_data = await url_manager(original_url_to_create)
    url_id = created_url_data["id"]

    delete_response = await ac.delete(f"/api/v1/urls/{url_id}")
    assert delete_response.status_code == 204

    get_response_after_delete = await ac.get(f"/api/v1/urls/{url_id}")
    assert get_response_after_delete.status_code == 404

@pytest.mark.asyncio
async def test_delete_url_by_id_not_found(ac: AsyncClient):
    non_existent_id = 9999998
    response = await ac.delete(f"/api/v1/urls/{non_existent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_to_url_success(ac: AsyncClient, url_manager):
    original_url = "https://www.google.com"
    created_url_data = await url_manager(original_url)
    url_id = created_url_data["id"]
    url_code = created_url_data["code"]
    initial_access_count = created_url_data["access_count"]

    redirect_response = await ac.get(f"/r/{url_code}", allow_redirects=False)
        
    assert redirect_response.status_code == 307
    assert redirect_response.headers["Location"] == original_url

    get_url_response = await ac.get(f"/api/v1/urls/{url_id}")
    assert get_url_response.status_code == 200 # Should still exist
    updated_url_data = get_url_response.json()
    assert updated_url_data["access_count"] == initial_access_count + 1

@pytest.mark.asyncio
async def test_redirect_non_existent_code(ac: AsyncClient):
    response = await ac.get("/r/nonexistentcode", allow_redirects=False)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_redirect_blocked_domain(ac: AsyncClient, url_manager):
    blocked_url = "http://malicious.com/somepath"
    created_url_data = await url_manager(blocked_url)
    url_code = created_url_data["code"]

    redirect_response = await ac.get(f"/r/{url_code}", allow_redirects=False)
    assert redirect_response.status_code == 403

@pytest.mark.asyncio
async def test_redirect_non_http_protocol(ac: AsyncClient, url_manager):
    non_http_url = "ftp://example.com/resource"
    created_url_data = await url_manager(non_http_url)
    url_code = created_url_data["code"]

    redirect_response = await ac.get(f"/r/{url_code}", allow_redirects=False)
    assert redirect_response.status_code == 403
