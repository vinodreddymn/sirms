import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'asset' AND table_name = 'assets';"))
        rows = result.fetchall()
        for row in rows:
            print(row)

if __name__ == '__main__':
    asyncio.run(main())
