"""
OCR Text Extractor for Screenshot Analysis
Extracts text from UI elements using Tesseract OCR
Enhances element identification with actual text content
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
from PIL import Image
import logging
import re

logger = logging.getLogger(__name__)

class OCRTextExtractor:
    """Extracts text from screenshots to enhance element detection."""
    
    def __init__(self, tesseract_path: str = None):
        """
        Initialize OCR text extractor.
        
        Args:
            tesseract_path: Path to tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Default Windows installation path
            import os
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
        
        self.text_cache = {}
        self.confidence_threshold = 60  # Minimum OCR confidence
        
    def extract_text_from_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Dict:
        """
        Extract text from specific region of image.
        
        Args:
            image: OpenCV image array
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Dict with text, confidence, and metadata
        """
        x, y, w, h = bbox
        
        # Crop region with padding
        padding = 5
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {'text': '', 'confidence': 0, 'words': []}
        
        # Preprocess for better OCR
        processed = self._preprocess_for_ocr(roi)
        
        # Extract text with detailed info
        try:
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            # Filter by confidence
            words = []
            full_text = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                
                if text and conf >= self.confidence_threshold:
                    words.append({
                        'text': text,
                        'confidence': conf,
                        'bbox': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    })
                    full_text.append(text)
            
            combined_text = ' '.join(full_text)
            avg_confidence = sum(w['confidence'] for w in words) / len(words) if words else 0
            
            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'words': words,
                'element_type': self._classify_by_text(combined_text)
            }
            
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return {'text': '', 'confidence': 0, 'words': []}
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
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
    
    def _classify_by_text(self, text: str) -> str:
        """
        Classify element type based on text content.
        
        Args:
            text: Extracted text
            
        Returns:
            Element type classification
        """
        text_lower = text.lower()
        
        # Button keywords
        button_keywords = ['submit', 'login', 'sign in', 'register', 'sign up', 'send', 
                          'save', 'cancel', 'delete', 'ok', 'yes', 'no', 'next', 'back',
                          'continue', 'confirm', 'apply', 'search', 'add', 'edit', 'remove']
        
        # Link keywords
        link_keywords = ['forgot password', 'create account', 'learn more', 'read more',
                        'click here', 'privacy policy', 'terms', 'help', 'support']
        
        # Label keywords
        label_keywords = ['username', 'password', 'email', 'name', 'address', 'phone',
                         'first name', 'last name', 'company', 'city', 'state', 'zip']
        
        for keyword in button_keywords:
            if keyword in text_lower:
                return 'button'
        
        for keyword in link_keywords:
            if keyword in text_lower:
                return 'link'
        
        for keyword in label_keywords:
            if keyword in text_lower:
                return 'label'
        
        # Check for input hints
        if any(x in text_lower for x in ['enter', 'type', 'select', 'choose']):
            return 'input_hint'
        
        return 'text'
    
    def extract_all_text(self, image: np.ndarray) -> List[Dict]:
        """
        Extract all text regions from entire image.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of text regions with locations
        """
        try:
            # Preprocess entire image
            processed = self._preprocess_for_ocr(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            current_line = []
            current_y = 0
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                
                if text and conf >= self.confidence_threshold:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    word_info = {
                        'text': text,
                        'confidence': conf,
                        'bbox': (x, y, w, h),
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    }
                    
                    # Group words into lines
                    if current_line and abs(y - current_y) > h * 0.5:
                        # New line
                        text_regions.append(self._merge_line_words(current_line))
                        current_line = [word_info]
                        current_y = y
                    else:
                        current_line.append(word_info)
                        current_y = y
            
            # Add last line
            if current_line:
                text_regions.append(self._merge_line_words(current_line))
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Full text extraction failed: {e}")
            return []
    
    def _merge_line_words(self, words: List[Dict]) -> Dict:
        """
        Merge individual words into a single line region.
        
        Args:
            words: List of word dictionaries
            
        Returns:
            Merged line dictionary
        """
        if not words:
            return {}
        
        # Combine text
        full_text = ' '.join(w['text'] for w in words)
        
        # Calculate bounding box
        min_x = min(w['bbox'][0] for w in words)
        min_y = min(w['bbox'][1] for w in words)
        max_x = max(w['bbox'][0] + w['bbox'][2] for w in words)
        max_y = max(w['bbox'][1] + w['bbox'][3] for w in words)
        
        return {
            'text': full_text,
            'confidence': sum(w['confidence'] for w in words) / len(words),
            'bbox': (min_x, min_y, max_x - min_x, max_y - min_y),
            'center_x': (min_x + max_x) // 2,
            'center_y': (min_y + max_y) // 2,
            'word_count': len(words),
            'element_type': self._classify_by_text(full_text)
        }
    
    def enhance_element_with_text(self, element: Dict, image: np.ndarray) -> Dict:
        """
        Enhance detected element with OCR text.
        
        Args:
            element: Element dictionary with bbox
            image: Full screenshot
            
        Returns:
            Enhanced element with text info
        """
        bbox = (element['x'], element['y'], element['width'], element['height'])
        ocr_result = self.extract_text_from_region(image, bbox)
        
        element['text'] = ocr_result['text']
        element['text_confidence'] = ocr_result['confidence']
        element['ocr_classification'] = ocr_result['element_type']
        
        # Generate better ID suggestions based on text
        if ocr_result['text']:
            element['suggested_id'] = self._text_to_id(ocr_result['text'])
            element['suggested_name'] = self._text_to_name(ocr_result['text'])
        
        return element
    
    def _text_to_id(self, text: str) -> str:
        """Convert text to valid HTML ID format."""
        # Remove special chars, convert to lowercase, replace spaces with hyphens
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        clean = clean.lower().strip()
        clean = re.sub(r'\s+', '-', clean)
        return clean or 'element'
    
    def _text_to_name(self, text: str) -> str:
        """Convert text to valid name attribute format."""
        # Similar to ID but allow underscores
        clean = re.sub(r'[^a-zA-Z0-9\s_-]', '', text)
        clean = clean.lower().strip()
        clean = re.sub(r'\s+', '_', clean)
        return clean or 'element'
    
    def find_text_near_element(self, element: Dict, all_text_regions: List[Dict], 
                               max_distance: int = 50) -> Optional[Dict]:
        """
        Find text label near an element (typically input fields).
        
        Args:
            element: Element to find label for
            all_text_regions: All detected text regions
            max_distance: Maximum pixel distance to consider
            
        Returns:
            Nearest text region or None
        """
        elem_center_x = element.get('center_x', element['x'] + element['width'] // 2)
        elem_center_y = element.get('center_y', element['y'] + element['height'] // 2)
        
        nearest = None
        min_distance = float('inf')
        
        for text_region in all_text_regions:
            # Calculate distance
            dx = text_region['center_x'] - elem_center_x
            dy = text_region['center_y'] - elem_center_y
            distance = (dx**2 + dy**2) ** 0.5
            
            # Prefer labels above or to the left
            if distance < min_distance and distance <= max_distance:
                # Check if text is above (dy < 0) or left (dx < 0)
                if dy < 0 or (abs(dy) < 20 and dx < 0):
                    min_distance = distance
                    nearest = text_region
        
        return nearest
