from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_session
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(str(user.id), user.role.value, user.branch_id)
    refresh_token, expires_at = create_refresh_token(str(user.id))
    session.add(
        RefreshToken(user_id=user.id, token_hash=hash_refresh_token(refresh_token), expires_at=expires_at)
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    data = await request.json()
    token = data.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh_token")
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    token_hash = hash_refresh_token(token)
    result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if stored is None or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    user = (await session.execute(select(User).where(User.id == stored.user_id))).scalar_one()
    access_token = create_access_token(str(user.id), user.role.value, user.branch_id)
    return TokenResponse(access_token=access_token, refresh_token=token)


@router.post("/logout")
async def logout(request: Request, session: AsyncSession = Depends(get_session)) -> dict:
    data = await request.json()
    token = data.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh_token")
    token_hash = hash_refresh_token(token)
    result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()
    if stored:
        await session.delete(stored)
        await session.commit()
    return {"status": "revoked"}
