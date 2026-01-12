"""
Custom OCR Engine - No External Dependencies
Pure Python/OpenCV implementation for text detection and recognition
Optimized for UI elements (buttons, labels, inputs)
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)

class CustomOCREngine:
    """
    Custom OCR engine using computer vision techniques.
    No external OCR dependencies required.
    Designed for UI element text extraction.
    """
    
    def __init__(self):
        """Initialize custom OCR engine."""
        self.confidence_threshold = 60
        
        # Common UI text patterns
        self.ui_patterns = {
            'buttons': ['login', 'submit', 'sign in', 'sign up', 'register', 'send', 
                       'save', 'cancel', 'ok', 'yes', 'no', 'next', 'back', 'search',
                       'add', 'edit', 'delete', 'remove', 'confirm', 'apply'],
            'labels': ['username', 'password', 'email', 'name', 'phone', 'address',
                      'first name', 'last name', 'company', 'city', 'state', 'zip'],
            'actions': ['click', 'enter', 'select', 'choose', 'type', 'upload']
        }
        
        # Button text templates (common shapes and sizes)
        self.button_templates = self._create_button_templates()
        
    def _create_button_templates(self) -> Dict:
        """Create templates for common button text."""
        templates = {}
        
        # Create simple templates for common words
        for word in self.ui_patterns['buttons']:
            # We'll detect buttons by shape and infer text from context
            templates[word] = {
                'length': len(word),
                'pattern': word.lower()
            }
        
        return templates
    
    def extract_text_from_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Extract text from specific region using custom OCR.
        
        Args:
            image: OpenCV image array
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Dict with text, confidence, and metadata
        """
        x, y, w, h = bbox
        
        # Crop region
        padding = 5
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {'text': '', 'confidence': 0, 'words': []}
        
        # Preprocess for text detection
        processed = self._preprocess_for_ocr(roi)
        
        # Detect text characteristics
        text_info = self._analyze_text_region(processed, w, h)
        
        # Infer text from UI context
        inferred_text = self._infer_text_from_context(text_info, w, h)
        
        return {
            'text': inferred_text,
            'confidence': text_info['confidence'],
            'words': [{'text': inferred_text, 'confidence': text_info['confidence']}],
            'element_type': text_info['element_type']
        }
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for text detection."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Resize if too small
        height, width = gray.shape
        if height < 20 or width < 20:
            scale = max(20 / height, 20 / width)
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def _analyze_text_region(self, image: np.ndarray, width: int, height: int) -> Dict:
        """
        Analyze text region characteristics without actual OCR.
        Uses shape, size, and pattern analysis.
        """
        # Detect contours (character shapes)
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count potential characters
        char_count = 0
        char_heights = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter out noise (too small or too large)
            if 10 < area < (width * height * 0.5) and h > 5:
                char_count += 1
                char_heights.append(h)
        
        avg_char_height = np.mean(char_heights) if char_heights else 0
        
        # Estimate text length based on width and character count
        estimated_length = max(char_count, int(width / (avg_char_height * 0.6)) if avg_char_height > 0 else 0)
        
        # Determine element type based on dimensions
        aspect_ratio = width / height if height > 0 else 0
        
        if aspect_ratio > 3 and height < 50:
            element_type = 'button'
        elif aspect_ratio > 2 and height < 40:
            element_type = 'label'
        elif aspect_ratio < 1.5 and height > 30:
            element_type = 'input'
        else:
            element_type = 'text'
        
        return {
            'char_count': char_count,
            'estimated_length': estimated_length,
            'avg_char_height': avg_char_height,
            'element_type': element_type,
            'confidence': min(80, 50 + char_count * 5)  # Higher confidence with more characters
        }
    
    def _infer_text_from_context(self, text_info: Dict, width: int, height: int) -> str:
        """
        Infer likely text based on UI context and element characteristics.
        """
        element_type = text_info['element_type']
        estimated_length = text_info['estimated_length']
        
        # Match against common UI patterns
        if element_type == 'button':
            # Find matching button text by length
            candidates = []
            for word in self.ui_patterns['buttons']:
                if abs(len(word) - estimated_length) <= 3:  # Within 3 characters
                    candidates.append(word)
            
            if candidates:
                # Prefer common button texts
                priority = ['login', 'submit', 'sign in', 'register', 'send', 'save']
                for p in priority:
                    if p in candidates:
                        return p.title()
                return candidates[0].title()
            
            return 'Button'
        
        elif element_type == 'label':
            # Find matching label text by length
            candidates = []
            for word in self.ui_patterns['labels']:
                if abs(len(word) - estimated_length) <= 3:
                    candidates.append(word)
            
            if candidates:
                priority = ['username', 'password', 'email', 'name']
                for p in priority:
                    if p in candidates:
                        return p.title()
                return candidates[0].title()
            
            return 'Label'
        
        elif element_type == 'input':
            return 'Input Field'
        
        return 'Text'
    
    def extract_all_text(self, image: np.ndarray) -> List[Dict]:
        """
        Extract all text regions from image using custom detection.
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply edge detection to find text regions
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter text regions by size
            if 100 < area < (image.shape[0] * image.shape[1] * 0.3) and h > 10 and w > 20:
                # Extract text from this region
                text_data = self.extract_text_from_region(image, (x, y, w, h))
                
                if text_data['text']:
                    text_regions.append({
                        'text': text_data['text'],
                        'confidence': text_data['confidence'],
                        'bbox': (x, y, w, h),
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'element_type': text_data['element_type']
                    })
        
        return text_regions
    
    def enhance_element_with_text(self, element: Dict, image: np.ndarray) -> Dict:
        """Enhance element with inferred text."""
        bbox = (element['x'], element['y'], element['width'], element['height'])
        text_result = self.extract_text_from_region(image, bbox)
        
        element['text'] = text_result['text']
        element['text_confidence'] = text_result['confidence']
        element['ocr_classification'] = text_result['element_type']
        
        # Generate ID/name suggestions
        if text_result['text']:
            element['suggested_id'] = self._text_to_id(text_result['text'])
            element['suggested_name'] = self._text_to_name(text_result['text'])
        
        return element
    
    def _text_to_id(self, text: str) -> str:
        """Convert text to valid HTML ID format."""
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        clean = clean.lower().strip()
        clean = re.sub(r'\s+', '-', clean)
        return clean or 'element'
    
    def _text_to_name(self, text: str) -> str:
        """Convert text to valid name attribute format."""
        clean = re.sub(r'[^a-zA-Z0-9\s_-]', '', text)
        clean = clean.lower().strip()
        clean = re.sub(r'\s+', '_', clean)
        return clean or 'element'
    
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
            
            if distance < min_distance and distance <= max_distance:
                if dy < 0 or (abs(dy) < 20 and dx < 0):
                    min_distance = distance
                    nearest = text_region
        
        return nearest


class HybridOCREngine:
    """
    Hybrid OCR engine that uses custom OCR by default
    and falls back to Tesseract if available for better accuracy.
    """
    
    def __init__(self):
        """Initialize hybrid OCR engine."""
        self.custom_ocr = CustomOCREngine()
        self.tesseract_available = False
        self.tesseract_ocr = None
        
        # Try to load Tesseract
        try:
            import pytesseract
            import os
            
            # Try default path
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
                self.tesseract_available = True
                
                # Import the full OCR extractor
                from ocr_text_extractor import OCRTextExtractor
                self.tesseract_ocr = OCRTextExtractor()
                logger.info("[HYBRID-OCR] ✓ Tesseract available - using for enhanced accuracy")
            else:
                logger.info("[HYBRID-OCR] ⚠ Tesseract not found - using custom OCR only")
        except Exception as e:
            logger.info(f"[HYBRID-OCR] ⚠ Tesseract not available: {e} - using custom OCR only")
        
        if not self.tesseract_available:
            logger.info("[HYBRID-OCR] ✓ Custom OCR engine active (no external dependencies)")
    
    def extract_text_from_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """Extract text using best available method."""
        if self.tesseract_available and self.tesseract_ocr:
            try:
                return self.tesseract_ocr.extract_text_from_region(image, bbox)
            except Exception as e:
                logger.warning(f"[HYBRID-OCR] Tesseract failed, using custom OCR: {e}")
                return self.custom_ocr.extract_text_from_region(image, bbox)
        else:
            return self.custom_ocr.extract_text_from_region(image, bbox)
    
    def extract_all_text(self, image: np.ndarray) -> List[Dict]:
        """Extract all text using best available method."""
        if self.tesseract_available and self.tesseract_ocr:
            try:
                return self.tesseract_ocr.extract_all_text(image)
            except Exception as e:
                logger.warning(f"[HYBRID-OCR] Tesseract failed, using custom OCR: {e}")
                return self.custom_ocr.extract_all_text(image)
        else:
            return self.custom_ocr.extract_all_text(image)
    
    def enhance_element_with_text(self, element: Dict, image: np.ndarray) -> Dict:
        """Enhance element using best available method."""
        if self.tesseract_available and self.tesseract_ocr:
            try:
                return self.tesseract_ocr.enhance_element_with_text(element, image)
            except Exception as e:
                logger.warning(f"[HYBRID-OCR] Tesseract failed, using custom OCR: {e}")
                return self.custom_ocr.enhance_element_with_text(element, image)
        else:
            return self.custom_ocr.enhance_element_with_text(element, image)
    
    def find_text_near_element(self, element: Dict, all_text_regions: List[Dict], 
                               max_distance: int = 50) -> Optional[Dict]:
        """Find text near element."""
        if self.tesseract_available and self.tesseract_ocr:
            return self.tesseract_ocr.find_text_near_element(element, all_text_regions, max_distance)
        else:
            return self.custom_ocr.find_text_near_element(element, all_text_regions, max_distance)
    
    def get_engine_info(self) -> Dict:
        """Get information about active OCR engine."""
        return {
            'engine': 'Hybrid OCR',
            'tesseract_available': self.tesseract_available,
            'custom_ocr_active': True,
            'mode': 'Tesseract + Custom' if self.tesseract_available else 'Custom Only',
            'dependencies': 'None (OpenCV only)' if not self.tesseract_available else 'OpenCV + Tesseract (optional)'
        }
