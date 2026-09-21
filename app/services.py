from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import TelegramAccount, ProcessedEvent

async def get_account(session: AsyncSession, telegram_user_id: int):
    r = await session.execute(select(TelegramAccount).where(TelegramAccount.telegram_user_id == telegram_user_id))
    return r.scalar_one_or_none()

async def ensure_account(session: AsyncSession, telegram_user_id: int):
    account = await get_account(session, telegram_user_id)
    if account:
        return account
    account = TelegramAccount(telegram_user_id=telegram_user_id)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account

async def set_locale(session: AsyncSession, telegram_user_id: int, locale: str):
    account = await ensure_account(session, telegram_user_id)
    account.locale = locale
    await session.commit()

async def set_link(session: AsyncSession, telegram_user_id: int, backend_user_id: str, token: str):
    account = await ensure_account(session, telegram_user_id)
    account.backend_user_id = backend_user_id
    account.integration_token = token
    await session.commit()

async def mark_event_once(session: AsyncSession, event_id: str, event_type: str) -> bool:
    exists = await session.execute(select(ProcessedEvent).where(ProcessedEvent.event_id == event_id))
    if exists.scalar_one_or_none():
        return False
    session.add(ProcessedEvent(event_id=event_id, event_type=event_type))
    await session.commit()
    return True
