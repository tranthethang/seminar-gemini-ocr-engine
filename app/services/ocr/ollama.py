from typing import Optional, Dict, Any
from pathlib import Path
import base64
import json
import requests
import PIL.Image
from loguru import logger

from app.services.ocr.base import OCREngine
from app.config import Config

class OllamaOCREngine(OCREngine):
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self._load_prompt()

    def _load_prompt(self):
        try:
            with open(Config.PROMPT_FILE, "r", encoding="utf-8") as f:
                self.prompt_text = f.read()
        except FileNotFoundError:
            logger.error(f"File {Config.PROMPT_FILE} not found")
            self.prompt_text = ""

    def extract_info(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract information from the image using Ollama.
        """
        if not self.prompt_text:
            logger.error("Prompt text is empty. Cannot process.")
            return None

        try:
            # 1. Resize and prepare image
            with PIL.Image.open(image_path) as img_pil:
                # Resize logic (consistent with Gemini implementation)
                if img_pil.width > 1024:
                    new_width = 1024
                    new_height = int(img_pil.height * (new_width / img_pil.width))
                    img_pil = img_pil.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
                    img_pil.save(image_path)
                    logger.info(f"Resized {image_path} to width 1024px")
                
                # Encode to base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # 2. Prepare Request
            url = f"{self.base_url}/api/chat"
            system_msg = (
                "You are a strict OCR engine. Extract text EXACTLY as shown in the image. "
                "DO NOT use internal knowledge. DO NOT invent data. "
                "If a field is not visible, set it to null. "
                "Return ONLY a JSON object."
            )
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_msg
                    },
                    {
                        "role": "user",
                        "content": self.prompt_text,
                        "images": [base64_image]
                    }
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "num_predict": 1024,
                    "top_k": 1,
                    "top_p": 0.1
                }
            }

            logger.info(f"Sending request to Ollama ({self.base_url}) model: {self.model} for {image_path}")
            
            # 3. Send Request
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            # 4. Parse Response
            result = response.json()
            content = result.get("message", {}).get("content", "{}")
            
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Ollama response: {content}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error during Ollama processing: {e}")
            return None
