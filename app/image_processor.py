import cv2
import imutils
from imutils.perspective import four_point_transform
import numpy as np
from loguru import logger
from pathlib import Path

def process_card(image_path: str, output_path: str) -> str:
    """
    Detects the card in the image, applies perspective transform,
    and saves the result to output_path.
    Returns the path to the processed image.
    """
    logger.info(f"Processing image: {image_path}")
    
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Failed to load image: {image_path}")
        return image_path

    orig = image.copy()
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)

    # Convert to grayscale, blur it, and find edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    # Find contours in the edged image
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None

    # Loop over the contours
    for c in cnts:
        # Approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # If our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    # If no 4-point contour is found, return the original image path (or handle differently)
    if screenCnt is None:
        logger.warning(f"Could not find 4-point contour for {image_path}. Saving original.")
        cv2.imwrite(output_path, orig)
        return output_path

    # Apply the four point perspective transform to obtain a top-down view of the card
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Save the warped image
    cv2.imwrite(output_path, warped)
    logger.info(f"Saved processed image to: {output_path}")

    return output_path
