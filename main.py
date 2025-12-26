from google import genai
from google.genai import types
import PIL.Image
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv
from utils.image_processor import process_card

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
        with PIL.Image.open(image_path) as img_pil:
            # Resize image if width > 500px
            if img_pil.width > 500:
                new_width = 500
                new_height = int(img_pil.height * (new_width / img_pil.width))
                img_pil = img_pil.resize((new_width, new_height), PIL.Image.Resampling.LANCZOS)
                img_pil.save(image_path)
                logger.info(f"Resized {image_path} to width 500px")
            
            # Re-read or use the current img_pil for API
            # Since img_pil might be modified, we use it directly
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
    except Exception as e:
        logger.error(f"Could not open or resize image {image_path}: {e}")
        return None


def process_image_task(img_path, tmp_dir):
    logger.info(f"--- Processing {img_path.name} started at {time.strftime('%H:%M:%S')} ---")
    img_start_time = time.time()

    # 1. Process image (detect card and perspective transform)
    process_start = time.time()
    processed_img_path = tmp_dir / f"processed_{img_path.name}"
    process_card(str(img_path), str(processed_img_path))
    process_end = time.time()
    process_duration = process_end - process_start
    logger.info(f"Xử lý ảnh từ {time.strftime('%H:%M:%S', time.localtime(process_start))} tới {time.strftime('%H:%M:%S', time.localtime(process_end))} tổng {process_duration:.2f} giây")
    
    # 2. Extract info using processed image
    api_start = time.time()
    result = extract_card_info(processed_img_path)
    
    # Retry logic: if person_name is null, retry with original image
    if result and result.get("person_name") is None:
        logger.info(f"person_name is null for {img_path.name}, retrying with original image...")
        result = extract_card_info(img_path)
        
    api_end = time.time()
    api_duration = api_end - api_start
    logger.info(f"Send Gemini API từ {time.strftime('%H:%M:%S', time.localtime(api_start))} tới {time.strftime('%H:%M:%S', time.localtime(api_end))} tổng {api_duration:.2f} giây")

    if result:
        print(f"--- Result for {img_path.name} ---")
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        logger.error(f"Failed to extract info from {img_path}")
    
    img_end_time = time.time()
    logger.info(f"--- Kết thúc lúc {time.strftime('%H:%M:%S', time.localtime(img_end_time))} (Tổng cộng: {img_end_time - img_start_time:.2f} giây) ---")
    return result


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

    # Create tmp directory if it doesn't exist
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Parallel processing using ThreadPoolExecutor
    max_workers = min(len(image_files), 10)  # Adjust based on API limits and local resources
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda p: process_image_task(p, tmp_dir), image_files)



if __name__ == "__main__":
    main()
