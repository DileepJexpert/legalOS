import asyncio
from app.db.session import SessionLocal
from app.domain.user import User
from app.domain.organization import Organization  # Import to register
from app.domain.matter import Matter  # Import to register
from sqlalchemy import update

async def main():
    async with SessionLocal() as s:
        await s.execute(
            update(User)
            .where(User.email == 'demo@legalos.local')
            .values(email='demo@legalos.dev')
        )
        await s.commit()
        print("Updated user email")

asyncio.run(main())