from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from app.db import SessionLocal
from app.i18n import t, available_locales
from app.integrations.backend import BackendClient, BackendError
from app.keyboards import main_menu,languages,seller_menu,product_actions,order_actions,back
from app.services import ensure_account,get_account,set_locale,set_link

router=Router(); backend=BackendClient()

class ProductForm(StatesGroup):
    name=State(); price=State(); stock=State()
class EditProductForm(StatesGroup):
    product_id=State(); field=State(); value=State()
class WalletForm(StatesGroup):
    action=State(); amount=State()
class TeamFilter(StatesGroup):
    level=State()
class CooperationForm(StatesGroup):
    company=State(); type=State(); geography=State(); warehouses=State(); branches=State()
    pvz=State(); tariffs=State(); api=State(); tracking=State(); webhook=State(); documents=State()

async def locale_for(uid):
    async with SessionLocal() as s:
        a=await ensure_account(s,uid); return a.locale

async def token_for(uid):
    async with SessionLocal() as s:
        a=await get_account(s,uid); return a.integration_token if a else None

@router.message(CommandStart())
async def start(m:Message):
    async with SessionLocal() as s:
        a=await ensure_account(s,m.from_user.id); locale=a.locale
    await m.answer(t(locale,"start.welcome"),reply_markup=languages())

@router.callback_query(F.data.startswith("lang:"))
async def lang(c:CallbackQuery):
    locale=c.data.split(":")[1]
    if locale not in available_locales(): locale="ru"
    async with SessionLocal() as s: await set_locale(s,c.from_user.id,locale)
    await c.message.edit_text(t(locale,"start.language_saved"))
    await c.message.answer(t(locale,"start.menu"),reply_markup=main_menu(locale))
    await c.answer()

@router.message(F.text)
async def menu(m:Message,state:FSMContext):
    locale=await locale_for(m.from_user.id); text=m.text; tok=await token_for(m.from_user.id)
    if text==t(locale,"menu.language"):
        await m.answer(t(locale,"language.choose"),reply_markup=languages()); return
    if text==t(locale,"menu.help"):
        await m.answer(t(locale,"help.text")); return
    if text==t(locale,"menu.notifications"):
        await m.answer(t(locale,"notifications.info")); return
    if text==t(locale,"menu.seller"):
        await m.answer(t(locale,"seller.title"),reply_markup=seller_menu(locale)); return
    if not tok and text in {t(locale,"menu.orders"),t(locale,"menu.wallet"),t(locale,"menu.team"),t(locale,"menu.status"),t(locale,"menu.cooperation")}:
        await m.answer(t(locale,"auth.required")); return

    try:
        if text==t(locale,"menu.orders"):
            data=await backend.orders(tok); items=data.get("items",data if isinstance(data,list) else [])
            if not items: await m.answer(t(locale,"orders.empty")); return
            for o in items[:20]:
                await m.answer(t(locale,"orders.item",id=o.get("id","—"),status=o.get("status","—"),total=o.get("total","—")),reply_markup=order_actions(locale,o.get("id")))
        elif text==t(locale,"menu.wallet"):
            d=await backend.wallet(tok)
            await m.answer(t(locale,"wallet.summary",total=d.get("balance","—"),available=d.get("available","—"),frozen=d.get("frozen","—"),currency=d.get("currency","")))
            await m.answer(t(locale,"wallet.actions"))
        elif text==t(locale,"menu.team"):
            d=await backend.team(tok)
            await m.answer(t(locale,"team.summary",total=d.get("total","—"),active=d.get("active","—"),inactive=d.get("inactive","—"),new=d.get("new","—"),reward=d.get("reward","—"),progress=d.get("progress","—")))
        elif text==t(locale,"menu.status"):
            d=await backend.status(tok); s=await backend.subscription(tok)
            await m.answer(t(locale,"status.summary",current=d.get("current","—"),next=d.get("next","—"),progress=d.get("progress","—"),conditions=d.get("conditions","—")))
            await m.answer(t(locale,"subscription.summary",plan=s.get("plan","—"),expires=s.get("expires_at","—"),status=s.get("status","—")))
        elif text==t(locale,"menu.cooperation"):
            await state.set_state(CooperationForm.company); await m.answer(t(locale,"cooperation.company"))
    except BackendError:
        await m.answer(t(locale,"errors.backend"))

