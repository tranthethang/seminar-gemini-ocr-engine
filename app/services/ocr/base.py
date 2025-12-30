from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

class OCREngine(ABC):
    @abstractmethod
    def extract_info(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract information from the image.
        
        Args:
            image_path (Path): Path to the image file.
            
        Returns:
            Optional[Dict[str, Any]]: Extracted data as a dictionary, or None if failed.
        """
        pass
