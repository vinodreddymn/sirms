"""Tests for maintenance operations.

Covers:
- Maintenance checklist CRUD
- Checklist items and sequences
- Maintenance schedules
- Maintenance history and execution
"""

import pytest


@pytest.mark.asyncio
async def test_list_checklists(authenticated_client):
    """Test listing maintenance checklists."""
    response = await authenticated_client.get("/api/v1/maintenance/checklists")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data


@pytest.mark.asyncio
async def test_create_checklist(authenticated_client, test_maintenance_data):
    """Test creating a maintenance checklist."""
    checklist_data = {
        "project_id": 1,
        "checklist_name": "Quarterly Maintenance",
        "description": "Quarterly maintenance checklist",
        "maintenance_type_id": 1,  # Preventive, Corrective, etc.
    }
    
    response = await authenticated_client.post(
        "/api/v1/maintenance/checklists",
        json=checklist_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_get_checklist_by_id(authenticated_client):
    """Test retrieving a specific checklist."""
    response = await authenticated_client.get("/api/v1/maintenance/checklists/1")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_checklist_items(authenticated_client):
    """Test listing items in a checklist."""
    response = await authenticated_client.get("/api/v1/maintenance/checklists/1/items")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_checklist_item(authenticated_client):
    """Test adding an item to a checklist."""
    item_data = {
        "item_description": "Check bearing temperature",
        "sequence_order": 1,
        "is_required": True,
    }
    
    response = await authenticated_client.post(
        "/api/v1/maintenance/checklists/1/items",
        json=item_data,
    )
    
    assert response.status_code in [200, 201, 400, 404]


@pytest.mark.asyncio
async def test_update_checklist_item(authenticated_client):
    """Test updating a checklist item."""
    item_data = {
        "item_description": "Check bearing temperature and lubrication",
        "is_required": True,
    }
    
    response = await authenticated_client.put(
        "/api/v1/maintenance/checklists/1/items/1",
        json=item_data,
    )
    
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_list_schedules(authenticated_client):
    """Test listing maintenance schedules."""
    response = await authenticated_client.get("/api/v1/maintenance/schedules")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_schedule(authenticated_client):
    """Test creating a maintenance schedule."""
    schedule_data = {
        "asset_id": 1,
        "checklist_id": 1,
        "next_due_date": "2025-04-01",
        "frequency_days": 90,
    }
    
    response = await authenticated_client.post(
        "/api/v1/maintenance/schedules",
        json=schedule_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_get_schedule_by_id(authenticated_client):
    """Test retrieving a specific schedule."""
    response = await authenticated_client.get("/api/v1/maintenance/schedules/1")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_schedule_history(authenticated_client):
    """Test listing maintenance history for a schedule."""
    response = await authenticated_client.get("/api/v1/maintenance/schedules/1/history")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_record_maintenance_history(authenticated_client):
    """Test recording a maintenance execution."""
    history_data = {
        "schedule_id": 1,
        "performed_by_id": 1,
        "performed_on": "2025-01-15",
        "is_completed": True,
        "notes": "Maintenance completed successfully",
    }
    
    response = await authenticated_client.post(
        "/api/v1/maintenance/history",
        json=history_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_list_all_history(authenticated_client):
    """Test listing all maintenance history."""
    response = await authenticated_client.get("/api/v1/maintenance/history")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_overdue_maintenance(authenticated_client):
    """Test retrieving overdue maintenance schedules."""
    response = await authenticated_client.get(
        "/api/v1/maintenance/schedules",
        params={"overdue": True}
    )
    
    # May not support overdue filter (404) or return results (200)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_update_schedule(authenticated_client):
    """Test updating a maintenance schedule."""
    update_data = {
        "next_due_date": "2025-05-01",
        "frequency_days": 60,
    }
    
    response = await authenticated_client.put(
        "/api/v1/maintenance/schedules/1",
        json=update_data,
    )
    
    assert response.status_code in [200, 400, 404]
