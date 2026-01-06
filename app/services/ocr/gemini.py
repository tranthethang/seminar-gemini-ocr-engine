from google import genai
from google.genai import types
import PIL.Image
import json
from loguru import logger
from pathlib import Path
from typing import Optional, Dict, Any

from app.config import Config
from app.services.ocr.base import OCREngine
from app.services.observability.langfuse_service import langfuse_manager

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
             
        langfuse_client = langfuse_manager.get_client()
        
        # Using context managers as in the example provided by user
        if langfuse_client:
            try:
                with langfuse_client.start_as_current_observation(as_type="span", name="ocr-process", input={"image_path": str(image_path)}) as root_span:
                    try:
                        with PIL.Image.open(image_path) as img_pil:
                            # Resize logic
                            if img_pil.width > 1024:
                                new_width = 1024
                                new_height = int(img_pil.height * (new_width / img_pil.width))
                                img_pil = img_pil.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
                                # Note: Original code saves the resized image back to disk. 
                                img_pil.save(image_path)
                                logger.info(f"Resized {image_path} to width 1024px")
                            
                            logger.info(f"Sending request to Gemini model: {self.model_id} for {image_path}")
                            
                            # Start a generation for the LLM call
                            with langfuse_client.start_as_current_observation(
                                as_type="generation", 
                                name="gemini-generation", 
                                model=self.model_id,
                                input=self.prompt_text
                            ) as generation:
                                try:
                                    response = self.client.models.generate_content(
                                        model=self.model_id,
                                        contents=[self.prompt_text, img_pil],
                                        config=types.GenerateContentConfig(
                                            response_mime_type="application/json",
                                            temperature=0.0
                                        )
                                    )
                                    data = json.loads(response.text)
                                    
                                    # Extract usage metadata for Langfuse
                                    usage = response.usage_metadata
                                    logger.info(f"Gemini Usage: prompt={usage.prompt_token_count}, candidates={usage.candidates_token_count}, total={usage.total_token_count}")
                                    
                                    # Calculate and log cost using litellm
                                    langfuse_manager.log_cost(
                                        model=self.model_id,
                                        prompt_tokens=usage.prompt_token_count,
                                        completion_tokens=usage.candidates_token_count
                                    )
                                    
                                    # Use multiple keys to ensure compatibility with different Langfuse versions
                                    langfuse_usage = {
                                        "input": usage.prompt_token_count,
                                        "output": usage.candidates_token_count,
                                        "total": usage.total_token_count,
                                        "input_tokens": usage.prompt_token_count,
                                        "output_tokens": usage.candidates_token_count,
                                        "total_tokens": usage.total_token_count
                                    }
                                    
                                    generation.update(
                                        output=data,
                                        usage=langfuse_usage
                                    )
                                    root_span.update(output=data)
                                        
                                    return data
                                except Exception as e:
                                    logger.exception(f"Error during Gemini API call or JSON parsing: {e}")
                                    generation.update(level="ERROR", status_message=str(e))
                                    root_span.update(level="ERROR", status_message=str(e))
                                    return None
                    except Exception as e:
                        logger.error(f"Could not open or resize image {image_path}: {e}")
                        root_span.update(level="ERROR", status_message=str(e))
                        return None
            finally:
                langfuse_manager.flush()
        else:
            # Fallback if langfuse is not available
            try:
                with PIL.Image.open(image_path) as img_pil:
                    if img_pil.width > 1024:
                        new_width = 1024
                        new_height = int(img_pil.height * (new_width / img_pil.width))
                        img_pil = img_pil.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
                        img_pil.save(image_path)
                        logger.info(f"Resized {image_path} to width 1024px")
                    
                    logger.info(f"Sending request to Gemini model: {self.model_id} for {image_path}")
                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=[self.prompt_text, img_pil],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.0
                        )
                    )
                    return json.loads(response.text)
            except Exception as e:
                logger.error(f"Error without Langfuse: {e}")
                return None
