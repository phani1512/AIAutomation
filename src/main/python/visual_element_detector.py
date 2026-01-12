"""
Visual Element Detector using Computer Vision
Detects UI elements from screenshots for test automation
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class VisualElementDetector:
    """Detects UI elements from screenshots using computer vision."""
    
    def __init__(self):
        """Initialize the visual element detector."""
        self.element_templates = {}
        self.last_screenshot = None
        
    def load_screenshot(self, screenshot_data: str) -> np.ndarray:
        """
        Load screenshot from base64 string or file path.
        
        Args:
            screenshot_data: Base64 encoded image or file path
            
        Returns:
            OpenCV image array
        """
        try:
            # Try as base64 first
            if screenshot_data.startswith('data:image'):
                screenshot_data = screenshot_data.split(',')[1]
            
            img_data = base64.b64decode(screenshot_data)
            img = Image.open(BytesIO(img_data))
            img_array = np.array(img)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            self.last_screenshot = img_bgr
            return img_bgr
        except:
            # Try as file path
            img_bgr = cv2.imread(screenshot_data)
            self.last_screenshot = img_bgr
            return img_bgr
    
    def detect_buttons(self, image: np.ndarray) -> List[Dict]:
        """
        Detect button elements in the image.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of detected buttons with coordinates and properties
        """
        buttons = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by button-like dimensions
            aspect_ratio = w / float(h) if h > 0 else 0
            area = w * h
            
            if 1.5 <= aspect_ratio <= 6 and 1000 <= area <= 50000:
                # Extract button region
                button_roi = image[y:y+h, x:x+w]
                
                # Get dominant color
                avg_color = cv2.mean(button_roi)[:3]
                
                buttons.append({
                    'type': 'button',
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2),
                    'color': [int(c) for c in avg_color],
                    'area': int(area)
                })
        
        logger.info(f"[VISUAL] Detected {len(buttons)} button candidates")
        return buttons
    
    def detect_input_fields(self, image: np.ndarray) -> List[Dict]:
        """
        Detect input field elements in the image.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of detected input fields with coordinates
        """
        input_fields = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by input field-like dimensions (long and thin)
            aspect_ratio = w / float(h) if h > 0 else 0
            area = w * h
            
            if aspect_ratio >= 3 and 2000 <= area <= 100000 and h <= 60:
                input_fields.append({
                    'type': 'input',
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2)
                })
        
        logger.info(f"[VISUAL] Detected {len(input_fields)} input field candidates")
        return input_fields
    
    def detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect text regions using EAST text detector or simple methods.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of detected text regions with bounding boxes
        """
        text_regions = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Use morphological operations to detect text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
        dilated = cv2.dilate(gray, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by text-like dimensions
            if w > 30 and h > 10 and w < image.shape[1] * 0.9:
                text_roi = image[y:y+h, x:x+w]
                
                text_regions.append({
                    'type': 'text',
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2)
                })
        
        logger.info(f"[VISUAL] Detected {len(text_regions)} text regions")
        return text_regions
    
    def detect_all_elements(self, screenshot_data: str) -> Dict[str, List[Dict]]:
        """
        Detect all UI elements in a screenshot.
        
        Args:
            screenshot_data: Base64 encoded screenshot or file path
            
        Returns:
            Dictionary containing all detected elements by type
        """
        image = self.load_screenshot(screenshot_data)
        
        if image is None:
            logger.error("[VISUAL] Failed to load screenshot")
            return {'buttons': [], 'inputs': [], 'text_regions': []}
        
        buttons = self.detect_buttons(image)
        inputs = self.detect_input_fields(image)
        text_regions = self.detect_text_regions(image)
        
        return {
            'buttons': buttons,
            'inputs': inputs,
            'text_regions': text_regions,
            'screenshot_width': image.shape[1],
            'screenshot_height': image.shape[0]
        }
    
    def find_element_at_position(self, x: int, y: int, elements: Dict) -> Optional[Dict]:
        """
        Find which element contains the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            elements: Dictionary of detected elements
            
        Returns:
            Element dict if found, None otherwise
        """
        for element_type in ['buttons', 'inputs', 'text_regions']:
            for element in elements.get(element_type, []):
                ex, ey, ew, eh = element['x'], element['y'], element['width'], element['height']
                if ex <= x <= ex + ew and ey <= y <= ey + eh:
                    return element
        
        return None
    
    def annotate_screenshot(self, elements: Dict, output_path: str = None) -> np.ndarray:
        """
        Draw bounding boxes on detected elements.
        
        Args:
            elements: Dictionary of detected elements
            output_path: Optional path to save annotated image
            
        Returns:
            Annotated image array
        """
        if self.last_screenshot is None:
            return None
        
        annotated = self.last_screenshot.copy()
        
        # Draw buttons in green
        for btn in elements.get('buttons', []):
            cv2.rectangle(annotated, (btn['x'], btn['y']), 
                         (btn['x'] + btn['width'], btn['y'] + btn['height']), 
                         (0, 255, 0), 2)
            cv2.putText(annotated, 'BTN', (btn['x'], btn['y'] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw inputs in blue
        for inp in elements.get('inputs', []):
            cv2.rectangle(annotated, (inp['x'], inp['y']), 
                         (inp['x'] + inp['width'], inp['y'] + inp['height']), 
                         (255, 0, 0), 2)
            cv2.putText(annotated, 'INPUT', (inp['x'], inp['y'] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw text regions in red
        for txt in elements.get('text_regions', []):
            cv2.rectangle(annotated, (txt['x'], txt['y']), 
                         (txt['x'] + txt['width'], txt['y'] + txt['height']), 
                         (0, 0, 255), 1)
        
        if output_path:
            cv2.imwrite(output_path, annotated)
            logger.info(f"[VISUAL] Saved annotated screenshot to {output_path}")
        
        return annotated
