import asyncio
from sqlalchemy import text
from app.db.session import SessionLocal

async def test():
    try:
        async with SessionLocal() as s:
            result = await s.execute(text("SELECT 1"))
            print("DB connection works")
    except Exception as e:
        print(f"DB connection failed: {e}")

asyncio.run(test())