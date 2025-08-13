from __future__ import annotations
import logging
import os
from python_json_logger import jsonlogger

def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(fmt)
    logger.handlers.clear()
    logger.addHandler(handler)
