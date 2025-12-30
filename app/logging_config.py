from loguru import logger
from app.config import Config

def setup_logging():
    logger.add(Config.LOG_FILE, rotation="500 MB", level="INFO")
