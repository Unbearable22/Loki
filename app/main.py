import asyncio,logging
from contextlib import asynccontextmanager
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI,HTTPException
from aiogram.types import Update
import uvicorn
from app.config import get_settings
from app.db import init_db
from app.handlers import router
from app.webhooks import router as web_router

settings=get_settings()
logging.basicConfig(level=settings.log_level)
bot=Bot(settings.telegram_bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher(); dp.include_router(router)

@asynccontextmanager
async def lifespan(app:FastAPI):
    await init_db(); app.state.bot=bot
    if settings.telegram_use_webhook:
        await bot.set_webhook(settings.public_webhook_url,secret_token=settings.telegram_webhook_secret)
    yield
    if settings.telegram_use_webhook: await bot.delete_webhook()
    await bot.session.close()

app=FastAPI(title="Marketplace Telegram Integration",lifespan=lifespan)
app.include_router(web_router)

@app.post("/telegram/webhook")
async def telegram_webhook(update:dict,x_telegram_bot_api_secret_token:str|None=None):
    if x_telegram_bot_api_secret_token!=settings.telegram_webhook_secret: raise HTTPException(401,"invalid telegram secret")
    await dp.feed_update(bot,Update.model_validate(update)); return {"ok":True}

async def polling():
    await init_db(); await bot.delete_webhook(drop_pending_updates=True); await dp.start_polling(bot)

async def main():
    if settings.telegram_use_webhook:
        await uvicorn.Server(uvicorn.Config(app,host=settings.app_host,port=settings.app_port)).serve()
    else: await polling()
