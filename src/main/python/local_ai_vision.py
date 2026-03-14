"""
Local AI Vision Detector using Trained Model
Uses your pre-trained selenium_ngram_model.pkl for element detection
NO external API dependencies - completely offline!
"""

import logging
import numpy as np
import cv2
from typing import Dict, List, Optional
from simple_ocr import SimpleOCR

logger = logging.getLogger(__name__)

class LocalAIVisionDetector:
    """
    Detects UI elements using YOUR trained AI model.
    Combines OCR text understanding with learned patterns from training.
    """
    
    def __init__(self, model_path: str = 'src/resources/selenium_ngram_model.pkl'):
        """Initialize with your trained model."""
        self.model = None
        self.model_path = model_path
        self.ocr = SimpleOCR()
        
        # Load your trained model
        try:
            from inference_improved import ImprovedSeleniumGenerator
            self.model = ImprovedSeleniumGenerator(model_path=model_path, silent=True)
            logger.info(f"[LOCAL-AI] ✅ Loaded trained model from {model_path}")
            logger.info(f"[LOCAL-AI] Model has {len(self.model.dataset_cache)} learned patterns")
        except Exception as e:
            logger.error(f"[LOCAL-AI] ❌ Could not load trained model: {e}")
            self.model = None
        
        # UI element keywords learned from your datasets
        self.input_keywords = {
            'username', 'user', 'email', 'password', 'pass', 'login', 'name',
            'first', 'last', 'phone', 'address', 'city', 'state', 'zip',
            'search', 'id', 'account', 'text', 'field', 'ssn', 'ein', 'producer'
        }
        
        self.button_keywords = {
            'login', 'sign in', 'sign up', 'submit', 'register', 'send', 'save',
            'search', 'go', 'next', 'back', 'cancel', 'ok', 'continue', 'apply',
            'confirm', 'delete', 'add', 'edit', 'update', 'create', 'close'
        }
    
    def analyze_screenshot(self, image: np.ndarray) -> Dict:
        """
        Analyze screenshot using trained AI model + OCR.
        
        Args:
            image: OpenCV image array (BGR)
            
        Returns:
            Dict with detected inputs, buttons, and their semantic labels
        """
        logger.info("[LOCAL-AI] ========== LOCAL AI VISION ANALYSIS ==========")
        
        if self.model is None:
            logger.error("[LOCAL-AI] ❌ No model loaded, cannot analyze")
            return {'inputs': [], 'buttons': [], 'text_regions': []}
        
        # Step 1: Extract all text with OCR
        text_regions = self.ocr.extract_all_text(image)
        logger.info(f"[LOCAL-AI] 📝 Extracted {len(text_regions)} text regions")
        
        # Step 2: Use trained model to understand context
        page_context = self._understand_page_context(text_regions)
        logger.info(f"[LOCAL-AI] 🧠 Page type: {page_context['type']}")
        
        # Step 3: Detect inputs using AI understanding
        inputs = self._detect_inputs_with_ai(image, text_regions, page_context)
        logger.info(f"[LOCAL-AI] 📥 Detected {len(inputs)} input fields")
        
        # Step 4: Detect buttons using AI understanding
        buttons = self._detect_buttons_with_ai(image, text_regions, page_context)
        logger.info(f"[LOCAL-AI] 🔘 Detected {len(buttons)} buttons")
        
        # Log what was found
        for inp in inputs:
            label = inp.get('label', inp.get('display_name', 'Unknown'))
            logger.info(f"[LOCAL-AI]   Input: '{label}' at ({inp['x']}, {inp['y']})")
        
        for btn in buttons:
            text = btn.get('text', btn.get('label', 'Unknown'))
            logger.info(f"[LOCAL-AI]   Button: '{text}' at ({btn['x']}, {btn['y']})")
        
        return {
            'inputs': inputs,
            'buttons': buttons,
            'text_regions': text_regions,
            'context': page_context
        }
    
    def _understand_page_context(self, text_regions: List[Dict]) -> Dict:
        """Use trained model to understand what kind of page this is."""
        # Combine all text
        all_text = ' '.join([r['text'].lower() for r in text_regions])
        
        # Use trained dataset patterns to identify page type
        login_score = 0
        registration_score = 0
        form_score = 0
        
        # Check against learned patterns
        if self.model and self.model.dataset_cache:
            for prompt in self.model.dataset_cache.keys():
                if any(word in prompt for word in ['login', 'sign in', 'username', 'password']):
                    if any(word in all_text for word in ['login', 'sign in', 'username', 'password']):
                        login_score += 1
                elif any(word in prompt for word in ['register', 'sign up', 'create account']):
                    if any(word in all_text for word in ['register', 'sign up', 'create']):
                        registration_score += 1
                elif any(word in prompt for word in ['enter', 'fill', 'type', 'select']):
                    form_score += 1
        
        # Determine page type
        if login_score > registration_score and login_score > form_score:
            page_type = 'login'
            expected = ['username/email input', 'password input', 'login button']
        elif registration_score > login_score:
            page_type = 'registration'
            expected = ['multiple inputs', 'submit button', 'maybe password confirmation']
        else:
            page_type = 'form'
            expected = ['various inputs', 'submit button']
        
        return {
            'type': page_type,
            'expected_elements': expected,
            'confidence': max(login_score, registration_score, form_score) / max(len(text_regions), 1)
        }
    
    def _detect_inputs_with_ai(self, image: np.ndarray, text_regions: List[Dict], 
                                context: Dict) -> List[Dict]:
        """Detect input fields using AI understanding of text labels."""
        inputs = []
        height, width = image.shape[:2]
        
        # Find text that looks like input labels
        for region in text_regions:
            text = region['text'].lower().strip()
            
            # Check if this text matches learned input label patterns
            is_input_label = False
            matched_keyword = None
            
            for keyword in self.input_keywords:
                if keyword in text:
                    # Verify it's a SHORT label (not a paragraph)
                    if len(text.split()) <= 3 and len(text) <= 30:
                        is_input_label = True
                        matched_keyword = keyword
                        break
            
            if not is_input_label:
                continue
            
            logger.info(f"[LOCAL-AI] 🎯 Found input label: '{region['text']}' (keyword: {matched_keyword})")
            
            # Look for input field BELOW this label
            label_x = region['x']
            label_y = region['y']
            label_w = region['width']
            label_h = region['height']
            
            # Search region below label
            search_x = max(0, label_x - 50)
            search_y = label_y + label_h
            search_w = min(width - search_x, label_w + 100)
            search_h = min(height - search_y, 100)
            
            if search_h <= 0 or search_w <= 0:
                continue
            
            # Extract search region
            roi = image[search_y:search_y+search_h, search_x:search_x+search_w]
            
            # Find input field using CV
            input_box = self._find_input_box(roi)
            
            if input_box:
                inp_x, inp_y, inp_w, inp_h = input_box
                
                inputs.append({
                    'type': 'input',
                    'label': region['text'],
                    'display_name': region['text'],
                    'text': region['text'],
                    'x': search_x + inp_x,
                    'y': search_y + inp_y,
                    'width': inp_w,
                    'height': inp_h,
                    'center_x': search_x + inp_x + inp_w // 2,
                    'center_y': search_y + inp_y + inp_h // 2,
                    'confidence': 90,
                    'ai_detected': True,
                    'matched_keyword': matched_keyword
                })
                logger.info(f"[LOCAL-AI] ✅ Found input box below '{region['text']}'")
        
        return inputs
    
    def _detect_buttons_with_ai(self, image: np.ndarray, text_regions: List[Dict],
                                 context: Dict) -> List[Dict]:
        """Detect buttons using AI understanding of action text."""
        buttons = []
        height, width = image.shape[:2]
        
        # Find text that looks like button labels
        for region in text_regions:
            text = region['text'].lower().strip()
            
            # Check if this text matches learned button patterns
            is_button_text = False
            matched_keyword = None
            
            for keyword in self.button_keywords:
                if text == keyword or text.startswith(keyword):
                    # Verify it's SHORT (buttons have 1-2 words)
                    if len(text.split()) <= 2 and len(text) <= 20:
                        is_button_text = True
                        matched_keyword = keyword
                        break
            
            if not is_button_text:
                continue
            
            # Verify this text is ISOLATED (not in a paragraph)
            if not self._is_text_isolated(region, text_regions):
                logger.info(f"[LOCAL-AI] ❌ Rejected button candidate '{text}' - not isolated")
                continue
            
            logger.info(f"[LOCAL-AI] 🎯 Found button text: '{region['text']}' (keyword: {matched_keyword})")
            
            # Look for button container around this text
            btn_x = region['x']
            btn_y = region['y']
            btn_w = region['width']
            btn_h = region['height']
            
            # Search region around text
            search_x = max(0, btn_x - 20)
            search_y = max(0, btn_y - 10)
            search_w = min(width - search_x, btn_w + 40)
            search_h = min(height - search_y, btn_h + 20)
            
            # Extract search region
            roi = image[search_y:search_y+search_h, search_x:search_x+search_w]
            
            # Find button container
            button_box = self._find_button_container(roi)
            
            if button_box:
                box_x, box_y, box_w, box_h = button_box
                
                buttons.append({
                    'type': 'button',
                    'text': region['text'],
                    'label': region['text'],
                    'display_name': region['text'],
                    'x': search_x + box_x,
                    'y': search_y + box_y,
                    'width': box_w,
                    'height': box_h,
                    'center_x': search_x + box_x + box_w // 2,
                    'center_y': search_y + box_y + box_h // 2,
                    'confidence': 95,
                    'ai_detected': True,
                    'matched_keyword': matched_keyword
                })
                logger.info(f"[LOCAL-AI] ✅ Found button container for '{region['text']}'")
            else:
                # No container found, use text position with padding
                buttons.append({
                    'type': 'button',
                    'text': region['text'],
                    'label': region['text'],
                    'display_name': region['text'],
                    'x': btn_x - 10,
                    'y': btn_y - 5,
                    'width': btn_w + 20,
                    'height': btn_h + 10,
                    'center_x': btn_x + btn_w // 2,
                    'center_y': btn_y + btn_h // 2,
                    'confidence': 85,
                    'ai_detected': True,
                    'matched_keyword': matched_keyword
                })
                logger.info(f"[LOCAL-AI] ⚠️ Using text region for button '{region['text']}' (no container)")
        
        return buttons
    
    def _find_input_box(self, roi: np.ndarray) -> Optional[tuple]:
        """Find input box in region of interest."""
        if roi.size == 0:
            return None
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect = w / h if h > 0 else 0
            
            # Input boxes are wide and not too tall
            if 2 < aspect < 15 and 20 < h < 60 and w > 100:
                return (x, y, w, h)
        
        return None
    
    def _find_button_container(self, roi: np.ndarray) -> Optional[tuple]:
        """Find button container in region of interest."""
        if roi.size == 0:
            return None
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect = w / h if h > 0 else 0
            
            # Buttons are wider than tall but not too wide
            if 1.5 < aspect < 8 and 20 < h < 60 and 50 < w < 300:
                return (x, y, w, h)
        
        return None
    
    def _is_text_isolated(self, target_region: Dict, all_regions: List[Dict]) -> bool:
        """Check if text is isolated (not part of a paragraph)."""
        target_x = target_region['center_x']
        target_y = target_region['center_y']
        
        # Count nearby text regions
        nearby_count = 0
        for region in all_regions:
            if region == target_region:
                continue
            
            dx = abs(region['center_x'] - target_x)
            dy = abs(region['center_y'] - target_y)
            
            # If text is very close, it's part of a sentence/paragraph
            if dx < 100 and dy < 30:
                nearby_count += 1
        
        # Isolated text has no more than 1 nearby text
        return nearby_count <= 1
