from google import genai
from google.genai import types
import PIL.Image
import json
from loguru import logger
from pathlib import Path
from typing import Optional, Dict, Any

from app.config import Config
from app.services.ocr.base import OCREngine

class GeminiOCREngine(OCREngine):
    def __init__(self):
        if not Config.GEMINI_API_KEY:
             raise ValueError("API Key not found")
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = Config.GEMINI_MODEL
        self._load_prompt()

    def _load_prompt(self):
        try:
            with open(Config.PROMPT_FILE, "r", encoding="utf-8") as f:
                self.prompt_text = f.read()
        except FileNotFoundError:
            logger.error(f"File {Config.PROMPT_FILE} not found")
            self.prompt_text = ""

    def extract_info(self, image_path: Path) -> Optional[Dict[str, Any]]:
        if not self.prompt_text:
             logger.error("Prompt text is empty. Cannot process.")
             return None
             
        try:
            with PIL.Image.open(image_path) as img_pil:
                # Resize logic
                if img_pil.width > 500:
                    new_width = 500
                    new_height = int(img_pil.height * (new_width / img_pil.width))
                    img_pil = img_pil.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
                    # Note: Original code saves the resized image back to disk. 
                    img_pil.save(image_path)
                    logger.info(f"Resized {image_path} to width 500px")
                
                logger.info(f"Sending request to Gemini model: {self.model_id} for {image_path}")
                
                try:
                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=[self.prompt_text, img_pil],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.1
                        )
                    )
                    data = json.loads(response.text)
                    return data
                except Exception as e:
                    logger.exception(f"Error during Gemini API call or JSON parsing: {e}")
                    return None
        except Exception as e:
            logger.error(f"Could not open or resize image {image_path}: {e}")
            return None
