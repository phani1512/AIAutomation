"""
AI-Powered Vision Element Detector
Uses multimodal AI to understand screenshots like a human would.
Detects elements by semantic understanding, not just visual features.
"""

import base64
import logging
import json
import os
from typing import Dict, List, Optional
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class AIVisionDetector:
    """Detects UI elements using AI vision understanding."""
    
    def __init__(self):
        """Initialize AI vision detector."""
        self.api_key = None
        self.model_type = "local"  # Can be: "openai", "anthropic", "local"
        
        # Try to detect available AI services
        self._detect_available_services()
        
    def _detect_available_services(self):
        """Detect what AI vision services are available."""
        # Check for OpenAI
        try:
            import openai
            import os
            if os.getenv('OPENAI_API_KEY'):
                self.model_type = "openai"
                logger.info("[AI-VISION] ✓ OpenAI API detected")
                return
        except:
            pass
            
        # Check for Anthropic
        try:
            import anthropic
            import os
            if os.getenv('ANTHROPIC_API_KEY'):
                self.model_type = "anthropic"
                logger.info("[AI-VISION] ✓ Anthropic API detected")
                return
        except:
            pass
        
        logger.warning("[AI-VISION] No AI vision API found - using fallback CV+OCR method")
        logger.warning("[AI-VISION] For best results, set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def detect_elements_with_ai(self, image_array: np.ndarray) -> Dict:
        """
        Detect elements using AI vision understanding.
        
        Args:
            image_array: OpenCV image array
            
        Returns:
            Dict with detected inputs, buttons, and their semantic labels
        """
        logger.info(f"[AI-VISION] ========== AI ELEMENT DETECTION ==========")
        logger.info(f"[AI-VISION] Model: {self.model_type}")
        
        # Convert image to base64 for AI API
        image_b64 = self._image_to_base64(image_array)
        
        if self.model_type == "openai":
            return self._detect_with_openai(image_b64)
        elif self.model_type == "anthropic":
            return self._detect_with_anthropic(image_b64)
        else:
            return self._detect_with_fallback(image_array)
    
    def _detect_with_openai(self, image_b64: str) -> Dict:
        """Detect elements using OpenAI GPT-4 Vision."""
        try:
            import openai
            
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = """You are an expert QA automation engineer. Analyze this screenshot and identify ONLY the interactive UI elements that a user would interact with.

BE VERY SELECTIVE - only report elements you are 100% confident about:
- Input fields (text boxes for user input)
- Buttons (clickable action buttons like Login, Submit, Search)
- Checkboxes (for selections)
- Links (clickable text links)

DO NOT report:
- Text labels or headings
- Logos or decorative images
- Navigation menus or headers
- Help text or instructions

For each interactive element, provide:
1. type: "input", "button", "checkbox", or "link"
2. label: What the element is for (e.g., "Username", "Password", "Login")
3. position: Approximate location (e.g., "top-center", "middle-left")

Return ONLY a JSON array:
[
  {"type": "input", "label": "Username", "position": "top-center"},
  {"type": "input", "label": "Password", "position": "center"},
  {"type": "button", "label": "Login", "position": "bottom-center"}
]

Be conservative - better to miss an element than report a false positive."""
            
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"[AI-VISION] OpenAI response: {result_text[:200]}")
            
            # Parse JSON from response
            elements_data = json.loads(result_text)
            return self._convert_ai_response_to_elements(elements_data)
            
        except Exception as e:
            logger.error(f"[AI-VISION] OpenAI detection failed: {e}")
            return {"inputs": [], "buttons": [], "checkboxes": [], "links": []}
    
    def _detect_with_anthropic(self, image_b64: str) -> Dict:
        """Detect elements using Anthropic Claude Vision."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            prompt = """You are an expert QA automation engineer. Analyze this screenshot and identify ONLY the interactive UI elements that a user would interact with.

BE VERY SELECTIVE - only report elements you are 100% confident about:
- Input fields (text boxes for user input)
- Buttons (clickable action buttons like Login, Submit, Search)
- Checkboxes (for selections)
- Links (clickable text links)

DO NOT report:
- Text labels or headings
- Logos or decorative images
- Navigation menus or headers
- Help text or instructions

