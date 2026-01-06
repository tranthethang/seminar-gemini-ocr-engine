from langfuse import Langfuse
from loguru import logger
from app.config import Config

class LangfuseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.client = Langfuse(
                public_key=Config.LANGFUSE_PUBLIC_KEY,
                secret_key=Config.LANGFUSE_SECRET_KEY,
                host=Config.LANGFUSE_HOST
            )
            logger.info("Langfuse client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse client: {e}")
            self.client = None

    def get_client(self):
        return self.client

    def flush(self):
        if self.client:
            self.client.flush()

langfuse_manager = LangfuseManager()
