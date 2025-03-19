# logging.py
import logging
from logging.handlers import RotatingFileHandler

from .config import LOG_FILE, LOG_LEVEL

logger: logging.Logger = logging.getLogger("app_logger")
logger.setLevel(LOG_LEVEL)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = RotatingFileHandler(LOG_FILE, maxBytes=20 * 1024 * 1024, backupCount=5)
fh.setFormatter(formatter)
logger.addHandler(fh)
