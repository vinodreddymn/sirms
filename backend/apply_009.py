import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

async def run():
    async with engine.begin() as conn:
        print("Creating pm_details...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incident.pm_details (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                incident_id     UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
                scheduled_date  DATE,
                completion_date DATE,
                pm_checklist_id UUID,
                remarks         TEXT
            );
        """))
        
        print("Creating inspection_details...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incident.inspection_details (
                id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                incident_id     UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
                inspection_date DATE,
                inspector_id    UUID REFERENCES security.users(id) ON DELETE SET NULL,
                result          VARCHAR(50),
                remarks         TEXT
            );
        """))
        
        print("Creating installation_details...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incident.installation_details (
                id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                incident_id       UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
                installation_date DATE,
                installed_by      UUID REFERENCES security.users(id) ON DELETE SET NULL,
                sign_off_date     DATE,
                remarks           TEXT
            );
        """))

        print("Creating vendor_repair_details...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incident.vendor_repair_details (
                id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                incident_id          UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
                vendor_id            UUID,
                dispatch_date        DATE,
                expected_return_date DATE,
                actual_return_date   DATE,
                repair_cost          NUMERIC(12, 2),
                remarks              TEXT
            );
        """))
        
        print("Creating calibration_details...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incident.calibration_details (
                id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                incident_id        UUID NOT NULL UNIQUE REFERENCES incident.incidents(id) ON DELETE CASCADE,
                calibration_date   DATE,
                next_due_date      DATE,
                calibrated_by      UUID REFERENCES security.users(id) ON DELETE SET NULL,
                certificate_number VARCHAR(100),
                result             VARCHAR(50),
                remarks            TEXT
            );
        """))
        
        print("Success: All detail tables created.")

if __name__ == "__main__":
    asyncio.run(run())