For each interactive element, provide:
1. type: "input", "button", "checkbox", or "link"
2. label: What the element is for (e.g., "Username", "Password", "Login")
3. position: Approximate location (e.g., "top-center", "middle-left")

Return ONLY a JSON array:
[
  {"type": "input", "label": "Username", "position": "top-center"},
  {"type": "input", "label": "Password", "position": "center"},
  {"type": "button", "label": "Login", "position": "bottom-center"}
]

Be conservative - better to miss an element than report a false positive."""
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            result_text = message.content[0].text
            logger.info(f"[AI-VISION] Anthropic response: {result_text[:200]}")
            
            # Parse JSON from response
            elements_data = json.loads(result_text)
            return self._convert_ai_response_to_elements(elements_data)
            
        except Exception as e:
            logger.error(f"[AI-VISION] Anthropic detection failed: {e}")
            return {"inputs": [], "buttons": [], "checkboxes": [], "links": []}
    
    def _detect_with_fallback(self, image_array: np.ndarray) -> Dict:
        """Fallback: Use CV + OCR when no AI API available."""
        logger.info("[AI-VISION] Using CV+OCR fallback method")
        
        # Import the standard CV detector
        from visual_element_detector import VisualElementDetector
        from simple_ocr import SimpleOCR
        
        detector = VisualElementDetector()
        ocr = SimpleOCR()
        
        # Detect elements visually
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        inputs = detector.detect_input_fields(image_array)
        buttons = detector.detect_buttons(image_array)
        
        # Extract text for labeling
        text_regions = ocr.extract_all_text(image_array)
        
        # Try to match text to elements
        for inp in inputs:
            label = self._find_nearest_label(inp, text_regions)
            inp['label'] = label if label else f"Input Field {inputs.index(inp) + 1}"
            inp['display_name'] = inp['label']
        
        for btn in buttons:
            label = self._find_nearest_label(btn, text_regions)
            btn['label'] = label if label else f"Button {buttons.index(btn) + 1}"
            btn['display_name'] = btn['label']
        
        return {
            "inputs": inputs,
            "buttons": buttons,
            "checkboxes": [],
            "links": []
        }
    
    def _convert_ai_response_to_elements(self, ai_elements: List[Dict]) -> Dict:
        """Convert AI response to standard element format."""
        result = {
            "inputs": [],
            "buttons": [],
            "checkboxes": [],
            "links": []
        }
        
        for elem in ai_elements:
            elem_type = elem.get('type', '').lower()
            label = elem.get('label', '')
            position = elem.get('position', 'center')
            
            # Create element dict with label
            element = {
                'type': elem_type,
                'label': label,
                'display_name': label,
                'text': label,
                'position': position,
                'x': 0,  # AI doesn't give exact coords
                'y': 0,
                'width': 200,
                'height': 40,
                'ai_detected': True
            }
            
            # Add to appropriate list
            if elem_type == 'input':
                result['inputs'].append(element)
            elif elem_type == 'button':
                result['buttons'].append(element)
            elif elem_type == 'checkbox':
                result['checkboxes'].append(element)
            elif elem_type == 'link':
                result['links'].append(element)
        
        logger.info(f"[AI-VISION] Detected: {len(result['inputs'])} inputs, {len(result['buttons'])} buttons")
        return result
    
    def _image_to_base64(self, image_array: np.ndarray) -> str:
        """Convert OpenCV image to base64."""
        # Convert BGR to RGB
        rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def _find_nearest_label(self, element: Dict, text_regions: List[Dict]) -> Optional[str]:
        """Find the nearest text label for an element."""
        if not text_regions:
            return None
        
        elem_x = element.get('center_x', element.get('x', 0))
        elem_y = element.get('center_y', element.get('y', 0))
        
        min_distance = float('inf')
        nearest_label = None
        
        for region in text_regions:
            if not isinstance(region, dict):
                continue
            
            text = region.get('text', '').strip()
            if not text or len(text) < 2:
                continue
            
            region_x = region.get('center_x', region.get('x', 0))
            region_y = region.get('center_y', region.get('y', 0))
            
            # Calculate distance
            distance = np.sqrt((elem_x - region_x)**2 + (elem_y - region_y)**2)
            
            # Labels are usually above or to the left of inputs
            # Prefer labels that are close and above
            if distance < min_distance and distance < 250:
                min_distance = distance
                nearest_label = text
        
        return nearest_label
