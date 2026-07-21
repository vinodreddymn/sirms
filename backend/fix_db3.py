import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text('ALTER TABLE asset.maintenance_history RENAME COLUMN maintenance_schedule_id TO schedule_id;'))
        except Exception:
            pass
        try:
            await conn.execute(text('ALTER TABLE asset.maintenance_history RENAME COLUMN completion_notes TO remarks;'))
        except Exception:
            pass
        try:
            await conn.execute(text('ALTER TABLE asset.maintenance_history ADD COLUMN IF NOT EXISTS completed BOOLEAN DEFAULT FALSE;'))
        except Exception:
            pass
        print('Fixed maintenance_history')

if __name__ == '__main__':
    asyncio.run(main())
