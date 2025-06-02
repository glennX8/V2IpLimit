"""
This module sets up the logging configuration for the application.
It configures a rotating file handler and a stream handler for the root logger.
"""

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "app.log", maxBytes=7 * 10**6, backupCount=3
)  # 7MB per file, keep 3 old files
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Prevent adding duplicate handlers if this module is re-imported
if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
    logger.addHandler(file_handler)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(stream_handler)