@router.callback_query(F.data=="seller:add")
async def add(c,state:FSMContext):
    locale=await locale_for(c.from_user.id); await state.set_state(ProductForm.name); await c.message.answer(t(locale,"seller.form.name")); await c.answer()

@router.message(ProductForm.name)
async def pname(m,state):
    locale=await locale_for(m.from_user.id); await state.update_data(name=m.text); await state.set_state(ProductForm.price); await m.answer(t(locale,"seller.form.price"))

@router.message(ProductForm.price)
async def pprice(m,state):
    locale=await locale_for(m.from_user.id)
    try: v=float(m.text.replace(",",".")); assert v>=0
    except: await m.answer(t(locale,"seller.form.invalid_price")); return
    await state.update_data(price=v); await state.set_state(ProductForm.stock); await m.answer(t(locale,"seller.form.stock"))

@router.message(ProductForm.stock)
async def pstock(m,state):
    locale=await locale_for(m.from_user.id)
    try: v=int(m.text); assert v>=0
    except: await m.answer(t(locale,"seller.form.invalid_stock")); return
    tok=await token_for(m.from_user.id)
    if not tok: await state.clear(); await m.answer(t(locale,"auth.required")); return
    d=await state.get_data()
    try:
        p=await backend.create_product(tok,{"name":d["name"],"price":d["price"],"stock":v})
        await m.answer(t(locale,"seller.created",id=p.get("id","—")),reply_markup=main_menu(locale))
    except BackendError: await m.answer(t(locale,"errors.backend"))
    await state.clear()

@router.callback_query(F.data=="seller:list")
async def plist(c):
    locale=await locale_for(c.from_user.id); tok=await token_for(c.from_user.id)
    if not tok: await c.message.answer(t(locale,"auth.required")); return
    try:
        d=await backend.products(tok); items=d.get("items",d if isinstance(d,list) else [])
        if not items: await c.message.answer(t(locale,"seller.empty")); return
        for p in items[:30]:
            await c.message.answer(t(locale,"seller.item",id=p.get("id","—"),name=p.get("name","—"),price=p.get("price","—"),stock=p.get("stock","—")),reply_markup=product_actions(locale,p.get("id")))
    except BackendError: await c.message.answer(t(locale,"errors.backend"))
    await c.answer()

@router.callback_query(F.data.startswith("product:delete:"))
async def pdelete(c):
    locale=await locale_for(c.from_user.id); tok=await token_for(c.from_user.id); pid=c.data.split(":")[2]
    try:
        await backend.delete_product(tok,pid); await c.message.edit_text(t(locale,"seller.deleted",id=pid))
    except BackendError: await c.message.answer(t(locale,"errors.backend"))
    await c.answer()

@router.callback_query(F.data.startswith("product:edit:"))
async def pedit(c,state):
    locale=await locale_for(c.from_user.id); pid=c.data.split(":")[2]
    await state.set_state(EditProductForm.value); await state.update_data(product_id=pid)
    await c.message.answer(t(locale,"seller.edit_prompt")); await c.answer()

@router.message(EditProductForm.value)
async def pedit_value(m,state):
    locale=await locale_for(m.from_user.id); tok=await token_for(m.from_user.id); d=await state.get_data()
    # Simple generic edit payload. Production UI can expose separate field buttons.
    try:
        await backend.update_product(tok,d["product_id"],{"name":m.text})
        await m.answer(t(locale,"seller.updated",id=d["product_id"]))
    except BackendError: await m.answer(t(locale,"errors.backend"))
    await state.clear()

@router.callback_query(F.data=="seller:moderation")
async def moderation(c):
    locale=await locale_for(c.from_user.id); tok=await token_for(c.from_user.id)
    try:
        d=await backend.products(tok); await c.message.answer(t(locale,"seller.moderation_info",data=str(d.get("moderation","—"))))
    except BackendError: await c.message.answer(t(locale,"errors.backend"))
    await c.answer()

@router.callback_query(F.data.startswith("order:view:"))
async def order_view(c):
    locale=await locale_for(c.from_user.id); tok=await token_for(c.from_user.id); oid=c.data.split(":")[2]
    try:
        o=await backend.order(tok,oid); d=o.get("delivery",{})
        await c.message.answer(t(locale,"orders.detail",id=o.get("id",oid),status=o.get("status","—"),tracking=d.get("tracking_number","—"),cargo=d.get("carrier","—"),location=d.get("location","—"),pvz=d.get("pickup_point","—"),eta=d.get("eta","—")))
    except BackendError: await c.message.answer(t(locale,"errors.backend"))
    await c.answer()

