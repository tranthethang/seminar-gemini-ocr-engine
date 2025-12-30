import time
import json
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any

from app.image_processor import process_card
from app.services.ocr.factory import OCREngineFactory
from app.config import Config

class ImageProcessingPipeline:
    def __init__(self, ocr_engine_type: Optional[str] = None):
        if ocr_engine_type is None:
            ocr_engine_type = Config.ENGINE_TYPE
        self.ocr_engine = OCREngineFactory.get_engine(ocr_engine_type)
        self.tmp_dir = Config.TMP_DIR
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, img_path: Path) -> Optional[Dict[str, Any]]:
        logger.info(f"--- Processing {img_path.name} started at {time.strftime('%H:%M:%S')} ---")
        img_start_time = time.time()

        # 1. Process image (detect card and perspective transform)
        process_start = time.time()
        processed_img_path = self.tmp_dir / f"processed_{img_path.name}"
        
        # process_card expects string paths
        process_card(str(img_path), str(processed_img_path))
        
        process_end = time.time()
        process_duration = process_end - process_start
        logger.info(f"Image processing (pre-processing) took {process_duration:.2f} seconds")
        
        # 2. Extract info using processed image
        api_start = time.time()
        result = self.ocr_engine.extract_info(processed_img_path)
        
        # Retry logic: if person_name is null, retry with original image
        if result and result.get("person_name") is None:
            logger.info(f"person_name is null for {img_path.name}, retrying with original image...")
            result = self.ocr_engine.extract_info(img_path)
            
        api_end = time.time()
        api_duration = api_end - api_start
        logger.info(f"OCR Extraction took {api_duration:.2f} seconds")

        if result:
            logger.info(f"--- Result for {img_path.name} extracted successfully ---")
        else:
            logger.error(f"Failed to extract info from {img_path}")
        
        img_end_time = time.time()
        logger.info(f"--- Finished {img_path.name} at {time.strftime('%H:%M:%S')} (Total: {img_end_time - img_start_time:.2f}s) ---")
        return result
