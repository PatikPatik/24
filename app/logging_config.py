from __future__ import annotations
import logging
import os
from pythonjsonlogger import jsonlogger  # <-- ВАЖНО: pythonjsonlogger, не python_json_logger

def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(fmt)

    root.handlers.clear()
    root.addHandler(handler)
