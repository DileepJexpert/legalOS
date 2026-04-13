import asyncio
import logging
from app.services.auth import AuthService
from app.db.session import SessionLocal

logging.basicConfig(level=logging.DEBUG)

async def test():
    try:
        async with SessionLocal() as s:
            auth = AuthService(s)
            result = await auth.login(email='demo@legalos.dev', password='DemoPass123!')
            print('Login successful:', result)
    except Exception as e:
        print(f'Login failed: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())