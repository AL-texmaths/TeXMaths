from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


LOG_DIR = Path("assistant/logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

formatter = logging.Formatter(
    fmt="""%(asctime)s | %(levelname)-8s |
     %(threadName)s | %(name)s | %(message)s
    """,
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5*1024*1024,
    backupCount=5,
    encoding="utf8"
)

handler.setFormatter(formatter)

logger = logging.getLogger("AssistantDeProgression")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def logger_wraper(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return wrapper