"""
Intelligent Screenshot Analyzer
Analyzes screenshots by understanding context, like a human QA engineer would.
Uses OCR-first approach: understand what text exists, then find associated interactive elements.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class IntelligentScreenshotAnalyzer:
    """Analyzes screenshots intelligently by understanding context."""
    
    def __init__(self, ocr_extractor, visual_detector):
        """
        Initialize intelligent analyzer.
        
        Args:
            ocr_extractor: OCR engine for text extraction
            visual_detector: Visual detector for finding elements
        """
        self.ocr = ocr_extractor
        self.visual = visual_detector
    
    def analyze(self, image_array: np.ndarray) -> Dict:
        """
        Intelligently analyze screenshot like a human would.
        
        Process:
        1. Read all text (like a human reading the page)
        2. Identify what types of elements should be there based on text
        3. Find those specific elements
        4. Match text labels to elements
        
        Args:
            image_array: OpenCV image array
            
        Returns:
            Dict with intelligently detected and labeled elements
        """
        logger.info("[INTELLIGENT] ========== STARTING INTELLIGENT ANALYSIS ==========")
        
        # STEP 1: Extract ALL text first (like reading the page)
        logger.info("[INTELLIGENT] Step 1: Reading all text from screenshot...")
        all_text = self.ocr.extract_all_text(image_array)
        logger.info(f"[INTELLIGENT] Found {len(all_text)} text regions")
        
        # Log what text we found
        for idx, text_region in enumerate(all_text):
            if isinstance(text_region, dict):
                text = text_region.get('text', '')
                logger.info(f"[INTELLIGENT]   Text {idx}: '{text}'")
        
        # STEP 2: Understand page context from text
        logger.info("[INTELLIGENT] Step 2: Understanding page context...")
        context = self._analyze_page_context(all_text)
        logger.info(f"[INTELLIGENT] Page type: {context['page_type']}")
        logger.info(f"[INTELLIGENT] Expected elements: {context['expected_elements']}")
        
        # STEP 3: Find input fields intelligently
        logger.info("[INTELLIGENT] Step 3: Finding input fields...")
        inputs = self._find_inputs_intelligently(image_array, all_text, context)
        logger.info(f"[INTELLIGENT] Found {len(inputs)} input fields")
        
        # STEP 4: Find buttons intelligently  
        logger.info("[INTELLIGENT] Step 4: Finding buttons...")
        buttons = self._find_buttons_intelligently(image_array, all_text, context)
        logger.info(f"[INTELLIGENT] Found {len(buttons)} buttons")
        
        logger.info("[INTELLIGENT] ========== ANALYSIS COMPLETE ==========")
        
        return {
            'inputs': inputs,
            'buttons': buttons,
            'text_regions': all_text,
            'context': context
        }
    
    def _analyze_page_context(self, text_regions: List[Dict]) -> Dict:
        """
        Understand what kind of page this is based on text content.
        
        Args:
            text_regions: All extracted text
            
        Returns:
            Dict with page_type and expected_elements
        """
        all_text_lower = ' '.join([
            r.get('text', '').lower() 
            for r in text_regions 
            if isinstance(r, dict)
        ])
        
        # Detect page type
        page_type = "unknown"
        expected_elements = []
        
        # Login page patterns
        if any(keyword in all_text_lower for keyword in ['login', 'sign in', 'password', 'username', 'email']):
            page_type = "login"
            expected_elements = ['username_input', 'password_input', 'login_button']
        
        # Registration page patterns
        elif any(keyword in all_text_lower for keyword in ['register', 'sign up', 'create account', 'first name', 'last name']):
            page_type = "registration"
            expected_elements = ['name_inputs', 'email_input', 'password_input', 'submit_button']
        
        # Form page patterns
        elif any(keyword in all_text_lower for keyword in ['submit', 'form', 'enter', 'required']):
            page_type = "form"
            expected_elements = ['multiple_inputs', 'submit_button']
        
        return {
            'page_type': page_type,
            'expected_elements': expected_elements,
            'all_text': all_text_lower
        }
    
    def _find_inputs_intelligently(self, image: np.ndarray, text_regions: List[Dict], context: Dict) -> List[Dict]:
        """
        Find input fields by looking for labels first, then finding inputs near them.
        
        CONSERVATIVE: Only detect actual form field labels, not random text
        """
        inputs = []
        img_height, img_width = image.shape[:2]
        
        # STRICT input field label keywords - only common form fields
        input_label_keywords = [
            'username', 'user name', 'email', 'e-mail', 'password',
            'first name', 'last name', 'name', 'phone', 'mobile',
            'address', 'city', 'state', 'zip', 'postal',
            'search', 'id', 'account'
        ]
        
        potential_labels = []
        for region in text_regions:
            if not isinstance(region, dict):
                continue
            
            text = region.get('text', '').lower().strip()
            
            # STRICT: Must be 1-3 words, match a keyword, and be short
            word_count = len(text.split())
            if word_count > 3 or len(text) > 25:
                continue
            
            # Must contain an input label keyword
            if any(keyword in text for keyword in input_label_keywords):
                potential_labels.append(region)
                logger.info(f"[INTELLIGENT] Potential input label: '{region.get('text')}'")
        
        # For each label, look for an input field below or to the right
        for label in potential_labels:
            label_x = label.get('x', 0)
            label_y = label.get('y', 0)
            label_text = label.get('text', '')
            
            # Search region: below and slightly to the right of label
            search_x_start = max(0, label_x - 50)
            search_x_end = min(img_width, label_x + 400)
            search_y_start = label_y + 5  # Start just below label
            search_y_end = min(img_height, label_y + 80)
            
            # Find rectangles in this region
            input_field = self._find_rectangle_in_region(
                image, 
                search_x_start, search_y_start,
                search_x_end, search_y_end
            )
            
            if input_field:
                input_field['label'] = label_text
                input_field['display_name'] = label_text
                input_field['text'] = label_text
                inputs.append(input_field)
                logger.info(f"[INTELLIGENT] ✓ Found input for label '{label_text}' at ({input_field['x']}, {input_field['y']})")
            else:
                logger.info(f"[INTELLIGENT] ✗ Label '{label_text}' found but no input field detected below it")
        
        # DON'T use CV detection as fallback - it causes false positives
        # Only report inputs we're confident about from labels
        
        return inputs
    
    def _find_buttons_intelligently(self, image: np.ndarray, text_regions: List[Dict], context: Dict) -> List[Dict]:
        """
        Find buttons by looking for button-like text first.
        
        CONSERVATIVE: Only text that is clearly actionable (verbs, short phrases)
        NOT labels, NOT headings, NOT links embedded in sentences
        """
        buttons = []
        img_height, img_width = image.shape[:2]
        
        # STRICT button text patterns - single words or short verb phrases
        button_keywords = [
            'login', 'log in', 'sign in', 'signin',
            'submit', 'continue', 'next', 'register',
            'sign up', 'signup', 'create', 'save',
            'search', 'go', 'send', 'apply', 'confirm'
        ]
        
        for region in text_regions:
            if not isinstance(region, dict):
                continue
            
            text = region.get('text', '').lower().strip()
            
            # STRICT filtering:
            # 1. Must be short (1-2 words, max 15 characters)
            # 2. Must match button keyword exactly
            # 3. Must NOT be part of a longer sentence
            word_count = len(text.split())
            
            if word_count > 3 or len(text) > 20:
                continue  # Too long to be a button
            
            # Check if it's a button keyword
            is_button = any(keyword == text or text.startswith(keyword + ' ') for keyword in button_keywords)
            
            if not is_button:
                continue
            
            # ADDITIONAL CHECK: Must not be surrounded by lots of other text
            # (Buttons are usually isolated, not embedded in paragraphs)
            x, y = region.get('x', 0), region.get('y', 0)
            w, h = region.get('width', 0), region.get('height', 0)
            
            # Check if there's text very close above or below (indicating it's part of a paragraph)
            is_isolated = True
            for other_region in text_regions:
                if other_region == region or not isinstance(other_region, dict):
                    continue
                    
                other_y = other_region.get('y', 0)
                other_x = other_region.get('x', 0)
                
                # If there's text within 30px above/below and same horizontal position, it's in a paragraph
                if abs(other_x - x) < 100 and abs(other_y - y) < 30 and other_y != y:
                    is_isolated = False
                    break
            
            if not is_isolated:
                logger.info(f"[INTELLIGENT] ✗ Rejecting button candidate '{text}' - embedded in text block")
                continue
            
            # Try to find the actual button container in image
            button_found = self._find_button_container(image, x, y, w, h)
            
            if button_found:
                button_found['text'] = region.get('text', '')
                button_found['label'] = region.get('text', '')
                button_found['display_name'] = region.get('text', '')
                buttons.append(button_found)
                logger.info(f"[INTELLIGENT] ✓ Found button with text '{region.get('text')}'")
            else:
                logger.info(f"[INTELLIGENT] ✗ Text '{text}' looks like button but no button container found")
        
        # Remove duplicate/overlapping buttons
        buttons = self._remove_overlapping_buttons(buttons)
        
        return buttons
    
    def _find_button_container(self, image: np.ndarray, text_x: int, text_y: int, text_w: int, text_h: int) -> Optional[Dict]:
        """Find the actual button rectangle containing the text."""
        # Expand region around text to find button container
        search_margin = 20
        x1 = max(0, text_x - search_margin)
        y1 = max(0, text_y - search_margin)
        x2 = min(image.shape[1], text_x + text_w + search_margin)
        y2 = min(image.shape[0], text_y + text_h + search_margin)
        
        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return None
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Look for rectangular button with colored background or border
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect = w / h if h > 0 else 0
            
            # Buttons are usually rectangular, wider than tall
            if 2 < aspect < 8 and w > 60 and 25 < h < 60:
                return {
                    'type': 'button',
                    'x': x1 + x,
                    'y': y1 + y,
                    'width': w,
                    'height': h,
                    'center_x': x1 + x + w // 2,
                    'center_y': y1 + y + h // 2,
                    'area': w * h
                }
        
        # Fallback: use text region as button bounds
        return {
            'type': 'button',
            'x': text_x - 10,
            'y': text_y - 10,
            'width': text_w + 20,
            'height': text_h + 20,
            'center_x': text_x + text_w // 2,
            'center_y': text_y + text_h // 2,
            'area': (text_w + 20) * (text_h + 20)
        }
    
    def _find_rectangle_in_region(self, image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> Optional[Dict]:
        """Find a rectangular input field in the specified region."""
        # Extract region
        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return None
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Try multiple detection methods
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for rectangular contours
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect = w / h if h > 0 else 0
            
            # Input fields are usually horizontal rectangles
            if 2 < aspect < 15 and w > 80 and 15 < h < 60:
                return {
                    'type': 'input',
                    'x': x1 + x,
                    'y': y1 + y,
                    'width': w,
                    'height': h,
                    'center_x': x1 + x + w // 2,
                    'center_y': y1 + y + h // 2,
                    'area': w * h,
                    'aspect_ratio': round(aspect, 2)
                }
        
        return None
    
    def _find_nearest_text_label(self, element: Dict, text_regions: List[Dict]) -> Optional[str]:
        """Find the nearest text that could be a label for this element."""
        elem_x = element.get('x', 0)
        elem_y = element.get('y', 0)
        
        min_distance = float('inf')
        best_label = None
        
        for region in text_regions:
            if not isinstance(region, dict):
                continue
            
            text = region.get('text', '').strip()
            if not text or len(text) < 2:
                continue
            
            region_x = region.get('x', 0)
            region_y = region.get('y', 0)
            
            # Calculate distance (prefer text above the element)
            dx = abs(elem_x - region_x)
            dy = elem_y - region_y  # Positive if text is above
            
            # Prefer labels above and close
            if dy > 0 and dy < 80 and dx < 150:
                distance = np.sqrt(dx**2 + dy**2)
                if distance < min_distance:
                    min_distance = distance
                    best_label = text
        
        return best_label
    
    def _elements_overlap(self, elem1: Dict, elem2: Dict) -> bool:
        """Check if two elements overlap."""
        x1, y1, w1, h1 = elem1['x'], elem1['y'], elem1['width'], elem1['height']
        x2, y2, w2, h2 = elem2['x'], elem2['y'], elem2['width'], elem2['height']
        
        # Check if rectangles overlap
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
    
    def _remove_overlapping_buttons(self, buttons: List[Dict]) -> List[Dict]:
        """Remove overlapping buttons, keeping the most likely one."""
        if len(buttons) <= 1:
            return buttons
        
        filtered = []
        for btn in sorted(buttons, key=lambda b: b.get('area', 0), reverse=True):
            overlaps = False
            for kept in filtered:
                if self._elements_overlap(btn, kept):
                    overlaps = True
                    break
            if not overlaps:
                filtered.append(btn)
        
        return filtered
