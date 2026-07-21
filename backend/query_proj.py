import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id FROM common.projects LIMIT 1;"))
        row = result.fetchone()
        print(row)

if __name__ == '__main__':
    asyncio.run(main())
