import asyncio
from sqlalchemy import text
from app.db.database import engine

async def main():
    async with engine.connect() as conn:
        # Check location_types master table
        result = await conn.execute(text("SELECT id, code, name FROM master.location_types LIMIT 10;"))
        rows = result.fetchall()
        print('Location Types:')
        for row in rows:
            print(row)
        
        # Check location_positions
        result2 = await conn.execute(text("SELECT id, location_id, position_number FROM infrastructure.location_positions LIMIT 10;"))
        rows2 = result2.fetchall()
        print('\nPositions:')
        for row in rows2:
            print(row)

if __name__ == '__main__':
    asyncio.run(main())
