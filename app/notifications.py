from aiogram import Bot
from app.db import SessionLocal
from app.services import get_account
from app.i18n import t

EVENT_KEYS={
 "order.created":"notifications.order_created",
 "order.status_changed":"notifications.order_status",
 "delivery.status_changed":"notifications.delivery",
 "payment.completed":"notifications.payment",
 "subscription.paid":"notifications.subscription_paid",
 "user.status_changed":"notifications.user_status",
 "team.member_joined":"notifications.team_joined",
 "team.member_status_changed":"notifications.team_status",
 "cooperation.application_created":"notifications.cooperation",
 "wallet.operation_created":"notifications.wallet",
}

async def send_event(bot:Bot,event:dict):
    uid=event.get("user_id")
    if not uid: return False
    async with SessionLocal() as s:
        account=await get_account(s,int(uid))
        if not account or not account.integration_token or not account.notifications_enabled: return False
        locale=account.locale
        key=EVENT_KEYS.get(event.get("type"),"notifications.generic")
        p=event.get("payload") or {}
        text=t(locale,key,**p)
    try:
        await bot.send_message(account.telegram_user_id,text)
        return True
    except Exception:
        return False
