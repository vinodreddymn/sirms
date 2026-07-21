import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.begin() as conn:
        await conn.execute(text('ALTER TABLE asset.asset_movements ADD COLUMN IF NOT EXISTS quantity INTEGER;'))
        print('Column added')

if __name__ == '__main__':
    asyncio.run(main())
