import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text('ALTER TABLE asset.checklist_items RENAME COLUMN item_sequence TO sequence_order;'))
        except Exception:
            pass
        try:
            await conn.execute(text('ALTER TABLE asset.checklist_items RENAME COLUMN item_description TO task_description;'))
        except Exception:
            pass
        try:
            await conn.execute(text('ALTER TABLE asset.checklist_items RENAME COLUMN is_mandatory TO is_required;'))
        except Exception:
            pass
        print('Fixed checklist_items')

if __name__ == '__main__':
    asyncio.run(main())
