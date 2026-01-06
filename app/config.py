import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Ollama Config
    ENGINE_TYPE = os.getenv("ENGINE_TYPE", "gemini")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

    LOG_FILE = "app.log"
    PROMPT_FILE = Path("prompt.md")
    SAMPLE_DATA_DIR = Path("sample_data")
    TMP_DIR = Path("tmp")
    
    # Langfuse Config
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    @staticmethod
    def validate():
        if Config.ENGINE_TYPE == "gemini":
            if not Config.GEMINI_API_KEY:
                raise ValueError("API Key not found. Please set GEMINI_API_KEY in .env file for Gemini engine")
        elif Config.ENGINE_TYPE == "ollama":
            if not Config.OLLAMA_BASE_URL:
                raise ValueError("Ollama Base URL not found. Please set OLLAMA_BASE_URL in .env file")

