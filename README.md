# Telegram Bot (Polling) + TON payments (TonAPI polling)

## Quick start (Render)
1. Upload this zip or connect repo.
2. Set **Start Command**: `python -m app`.
3. Add Environment variables:
```
MODE=polling
ENV=prod
BOT_TOKEN=<your_token>
TON_WALLET=<your_ton_address>
TON_MIN_AMOUNT=0.1
TON_INVOICE_TTL=900
TON_POLL_INTERVAL=5
TONAPI_BASE=https://tonapi.io/v2
TONAPI_KEY=
```
4. (Once) Reset Telegram webhook in a browser:
   `https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook?drop_pending_updates=true`
5. Deploy. In Telegram, send `/pay`.

## Commands
- `/pay` — create invoice (0.1 TON by default).
