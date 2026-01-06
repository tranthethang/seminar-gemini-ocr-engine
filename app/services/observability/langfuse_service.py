from langfuse import Langfuse
from loguru import logger
from litellm import completion_cost
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

    def log_cost(self, model: str, prompt_tokens: int, completion_tokens: int):
        try:
            # LiteLLM expects model name in a specific format if not standard
            # For Gemini, it's usually just the model name or gemini/model-name
            # We'll try to prepend 'gemini/' if it's not already there for Gemini models
            litellm_model = model
            if "gemini" in model.lower() and not model.lower().startswith("gemini/"):
                litellm_model = f"gemini/{model}"
            
            # Construct a dummy response object for LiteLLM to calculate cost
            dummy_response = {
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens
                }
            }
            
            cost = completion_cost(
                model=litellm_model,
                completion_response=dummy_response
            )
            
            if cost is not None:
                logger.info(f"Estimated Cost for {model}: ${cost:.6f}")
            else:
                logger.warning(f"Could not calculate cost for model: {model}")
            return cost
        except Exception as e:
            logger.error(f"Error calculating cost with litellm: {e}")
            return None

langfuse_manager = LangfuseManager()
