import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, code, name, parent_location_id FROM infrastructure.locations;"))
        rows = result.fetchall()
        for row in rows:
            print(row)

if __name__ == '__main__':
    asyncio.run(main())
