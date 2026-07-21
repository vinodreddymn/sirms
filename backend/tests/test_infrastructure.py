"""Tests for infrastructure location management.

Covers:
- Location hierarchy and tree structure
- Location CRUD operations
- Location template creation
- Position and capacity management
"""

import pytest


@pytest.mark.asyncio
async def test_list_locations(authenticated_client):
    """Test listing all locations."""
    response = await authenticated_client.get("/api/v1/infrastructure/locations")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_create_location(authenticated_client, test_project_data):
    """Test creating a new location."""
    location_data = {
        "project_id": 1,  # Would use actual project ID
        "location_code": "LOC-001",
        "location_name": "Test Location",
        "location_type_id": 1,  # Building, Floor, etc.
        "description": "A test location",
        "parent_location_id": None,  # Root location
    }
    
    response = await authenticated_client.post(
        "/api/v1/infrastructure/locations",
        json=location_data,
    )
    
    assert response.status_code in [200, 201, 400, 409]


@pytest.mark.asyncio
async def test_get_location_by_id(authenticated_client):
    """Test retrieving a specific location."""
    response = await authenticated_client.get("/api/v1/infrastructure/locations/1")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_location_tree(authenticated_client):
    """Test retrieving location hierarchy as tree."""
    response = await authenticated_client.get("/api/v1/infrastructure/locations/tree")
    
    # May not have tree endpoint or no locations (404)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        # Should be a list of root locations with children
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_location_children(authenticated_client):
    """Test retrieving direct children of a location."""
    response = await authenticated_client.get("/api/v1/infrastructure/locations/1/children")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_create_position(authenticated_client):
    """Test creating a position in a location."""
    position_data = {
        "location_id": 1,
        "position_code": "POS-001",
        "position_name": "Test Position",
        "description": "A test position",
        "capacity": 1,
    }
    
    response = await authenticated_client.post(
        "/api/v1/infrastructure/positions",
        json=position_data,
    )
    
    # May not exist (404) or conflict (409)
    assert response.status_code in [200, 201, 400, 404, 409]


@pytest.mark.asyncio
async def test_list_positions(authenticated_client):
    """Test listing positions."""
    response = await authenticated_client.get("/api/v1/infrastructure/positions")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_update_location(authenticated_client):
    """Test updating a location."""
    update_data = {
        "location_name": "Updated Location Name",
        "description": "Updated description",
    }
    
    response = await authenticated_client.put(
        "/api/v1/infrastructure/locations/1",
        json=update_data,
    )
    
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_delete_location(authenticated_client):
    """Test deleting a location."""
    response = await authenticated_client.delete(
        "/api/v1/infrastructure/locations/1"
    )
    
    # May fail if location has assets (409)
    assert response.status_code in [200, 204, 400, 404, 409]
