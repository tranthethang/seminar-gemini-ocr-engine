from app.services.ocr.base import OCREngine

class OCREngineFactory:
    @staticmethod
    def get_engine(engine_type: str = "gemini") -> OCREngine:
        if engine_type == "gemini":
            from app.services.ocr.gemini import GeminiOCREngine
            return GeminiOCREngine()
        else:
            raise ValueError(f"Unknown OCR engine type: {engine_type}")
