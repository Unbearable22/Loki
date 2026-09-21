import hashlib,hmac,json
from fastapi import APIRouter,Header,HTTPException,Request
from aiogram import Bot
from app.config import get_settings
from app.db import SessionLocal
from app.notifications import send_event
from app.services import mark_event_once

router=APIRouter(); settings=get_settings()

def verify(raw,signature,secret):
    if not secret or not signature: return False
    return hmac.compare_digest(hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest(),signature)

@router.get("/health")
async def health(): return {"status":"ok"}

@router.post("/integrations/cargo/webhook")
async def cargo(request:Request,x_signature:str|None=Header(default=None)):
    raw=await request.body()
    if not verify(raw,x_signature,settings.cargo_webhook_secret): raise HTTPException(401,"invalid signature")
    event=json.loads(raw)
    # Canonical delivery event should normally be emitted by the marketplace backend.
    return {"ok":True,"event_id":event.get("id")}

@router.post("/integrations/backend/events")
async def backend_events(request:Request,x_signature:str|None=Header(default=None)):
    raw=await request.body()
    if not verify(raw,x_signature,settings.backend_event_secret): raise HTTPException(401,"invalid signature")
    event=json.loads(raw)
    event_id=event.get("id")
    if not event_id: raise HTTPException(400,"missing event id")
    async with SessionLocal() as s:
        fresh=await mark_event_once(s,event_id,event.get("type","unknown"))
    if not fresh: return {"ok":True,"duplicate":True}
    # Bot is injected by app.main at runtime.
    bot:Bot=request.app.state.bot
    await send_event(bot,event)
    return {"ok":True}
