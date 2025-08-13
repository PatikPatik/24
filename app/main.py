from __future__ import annotations
import logging
from telegram.ext import ApplicationBuilder, AIORateLimiter
from .settings import settings
from .logging_config import setup_logging
from .handlers.payments import register_payment_handlers

logger = logging.getLogger(__name__)

def run() -> None:
    setup_logging()

    application = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    register_payment_handlers(application)

    # В PTB 22 run_polling() сам позаботится о цикле; 
    # он также удаляет вебхук при старте.
    logger.info("Starting bot in POLLING mode")
    application.run_polling(allowed_updates=None)
