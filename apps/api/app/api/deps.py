from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.domain.user import User
from app.repositories.users import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger("legalos.auth")

_BYPASS_AUTH_EMAIL = "demo@legalos.dev"


async def get_db_session(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    return session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    settings = get_settings()

    if settings.bypass_auth:
        # Dev-only bypass: resolve as the demo user or the first user in DB.
        user = await UserRepository(session).get_by_email(_BYPASS_AUTH_EMAIL)
        if user is None:
            logger.debug("bypass_auth: demo user not found by email, falling back to first user")
            result = await session.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
        if user is None:
            logger.error("bypass_auth is enabled but no users exist — run: make seed")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "BYPASS_AUTH is enabled but no users exist in the database. "
                    "Run: make seed"
                ),
            )
        logger.debug("bypass_auth: resolved request as user=%s org=%s",
                     user.email, user.organization_id)
        return user

    if credentials is None:
        logger.warning("request rejected — no bearer token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload["sub"]
        user_id = UUID(subject)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.warning("request rejected — invalid token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        logger.warning("request rejected — token subject %s not found in DB", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found",
        )
    logger.debug("authenticated user=%s org=%s", user.email, user.organization_id)
    return user
