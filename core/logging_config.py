import logging
import sys
from tools.config import LOGGING

def setup_logging():
    logger = logging.getLogger("wallet")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    match LOGGING:
        case "1":
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        case "2":
            file_handler = logging.FileHandler("app.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        case "3":
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            file_handler = logging.FileHandler("app.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    return logger

logger = setup_logging()