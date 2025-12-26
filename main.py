from google import genai
from google.genai import types
import PIL.Image
import json
import os
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Setup logging
log_file = "app.log"
logger.add(log_file, rotation="500 MB", level="INFO")

# 1. Initialize Client with your API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("API Key not found. Please set GEMINI_API_KEY in .env file")
    raise ValueError("API Key not found. Please set GEMINI_API_KEY in .env file")
client = genai.Client(api_key=api_key)


def extract_card_info(image_path):
    try:
        img_pil = PIL.Image.open(image_path)
    except Exception as e:
        logger.error(f"Could not open image {image_path}: {e}")
        return None

    try:
        with open("prompt.md", "r", encoding="utf-8") as f:
            prompt_text = f.read()
    except FileNotFoundError:
        logger.error("File prompt.md not found")
        return None

    model_id = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    logger.info(f"Sending request to Gemini model: {model_id} for {image_path}")
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt_text, img_pil],
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


def main():
    sample_dir = Path("sample_data")
    if not sample_dir.exists():
        logger.error(f"Directory {sample_dir} does not exist")
        return

    # Supported image extensions
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    image_files = []
    for ext in extensions:
        image_files.extend(sample_dir.glob(ext))

    if not image_files:
        logger.info("No images found in sample_data")
        return

    logger.info(f"Found {len(image_files)} images to process")

    for img_path in image_files:
        result = extract_card_info(img_path)
        if result:
            print(f"--- Result for {img_path.name} ---")
            print(json.dumps(result, indent=4, ensure_ascii=False))
        else:
            logger.error(f"Failed to extract info from {img_path}")


if __name__ == "__main__":
    main()
