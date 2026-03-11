"""
Simple OCR Wrapper using Pytesseract
Minimal dependencies, clean interface
"""

import logging
import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Try to import Pytesseract
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
    logger.info("[SIMPLE-OCR] ✅ Pytesseract available")
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("[SIMPLE-OCR] ⚠️ Pytesseract not available")


class SimpleOCR:
    """Simple OCR using Pytesseract with minimal overhead."""
    
    def __init__(self):
        """Initialize simple OCR."""
        self.available = TESSERACT_AVAILABLE
        
    def extract_all_text(self, image: np.ndarray) -> List[Dict]:
        """
        Extract all text regions from image.
        
        Args:
            image: OpenCV image array (BGR format)
            
        Returns:
            List of text regions with text, position, and confidence
        """
        if not self.available:
            logger.warning("[SIMPLE-OCR] Pytesseract not available, returning empty")
            return []
        
        try:
            # Extract text data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > 30 and text:  # Only keep confident text
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    text_regions.append({
                        'text': text,
                        'confidence': conf,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'bbox': (x, y, w, h)
                    })
            
            logger.info(f"[SIMPLE-OCR] Extracted {len(text_regions)} text regions")
            return text_regions
            
        except Exception as e:
            logger.error(f"[SIMPLE-OCR] Error: {e}")
            return []
    
    def extract_text_from_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Extract text from specific region.
        
        Args:
            image: OpenCV image array
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Dict with text and confidence
        """
        if not self.available:
            return {'text': '', 'confidence': 0}
        
        try:
            x, y, w, h = bbox
            roi = image[y:y+h, x:x+w]
            
            text = pytesseract.image_to_string(roi).strip()
            
            # Get confidence (average of all words)
            try:
                data = pytesseract.image_to_data(roi, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data['conf'] if int(c) > 0]
                avg_conf = sum(confidences) // len(confidences) if confidences else 0
            except:
                avg_conf = 50
            
            return {
                'text': text,
                'confidence': avg_conf
            }
            
        except Exception as e:
            logger.error(f"[SIMPLE-OCR] Error extracting from region: {e}")
            return {'text': '', 'confidence': 0}
    
    def find_text_near_element(self, element: Dict, all_text_regions: List[Dict], 
                               max_distance: int = 50) -> Optional[Dict]:
        """Find text label near an element."""
        elem_center_x = element.get('center_x', element['x'] + element['width'] // 2)
        elem_center_y = element.get('center_y', element['y'] + element['height'] // 2)
        
        nearest = None
        min_distance = float('inf')
        
        for text_region in all_text_regions:
            dx = text_region['center_x'] - elem_center_x
            dy = text_region['center_y'] - elem_center_y
            distance = (dx**2 + dy**2) ** 0.5
            
            # Prefer text above or to the left
            if distance < min_distance and distance <= max_distance:
                if dy < 0 or (abs(dy) < 20 and dx < 0):
                    min_distance = distance
                    nearest = text_region
        
        return nearest
