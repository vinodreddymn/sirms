import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine('postgresql+asyncpg://svr_user:india123@localhost:5432/sirms')
    async with engine.connect() as conn:
        print("--- SCHEMA INVENTORY CHECK ---")
        res = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'inventory'"))
        print("Schema 'inventory' exists:", bool(res.fetchall()))

        print("--- ALEMBIC VERSION ---")
        res = await conn.execute(text("SELECT version_num FROM alembic_version"))
        print("Current Alembic Version:", res.scalar())

        print("--- FUNCTIONS IN SCHEMA COMMON ---")
        res = await conn.execute(text("""
            SELECT proname, pg_get_function_arguments(oid) 
            FROM pg_proc 
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'common')
        """))
        for row in res:
            print(f"Function: {row[0]}, Arguments: {row[1]}")

        print("--- NUMBER SEQUENCES SEEDED ---")
        res = await conn.execute(text("SELECT entity_name, prefix, current_value FROM common.number_sequences"))
        for row in res:
            print(row)

asyncio.run(main())
