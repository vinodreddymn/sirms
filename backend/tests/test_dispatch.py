from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common import Vendor
from app.models.dispatch import Dispatch
from app.services.activity_service import ActivityService
from app.services.dispatch_service import DispatchService

pytestmark = pytest.mark.asyncio

async def test_activity_logging_uses_empty_entity_name_when_missing(
    test_session: AsyncSession,
):
    service = ActivityService(test_session)

    entry = await service.log_activity(
        source="AUTO",
        module="ASSET",
        action="DISPATCH",
        title="Dispatched for Repair",
        metadata={"dispatch_id": "123"},
    )

    assert entry.entity_name == ""


async def test_dispatch_details_include_vendor_name(
    test_session: AsyncSession,
):
    vendor = Vendor(
        id=uuid4(),
        vendor_code="VEND-001",
        vendor_name="Acme Service Center",
        vendor_type="Repair",
    )
    dispatch = Dispatch(
        id=uuid4(),
        dispatch_no="DSP-001",
        dispatch_date=date(2024, 3, 15),
        vendor_id=vendor.id,
        purpose="Repair",
        status="Draft",
    )

    test_session.add_all([vendor, dispatch])
    await test_session.commit()

    service = DispatchService(test_session)
    details = await service.get_dispatch_details(dispatch.id)

    assert details is not None
    assert details["vendor_name"] == "Acme Service Center"


async def test_dispatch_lifecycle(
    admin_client: AsyncClient,
):
    # 1. Create a dispatch
    payload = {
        "dispatch_date": "2024-03-15",
        "purpose": "Repair",
        "items": [
            {
                "dispatch_type": "Component",
                "component_name": "Power Supply",
                "quantity": 1,
                "condition": "Faulty"
            }
        ]
    }
    
    res = await admin_client.post("/api/v1/dispatches", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "dispatch_no" in data
    assert data["status"] == "Draft"
    dispatch_id = data["id"]
    
    # 2. Update dispatch
    update_payload = {
        "remarks": "Urgent repair needed"
    }
    res = await admin_client.put(f"/api/v1/dispatches/{dispatch_id}", json=update_payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["remarks"] == "Urgent repair needed"
    
    # 3. Submit dispatch
    res = await admin_client.post(f"/api/v1/dispatches/{dispatch_id}/submit")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "Dispatched"
    assert data["delivery_challan_no"] is not None
    
    # 4. Get dispatch details (with items)
    res = await admin_client.get(f"/api/v1/dispatches/{dispatch_id}")
    assert res.status_code == 200, res.text
    details = res.json()
    items = details["items"]
    assert len(items) == 1
    item_id = items[0]["id"]
    
    # 5. Receive item
    receive_payload = {
        "return_date": "2024-03-20",
        "result": "Repaired",
        "repair_cost": 150.00,
        "remarks": "Fixed capacitor"
    }
    res = await admin_client.post(
        f"/api/v1/dispatches/{dispatch_id}/items/{item_id}/receive",
        json=receive_payload
    )
    assert res.status_code == 200, res.text
    
    # 6. Verify dispatch is closed
    res = await admin_client.get(f"/api/v1/dispatches/{dispatch_id}")
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "Closed"
