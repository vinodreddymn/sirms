import asyncio
from sqlalchemy import text
from app.db.database import engine

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='incident' AND table_name='incidents' "
            "ORDER BY ordinal_position"
        ))
        cols = [r[0] for r in result.fetchall()]
        print("Columns:", cols)
        
        # Check resolution_remarks and closed_by exist
        assert "resolution_remarks" in cols, "resolution_remarks MISSING!"
        assert "closed_by" in cols, "closed_by MISSING!"
        assert "assigned_to" not in cols, "assigned_to still exists!"
        print("Schema looks good!")

asyncio.run(check())