@router.callback_query(F.data=="wallet:operations")
async def wallet_ops(c):
    locale=await locale_for(c.from_user.id); tok=await token_for(c.from_user.id)
    try:
        d=await backend.wallet_operations(tok); items=d.get("items",[])
        if not items: await c.message.answer(t(locale,"wallet.empty"))
        else:
            for x in items[:30]: await c.message.answer(t(locale,"wallet.operation",type=x.get("type","—"),amount=x.get("amount","—"),fee=x.get("fee","—"),status=x.get("status","—"),date=x.get("created_at","—")))
    except BackendError: await c.message.answer(t(locale,"errors.backend"))
    await c.answer()

# Wallet text commands are intentionally explicit to avoid accidental money movements.
@router.message(F.text.regexp(r"^(Пополнить|Пополнить баланс|Пополнение)$"))
async def topup(m,state):
    locale=await locale_for(m.from_user.id); await state.set_state(WalletForm.amount); await state.update_data(action="topup"); await m.answer(t(locale,"wallet.amount"))

@router.message(F.text.regexp(r"^(Вывести|Вывод средств)$"))
async def withdraw(m,state):
    locale=await locale_for(m.from_user.id); await state.set_state(WalletForm.amount); await state.update_data(action="withdraw"); await m.answer(t(locale,"wallet.amount"))

@router.message(WalletForm.amount)
async def wallet_amount(m,state):
    locale=await locale_for(m.from_user.id); tok=await token_for(m.from_user.id); d=await state.get_data()
    try: amount=float(m.text.replace(",",".")); assert amount>0
    except: await m.answer(t(locale,"wallet.invalid_amount")); return
    try:
        if d["action"]=="topup": result=await backend.top_up(tok,amount)
        else: result=await backend.withdraw(tok,amount)
        await m.answer(t(locale,"wallet.requested",id=result.get("id","—"),status=result.get("status","—")))
    except BackendError: await m.answer(t(locale,"errors.backend"))
    await state.clear()

# Cooperation wizard
@router.message(CooperationForm.company)
async def coop_company(m,state): await state.update_data(company=m.text); await state.set_state(CooperationForm.type); await m.answer("Cargo / Logistics / Courier / Last Mile / PVZ?")
@router.message(CooperationForm.type)
async def coop_type(m,state): await state.update_data(type=m.text); await state.set_state(CooperationForm.geography); await m.answer("География работы:")
@router.message(CooperationForm.geography)
async def coop_geo(m,state): await state.update_data(geography=m.text); await state.set_state(CooperationForm.warehouses); await m.answer("Склады:")
@router.message(CooperationForm.warehouses)
async def coop_wh(m,state): await state.update_data(warehouses=m.text); await state.set_state(CooperationForm.branches); await m.answer("Филиалы:")
@router.message(CooperationForm.branches)
async def coop_br(m,state): await state.update_data(branches=m.text); await state.set_state(CooperationForm.pvz); await m.answer("ПВЗ:")
@router.message(CooperationForm.pvz)
async def coop_pvz(m,state): await state.update_data(pvz=m.text); await state.set_state(CooperationForm.tariffs); await m.answer("Тарифы:")
@router.message(CooperationForm.tariffs)
async def coop_tar(m,state): await state.update_data(tariffs=m.text); await state.set_state(CooperationForm.api); await m.answer("API:")
@router.message(CooperationForm.api)
async def coop_api(m,state): await state.update_data(api=m.text); await state.set_state(CooperationForm.tracking); await m.answer("Tracking:")
@router.message(CooperationForm.tracking)
async def coop_tracking(m,state): await state.update_data(tracking=m.text); await state.set_state(CooperationForm.webhook); await m.answer("Webhook:")
@router.message(CooperationForm.webhook)
async def coop_webhook(m,state): await state.update_data(webhook=m.text); await state.set_state(CooperationForm.documents); await m.answer("Документы (ссылки/ID файлов):")
@router.message(CooperationForm.documents)
async def coop_documents(m,state):
    locale=await locale_for(m.from_user.id); tok=await token_for(m.from_user.id); d=await state.get_data(); d["documents"]=m.text
    try:
        r=await backend.cooperation_create(tok,d)
        await m.answer(t(locale,"cooperation.created",id=r.get("id","—"),status=r.get("status","—")),reply_markup=main_menu(locale))
    except BackendError: await m.answer(t(locale,"errors.backend"))
    await state.clear()
