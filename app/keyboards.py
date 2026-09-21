from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from app.i18n import t

def main_menu(locale):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(locale,"menu.seller")), KeyboardButton(text=t(locale,"menu.orders"))],
        [KeyboardButton(text=t(locale,"menu.wallet")), KeyboardButton(text=t(locale,"menu.team"))],
        [KeyboardButton(text=t(locale,"menu.status")), KeyboardButton(text=t(locale,"menu.cooperation"))],
        [KeyboardButton(text=t(locale,"menu.notifications")), KeyboardButton(text=t(locale,"menu.language"))],
        [KeyboardButton(text=t(locale,"menu.help"))]
    ], resize_keyboard=True)

def languages():
    names={"ru":"Русский","ky":"Кыргызча","kk":"Қазақша","uz":"O‘zbekcha","tg":"Тоҷикӣ"}
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=v, callback_data=f"lang:{k}") for k,v in [("ru",names["ru"]),("ky",names["ky"])]],
        [InlineKeyboardButton(text=v, callback_data=f"lang:{k}") for k,v in [("kk",names["kk"]),("uz",names["uz"]),("tg",names["tg"])]]
    ])

def seller_menu(locale):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(locale,"seller.add"),callback_data="seller:add")],
        [InlineKeyboardButton(text=t(locale,"seller.list"),callback_data="seller:list")],
        [InlineKeyboardButton(text=t(locale,"seller.moderation"),callback_data="seller:moderation")]
    ])

def product_actions(locale, product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(locale,"seller.edit"),callback_data=f"product:edit:{product_id}")],
        [InlineKeyboardButton(text=t(locale,"seller.delete"),callback_data=f"product:delete:{product_id}")],
        [InlineKeyboardButton(text=t(locale,"common.back"),callback_data="seller:list")]
    ])

def order_actions(locale, order_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(locale,"orders.details"),callback_data=f"order:view:{order_id}")]
    ])

def back(locale, cb="menu:main"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(locale,"common.back"),callback_data=cb)]])
