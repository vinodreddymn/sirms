#!/usr/bin/env python
"""CLI script to seed permissions into SIRMS database.

Syncs permission codes from a manifest file to the database, creating
any missing Permission records in the security schema.

Usage:
    python scripts/seed_permissions.py
    python scripts/seed_permissions.py --manifest custom_permissions.json
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import click
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.config import get_settings
from app.models.security import Permission


# Default permission manifest
DEFAULT_PERMISSIONS: Dict[str, List[Dict]] = {
    "master": [
        {"code": "lookup.read", "name": "Read Lookups", "description": "View lookup tables"},
        {"code": "lookup.create", "name": "Create Lookup", "description": "Create new lookup table"},
        {"code": "lookup.update", "name": "Update Lookup", "description": "Modify lookup table"},
        {"code": "lookup.delete", "name": "Delete Lookup", "description": "Delete lookup table"},
        {"code": "specification.read", "name": "Read Specifications", "description": "View specification definitions"},
        {"code": "specification.create", "name": "Create Specification", "description": "Create new specification"},
        {"code": "specification.update", "name": "Update Specification", "description": "Modify specification"},
        {"code": "specification.delete", "name": "Delete Specification", "description": "Delete specification"},
    ],
    "infrastructure": [
        {"code": "location.read", "name": "Read Locations", "description": "View infrastructure locations"},
        {"code": "location.create", "name": "Create Location", "description": "Create new location"},
        {"code": "location.update", "name": "Update Location", "description": "Modify location"},
        {"code": "location.delete", "name": "Delete Location", "description": "Delete location"},
        {"code": "position.read", "name": "Read Positions", "description": "View positions"},
        {"code": "position.create", "name": "Create Position", "description": "Create new position"},
    ],
    "asset": [
        {"code": "asset.read", "name": "Read Assets", "description": "View assets"},
        {"code": "asset.create", "name": "Create Asset", "description": "Create new asset"},
        {"code": "asset.update", "name": "Update Asset", "description": "Modify asset"},
        {"code": "asset.delete", "name": "Delete Asset", "description": "Delete asset"},
        {"code": "asset.move", "name": "Move Asset", "description": "Record asset movement"},
        {"code": "asset.install", "name": "Install Asset", "description": "Record asset installation"},
    ],
    "incident": [
        {"code": "incident.read", "name": "Read Incidents", "description": "View incidents"},
        {"code": "incident.create", "name": "Create Incident", "description": "Report new incident"},
        {"code": "incident.update", "name": "Update Incident", "description": "Modify incident status/assignment"},
        {"code": "incident.close", "name": "Close Incident", "description": "Close resolved incident"},
        {"code": "workorder.read", "name": "Read Work Orders", "description": "View work orders"},
        {"code": "workorder.create", "name": "Create Work Order", "description": "Create work order for incident"},
        {"code": "workorder.update", "name": "Update Work Order", "description": "Update work order status"},
    ],
    "maintenance": [
        {"code": "maintenance.read", "name": "Read Maintenance", "description": "View maintenance data"},
        {"code": "maintenance.create", "name": "Create Maintenance", "description": "Create maintenance schedule"},
        {"code": "maintenance.update", "name": "Update Maintenance", "description": "Update maintenance data"},
        {"code": "maintenance.execute", "name": "Execute Maintenance", "description": "Record maintenance completion"},
    ],
    "stock": [
        {"code": "stock.read", "name": "Read Stock", "description": "View stock levels"},
        {"code": "stock.create", "name": "Record Transaction", "description": "Record stock in/out/adjustment"},
        {"code": "stock.update", "name": "Update Stock", "description": "Modify transaction"},
    ],
    "admin": [
        {"code": "user.read", "name": "Read Users", "description": "View user accounts"},
        {"code": "user.create", "name": "Create User", "description": "Create new user"},
        {"code": "user.update", "name": "Update User", "description": "Modify user"},
        {"code": "user.delete", "name": "Delete User", "description": "Delete user account"},
        {"code": "permission.manage", "name": "Manage Permissions", "description": "Create/modify permissions"},
        {"code": "role.manage", "name": "Manage Roles", "description": "Create/modify roles"},
        {"code": "system.admin", "name": "System Admin", "description": "Full system access"},
    ],
}


async def seed_permissions(manifest_path: str | None = None) -> int:
    """Seed permissions into database from manifest.
    
    Args:
        manifest_path: Path to JSON manifest file (uses default if None)
        
    Returns:
        Number of permissions created
    """
    # Load permissions
    if manifest_path:
        with open(manifest_path, "r") as f:
            permissions_manifest = json.load(f)
    else:
        permissions_manifest = DEFAULT_PERMISSIONS
    
    # Connect to database
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    created_count = 0
    
    try:
        async with async_session() as session:
            # Flatten permissions from manifest
            all_permissions = []
            for category, perms in permissions_manifest.items():
                for perm in perms:
                    all_permissions.append(perm)
            
            # Check and create missing permissions
            for perm_data in all_permissions:
                code = perm_data["code"]
                
                # Check if permission already exists
                stmt = select(Permission).where(Permission.code == code)
                existing = await session.execute(stmt)
                if existing.scalar_one_or_none():
                    continue
                
                # Create new permission
                permission = Permission(
                    code=code,
                    name=perm_data.get("name", code),
                    description=perm_data.get("description", ""),
                )
                session.add(permission)
                created_count += 1
            
            # Commit all new permissions
            await session.commit()
            
            # Get total permission count
            stmt = select(Permission)
            result = await session.execute(stmt)
            total_count = len(result.scalars().all())
            
            return created_count, total_count
    
    finally:
        await engine.dispose()


@click.command()
@click.option(
    "--manifest",
    type=click.Path(exists=True),
    help="Path to JSON permission manifest file",
)
@click.option(
    "--show-manifest",
    is_flag=True,
    help="Display default permission manifest and exit",
)
def main(manifest: str | None, show_manifest: bool):
    """Seed permissions into SIRMS database.
    
    Creates Permission records for all codes defined in the manifest.
    Skips permissions that already exist.
    """
    if show_manifest:
        click.echo("Default Permission Manifest:")
        click.echo(json.dumps(DEFAULT_PERMISSIONS, indent=2))
        return
    
    try:
        click.echo("Seeding permissions...")
        created, total = asyncio.run(seed_permissions(manifest))
        
        click.secho(
            f"✓ Permissions synced successfully!",
            fg="green",
            bold=True,
        )
        click.echo(f"  Created: {created}")
        click.echo(f"  Total in database: {total}")
        
    except FileNotFoundError as e:
        click.secho(f"✗ File not found: {str(e)}", fg="red", bold=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.secho(f"✗ Invalid JSON: {str(e)}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg="red", bold=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
