import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

async def run():
    async with engine.begin() as conn:
        try:
            print("Adding resolution_remarks to incident.incidents...")
            await conn.execute(text("ALTER TABLE incident.incidents ADD COLUMN resolution_remarks TEXT;"))
            print("Success")
        except Exception as e:
            print(f"Skipped resolution_remarks: {e}")
            
        try:
            print("Adding closed_by to incident.incidents...")
            await conn.execute(text("ALTER TABLE incident.incidents ADD COLUMN closed_by UUID REFERENCES security.users(id) ON DELETE SET NULL;"))
            print("Success")
        except Exception as e:
            print(f"Skipped closed_by: {e}")
            
        try:
            print("Dropping work_orders related tables...")
            await conn.execute(text("DROP TABLE IF EXISTS incident.work_order_tasks CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS incident.work_orders CASCADE;"))
            print("Success")
        except Exception as e:
            print(f"Failed dropping work orders: {e}")
            
        try:
            print("Dropping assigned_to (CASCADE)...")
            await conn.execute(text("ALTER TABLE incident.incidents DROP COLUMN IF EXISTS assigned_to CASCADE;"))
            print("Success")
        except Exception as e:
            print(f"Failed dropping assigned_to: {e}")

if __name__ == "__main__":
    asyncio.run(run())
