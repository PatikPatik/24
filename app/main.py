from __future__ import annotations
import asyncio
import logging
from telegram.ext import Application, ApplicationBuilder, AIORateLimiter
from .settings import settings
from .logging_config import setup_logging
from .handlers.payments import register_payment_handlers

logger = logging.getLogger(__name__)

async def run() -> None:
    setup_logging()

    application: Application = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    register_payment_handlers(application)

    if settings.MODE.lower() == "polling":
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        logger.info("Starting bot in POLLING mode")
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=None)
        await application.updater.wait_until_closed()
        await application.stop()
    else:
        raise RuntimeError("Set MODE=polling for this build.")

if __name__ == "__main__":
    asyncio.run(run())
