"""Clear alembic_version table to start fresh."""
import asyncio
from app.db.database import get_async_engine
from sqlalchemy import text

async def clear_alembic_version():
    engine = get_async_engine()
    async with engine.connect() as conn:
        await conn.execute(text('DELETE FROM alembic_version'))
        await conn.commit()
    print("Cleared alembic_version table")

if __name__ == "__main__":
    asyncio.run(clear_alembic_version())