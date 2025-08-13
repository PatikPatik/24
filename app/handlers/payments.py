from __future__ import annotations
import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from ..settings import settings
from ..services.ton import ton_deeplink, to_nanotons, tonapi_find_payment
from ..services.timeutils import utcnow

@dataclass
class Invoice:
    code: str
    chat_id: int
    amount_ton: float
    amount_nanoton: int
    created_at: float
    expires_at_ts: float
    paid: bool = False
    tx_hash: str | None = None
    from_address: str | None = None

INVOICES: Dict[str, Invoice] = {}

def _gen_code() -> str:
    return secrets.token_hex(3).upper()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Жми /pay, чтобы создать счёт на оплату TON.")

async def cmd_pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    amount_ton = float(settings.TON_MIN_AMOUNT)
    code = _gen_code()

    invoice = Invoice(
        code=code,
        chat_id=chat_id,
        amount_ton=amount_ton,
        amount_nanoton=to_nanotons(amount_ton),
        created_at=utcnow().timestamp(),
        expires_at_ts=(utcnow() + timedelta(seconds=settings.TON_INVOICE_TTL)).timestamp(),
    )
    INVOICES[code] = invoice

    link = ton_deeplink(settings.TON_WALLET, amount_ton, code)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Оплатить в Tonkeeper", url=link)],
        [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check:{code}")]
    ])

    text = (
        f"💳 Счёт на оплату: <b>{amount_ton:.3f} TON</b>\n"
        f"👛 Адрес: <code>{settings.TON_WALLET}</code>\n"
        f"📝 Комментарий: <code>{code}</code>\n\n"
        f"Важно: переведи ровно сумму и <b>не меняй</b> комментарий. "
        f"Счёт активен {settings.TON_INVOICE_TTL//60} мин."
    )
    await update.effective_message.reply_text(text, reply_markup=kb, parse_mode="HTML")

async def cb_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _, code = (query.data or "").split(":", 1)
    inv = INVOICES.get(code)
    if not inv:
        await query.edit_message_text("Счёт не найден или истёк.")
        return
    await query.edit_message_text("Идёт проверка платежа…")
    from datetime import timedelta
    since = utcnow() - timedelta(seconds=settings.TON_INVOICE_TTL + 60)
    res = await tonapi_find_payment(code, inv.amount_nanoton, since)
    if res.ok:
        inv.paid = True
        inv.tx_hash = res.tx_hash
        inv.from_address = res.from_address
        await context.bot.send_message(inv.chat_id,
            f"✅ Оплата найдена!\nTx: <code>{res.tx_hash or 'unknown'}</code>",
            parse_mode="HTML")
    else:
        await context.bot.send_message(inv.chat_id, "Пока не вижу поступления. Попробуй через минуту ещё раз.")

def register_payment_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("pay", cmd_pay))
    app.add_handler(CallbackQueryHandler(cb_check, pattern=r"^check:"))
