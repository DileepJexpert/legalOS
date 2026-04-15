from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.repositories.users import UserRepository

logger = logging.getLogger("legalos.auth")


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserRepository(session)

    async def login(self, *, email: str, password: str) -> tuple[str, object]:
        logger.info("login attempt  email=%s", email)
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            logger.warning("login failed  email=%s  reason=%s",
                           email, "user not found" if user is None else "wrong password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        token = create_access_token(
            str(user.id),
            {"organization_id": str(user.organization_id), "role": user.role.value},
        )
        logger.info("login success  email=%s  user_id=%s", user.email, user.id)
        return token, user
