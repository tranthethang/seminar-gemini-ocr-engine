from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from pathlib import Path

from app.config import Config
from app.pipeline import ImageProcessingPipeline

class Runner:
    def __init__(self):
        self.pipeline = ImageProcessingPipeline()
        self.sample_dir = Config.SAMPLE_DATA_DIR

    def run(self):
        if not self.sample_dir.exists():
            logger.error(f"Directory {self.sample_dir} does not exist")
            return

        # Supported image extensions
        extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
        image_files = []
        for ext in extensions:
            image_files.extend(self.sample_dir.glob(ext))

        if not image_files:
            logger.info("No images found in sample_data")
            return

        logger.info(f"Found {len(image_files)} images to process")

        # Create tmp directory if it doesn't exist
        Config.TMP_DIR.mkdir(parents=True, exist_ok=True)

        # Parallel processing using ThreadPoolExecutor
        max_workers = min(len(image_files), 10)  # Adjust based on API limits and local resources
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.pipeline.process_image, image_files)
