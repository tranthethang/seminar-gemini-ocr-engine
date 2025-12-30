import sys
import os
from pathlib import Path
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ocr.ollama import OllamaOCREngine
from app.config import Config

def main():
    print(f"Testing Ollama OCR with {Config.OLLAMA_MODEL} at {Config.OLLAMA_BASE_URL}")
    
    engine = OllamaOCREngine()
    
    image_path = Path("sample_data/card-01.jpg")
    if not image_path.exists():
        print(f"Error: {image_path} does not exist")
        return

    print(f"Processing {image_path}...")
    result = engine.extract_info(image_path)
    
    if result:
        print("\nSuccess! Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("\nFailed to extract info.")

if __name__ == "__main__":
    main()
