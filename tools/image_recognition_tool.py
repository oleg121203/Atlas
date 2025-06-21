"""
Image Recognition Tool for Atlas

This module provides functionality for image recognition tasks, such as template matching
and object detection on screenshots, using OpenCV.
"""
#Try to import cv2 safely for headless environments or missing dependencies
try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from typing import Optional, Tuple

from utils.logger import get_logger

logger = get_logger()

def find_template_in_image(template_path: str, image_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    Find a template image within a larger image using template matching.
    
    Args:
        template_path (str): Path to the template image file.
        image_path (str): Path to the larger image file to search in.
        threshold (float): Matching threshold (0.0 to 1.0). Higher values mean stricter matching.
    
    Returns:
        Optional[Tuple[int, int]]: Top-left coordinates (x, y) of the matched template if found, None otherwise.
    """
    if not _CV2_AVAILABLE:
        logger.error("OpenCV (cv2) is not available. Cannot perform image recognition.")
        return None
        
    try:
        #Read images
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if template is None or image is None:
            logger.error(f"Failed to load images: template={template_path}, image={image_path}")
            return None
        
        #Perform template matching
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            logger.info(f"Template found at {max_loc} with confidence {max_val}")
            return max_loc
        else:
            logger.info(f"No match found above threshold {threshold}. Best match confidence: {max_val}")
            return None
    except Exception as e:
        logger.error(f"Error in template matching: {str(e)}")
        return None

def find_object_in_image(image_path: str, object_cascade_path: str) -> list:
    """
    Detect objects in an image using a pre-trained Haar or LBP cascade classifier.
    
    Args:
        image_path (str): Path to the image file.
        object_cascade_path (str): Path to the cascade classifier XML file.
    
    Returns:
        list: List of rectangles (x, y, w, h) where objects were detected.
    """
    if not _CV2_AVAILABLE:
        logger.error("OpenCV (cv2) is not available. Cannot perform object detection.")
        return []
        
    try:
        #Load image and cascade classifier
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(object_cascade_path)
        if cascade.empty():
            logger.error(f"Failed to load cascade classifier: {object_cascade_path}")
            return []
        
        #Detect objects
        objects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        logger.info(f"Found {len(objects)} objects in image")
        return objects.tolist()
    except Exception as e:
        logger.error(f"Error in object detection: {str(e)}")
        return []
