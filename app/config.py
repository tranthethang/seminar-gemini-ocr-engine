import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    LOG_FILE = "app.log"
    PROMPT_FILE = Path("prompt.md")
    SAMPLE_DATA_DIR = Path("sample_data")
    TMP_DIR = Path("tmp")
    
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise ValueError("API Key not found. Please set GEMINI_API_KEY in .env file")
