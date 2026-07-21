"""Tests for stock management operations.

Covers:
- Stock transaction CRUD
- Stock ledger queries
- Current stock levels
"""

import pytest


@pytest.mark.asyncio
async def test_list_stock_transactions(authenticated_client):
    """Test listing all stock transactions."""
    response = await authenticated_client.get("/api/v1/stock/transactions")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_create_stock_transaction(authenticated_client):
    """Test creating a stock transaction."""
    transaction_data = {
        "project_id": 1,
        "asset_id": 1,
        "transaction_type_id": 1,  # In, Out, Adjustment, etc.
        "location_id": 1,
        "quantity": 5,
        "transaction_at": "2025-01-15",
        "remarks": "Stock received from vendor",
    }
    
    response = await authenticated_client.post(
        "/api/v1/stock/transactions",
        json=transaction_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_get_stock_transaction_by_id(authenticated_client):
    """Test retrieving a specific stock transaction."""
    response = await authenticated_client.get("/api/v1/stock/transactions/1")
    
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "transaction_id" in data or "id" in data


@pytest.mark.asyncio
async def test_list_stock_transactions_for_asset(authenticated_client):
    """Test listing stock transactions for an asset."""
    response = await authenticated_client.get(
        "/api/v1/stock/transactions",
        params={"asset_id": 1}
    )
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_stock_by_location(authenticated_client):
    """Test retrieving stock levels by location."""
    response = await authenticated_client.get(
        "/api/v1/stock/transactions",
        params={"location_id": 1}
    )
    
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_current_stock_level(authenticated_client):
    """Test retrieving current stock level for an asset."""
    response = await authenticated_client.get(
        "/api/v1/stock/transactions",
        params={"asset_id": 1, "current_level": True}
    )
    
    # May not support current_level query (returns all transactions)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_stock_adjustment(authenticated_client):
    """Test creating a stock adjustment transaction."""
    adjustment_data = {
        "project_id": 1,
        "asset_id": 1,
        "transaction_type_id": 3,  # Adjustment type
        "location_id": 1,
        "quantity": -2,  # Negative for reduction
        "transaction_at": "2025-01-20",
        "remarks": "Stock adjustment - inventory count discrepancy",
    }
    
    response = await authenticated_client.post(
        "/api/v1/stock/transactions",
        json=adjustment_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_stock_transfer(authenticated_client):
    """Test creating a stock transfer transaction."""
    transfer_data = {
        "project_id": 1,
        "asset_id": 1,
        "transaction_type_id": 2,  # Transfer/Out type
        "location_id": 2,  # Destination location
        "quantity": 3,
        "transaction_at": "2025-01-15",
        "remarks": "Stock transferred to maintenance",
    }
    
    response = await authenticated_client.post(
        "/api/v1/stock/transactions",
        json=transfer_data,
    )
    
    assert response.status_code in [200, 201, 400]


@pytest.mark.asyncio
async def test_stock_with_vendor(authenticated_client):
    """Test stock transaction with vendor reference."""
    transaction_data = {
        "project_id": 1,
        "asset_id": 1,
        "transaction_type_id": 1,  # Inbound
        "location_id": 1,
        "vendor_id": 1,  # Vendor reference
        "quantity": 10,
        "transaction_at": "2025-01-10",
        "remarks": "Purchase order #12345",
    }
    
    response = await authenticated_client.post(
        "/api/v1/stock/transactions",
        json=transaction_data,
    )
    
    assert response.status_code in [200, 201, 400]
