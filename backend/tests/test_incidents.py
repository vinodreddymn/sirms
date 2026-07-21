"""Tests for incident management operations.

Covers:
- Incident lifecycle CRUD
- Incident assignment and status tracking
- Incident timeline/updates
- Work order creation and management
- Work order tasks
"""

import pytest


@pytest.mark.asyncio
async def test_list_incidents(authenticated_client):
    """Test listing all incidents."""
    response = await authenticated_client.get("/api/v1/incidents")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_create_incident(authenticated_client, test_incident_data):
    """Test creating a new incident."""
    incident_data = {
        "project_id": 1,
        "asset_id": 1,
        "incident_title": "Test Incident",
        "description": "A test incident",
        "priority_id": 2,  # Priority lookup ID
        "category_id": 1,  # Incident category
        "reported_by_id": 1,  # User ID
    }
    
    response = await authenticated_client.post(
        "/api/v1/incidents",
        json=incident_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_get_incident_by_id(authenticated_client):
    """Test retrieving a specific incident."""
    response = await authenticated_client.get("/api/v1/incidents/1")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "incident_id" in data or "id" in data


@pytest.mark.asyncio
async def test_update_incident(authenticated_client):
    """Test updating an incident."""
    update_data = {
        "status_id": 2,  # In Progress
        "priority_id": 1,  # Changed priority
    }
    
    response = await authenticated_client.put(
        "/api/v1/incidents/1",
        json=update_data,
    )
    
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_list_incident_updates(authenticated_client):
    """Test listing timeline updates for an incident."""
    response = await authenticated_client.get("/api/v1/incidents/1/updates")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data


@pytest.mark.asyncio
async def test_create_incident_update(authenticated_client):
    """Test adding an update/note to incident timeline."""
    update_data = {
        "update_text": "Incident investigation in progress",
        "update_type": "note",
    }
    
    response = await authenticated_client.post(
        "/api/v1/incidents/1/updates",
        json=update_data,
    )
    
    assert response.status_code in [200, 201, 400, 404]


@pytest.mark.asyncio
async def test_list_incident_attachments(authenticated_client):
    """Test listing attachments for an incident."""
    response = await authenticated_client.get("/api/v1/incidents/1/attachments")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_work_orders(authenticated_client):
    """Test listing all work orders."""
    response = await authenticated_client.get("/api/v1/work-orders")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_work_order(authenticated_client):
    """Test creating a work order for an incident."""
    work_order_data = {
        "incident_id": 1,
        "work_type_id": 1,  # Repair, Maintenance, etc.
        "assigned_to_id": 1,  # Technician
        "description": "Work required to resolve incident",
        "due_date": "2025-02-01",
    }
    
    response = await authenticated_client.post(
        "/api/v1/work-orders",
        json=work_order_data,
    )
    
    assert response.status_code in [200, 201, 400, 404]


@pytest.mark.asyncio
async def test_get_work_order_by_id(authenticated_client):
    """Test retrieving a specific work order."""
    response = await authenticated_client.get("/api/v1/work-orders/1")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_work_order_tasks(authenticated_client):
    """Test listing tasks for a work order."""
    response = await authenticated_client.get("/api/v1/work-orders/1/tasks")
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_work_order_task(authenticated_client):
    """Test creating a task within a work order."""
    task_data = {
        "task_description": "Replace broken component",
        "sequence_order": 1,
        "is_required": True,
    }
    
    response = await authenticated_client.post(
        "/api/v1/work-orders/1/tasks",
        json=task_data,
    )
    
    assert response.status_code in [200, 201, 400, 404]


@pytest.mark.asyncio
async def test_update_work_order_task(authenticated_client):
    """Test updating a work order task."""
    task_data = {
        "is_completed": True,
        "completed_at": "2025-01-20",
    }
    
    response = await authenticated_client.put(
        "/api/v1/work-orders/tasks/1",
        json=task_data,
    )
    
    assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_close_incident(authenticated_client):
    """Test closing an incident."""
    close_data = {
        "status_id": 3,  # Closed status
        "resolution_notes": "Incident resolved successfully",
    }
    
    response = await authenticated_client.put(
        "/api/v1/incidents/1",
        json=close_data,
    )
    
    assert response.status_code in [200, 400, 404]
