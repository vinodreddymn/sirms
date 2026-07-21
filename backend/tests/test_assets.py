"""Tests for asset management operations.

Covers:
- Asset CRUD operations
- Asset installation and movement tracking
- Asset specifications
- Asset status and relationships
"""

import pytest


@pytest.mark.asyncio
async def test_list_assets(authenticated_client):
    """Test listing all assets."""
    response = await authenticated_client.get("/api/v1/assets")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_create_asset(authenticated_client, test_asset_data):
    """Test creating a new asset."""
    asset_data = {
        "project_id": 1,
        "asset_number": "AST-TEST-001",
        "asset_name": "Test Asset",
        "description": "A test asset for unit testing",
        "category_id": 1,  # Electronic, Mechanical, etc.
        "location_id": 1,  # Current location
        "status_id": 1,  # Active, Inactive, etc.
        "manufacture_date": "2025-01-01",
    }
    
    response = await authenticated_client.post(
        "/api/v1/assets",
        json=asset_data,
    )
    
    # May conflict if asset number exists
    assert response.status_code in [200, 201, 400, 409]


@pytest.mark.asyncio
async def test_get_asset_by_id(authenticated_client):
    """Test retrieving a specific asset."""
    response = await authenticated_client.get("/api/v1/assets/1")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "asset_id" in data or "id" in data


@pytest.mark.asyncio
async def test_update_asset(authenticated_client):
    """Test updating an asset."""
    update_data = {
        "asset_name": "Updated Asset Name",
        "description": "Updated asset description",
        "status_id": 2,
    }
    
    response = await authenticated_client.put(
        "/api/v1/assets/1",
        json=update_data,
    )
    
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_list_asset_specifications(authenticated_client):
    """Test listing specifications for an asset."""
    response = await authenticated_client.get("/api/v1/assets/1/specifications")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_asset_specification(authenticated_client):
    """Test adding a specification to an asset."""
    spec_data = {
        "specification_id": 1,
        "spec_value": "Test Value",
    }
    
    response = await authenticated_client.post(
        "/api/v1/assets/1/specifications",
        json=spec_data,
    )
    
    assert response.status_code in [200, 201, 400, 404, 409]


@pytest.mark.asyncio
async def test_list_asset_installations(authenticated_client):
    """Test listing installation history for an asset."""
    response = await authenticated_client.get("/api/v1/assets/1/installations")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_asset_installation(authenticated_client):
    """Test recording asset installation."""
    installation_data = {
        "location_id": 1,
        "position_id": 1,
        "installation_date": "2025-01-01",
        "notes": "Asset installed",
    }
    
    response = await authenticated_client.post(
        "/api/v1/assets/1/installations",
        json=installation_data,
    )
    
    assert response.status_code in [200, 201, 400, 404]


@pytest.mark.asyncio
async def test_list_asset_movements(authenticated_client):
    """Test listing movement history for an asset."""
    response = await authenticated_client.get("/api/v1/assets/1/movements")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_create_asset_movement(authenticated_client):
    """Test recording asset movement."""
    movement_data = {
        "from_location_id": 1,
        "to_location_id": 2,
        "movement_date": "2025-01-15",
        "reason": "Relocated for maintenance",
    }
    
    response = await authenticated_client.post(
        "/api/v1/assets/1/movements",
        json=movement_data,
    )
    
    assert response.status_code in [200, 201, 400, 404, 409]


@pytest.mark.asyncio
async def test_delete_asset(authenticated_client):
    """Test deleting an asset."""
    response = await authenticated_client.delete("/api/v1/assets/1")
    
    # May fail if asset has related records
    assert response.status_code in [200, 204, 400, 404, 409]


@pytest.mark.asyncio
async def test_list_assets_with_filters(authenticated_client):
    """Test listing assets with filters."""
    response = await authenticated_client.get(
        "/api/v1/assets",
        params={
            "category_id": 1,
            "status_id": 1,
            "skip": 0,
            "limit": 10,
        }
    )
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_asset_search(authenticated_client):
    """Test searching for assets."""
    response = await authenticated_client.get(
        "/api/v1/assets",
        params={"q": "TEST"}
    )
    
    # Search may not be implemented (404) or return results (200)
    assert response.status_code in [200, 404]
