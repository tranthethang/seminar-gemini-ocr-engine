# Seminar Gemini OCR Engine Repository Overview

This document provides a technical overview of the `seminar-gemini-ocr-engine` repository.

## 1. Project Description
An intelligent OCR engine designed to extract structured information (JSON) from business cards. It leverages OpenCV for image preprocessing (boundary detection, perspective correction) and Google's Gemini Generative AI for text extraction.

## 2. Project Structure

```text
seminar-gemini-ocr-engine/
├── main.py                     # Application entry point & orchestration
├── utils/
│   └── image_processor.py      # Computer vision logic (OpenCV)
├── prompt.md                   # System prompt for Gemini API
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # General project documentation
└── repo.md                     # Repository technical overview (this file)
```

## 3. Key Files & Components

### `main.py`
The main execution script that orchestrates the entire workflow.
- **Initialization**: Loads environment variables and initializes the Gemini client (`google-genai`).
- **Parallel Processing**: Uses `ThreadPoolExecutor` to process multiple images concurrently.
- **Workflow**:
    1.  **Image Processing**: Calls `utils.image_processor.process_card` to clean and crop the image.
    2.  **API Call**: Sends the processed image (or original as fallback) + `prompt.md` content to the Gemini API.
    3.  **Fallback Mechanism**: If the AI fails to extract a name from the processed image, it retries with the original raw image.
    4.  **Output**: Prints JSON results to stdout and logs to `app.log`.

### `utils/image_processor.py`
Handles all computer vision tasks using OpenCV (`cv2`) and `imutils`.
- **`process_card(image_path, output_path)`**:
    -   Resizes the image for consistent processing.
    -   Converts to grayscale, blurs, and applies Canny edge detection.
    -   Finds contours to detect the business card boundary (looks for a 4-point polygon).
    -   Applies a **4-point perspective transform** to crop and "flatten" the card (top-down view).
    -   Saves the processed image to the `tmp/` directory.

### `prompt.md`
Contains the natural language prompt sent to the Gemini model. It instructs the model to:
-   Analyze the business card image.
-   Extract specific fields: `company_name`, `person_name`, `position`, `contact`, `address`.
-   Return the result in strictly formatted JSON.

### Configuration
-   **`requirements.txt`**: Lists dependencies, including `google-genai`, `opencv-python`, `imutils`, `python-dotenv`, and `loguru`.
-   **`.env`**: Stores the `GEMINI_API_KEY` and `GEMINI_MODEL` configuration (not committed to repo).

## 4. Dependencies
Key libraries used in this project:
-   **`google-genai`**: Client for Google's Gemini API.
-   **`opencv-python` (cv2)**: Image processing and computer vision.
-   **`imutils`**: Helper functions for image processing (resizing, contours).
-   **`loguru`**: Enhanced logging.
-   **`python-dotenv`**: Environment variable management.
