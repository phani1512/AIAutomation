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
    
    def _remove_overlapping_elements(self, elements: List[Dict], overlap_threshold: float = 0.7) -> List[Dict]:
        """
        Remove overlapping elements, keeping the larger/better ones.
        
        Args:
            elements: List of element dictionaries
            overlap_threshold: IoU threshold for considering elements as overlapping
            
        Returns:
            Filtered list with duplicates removed
        """
        if len(elements) <= 1:
            return elements
        
        # Sort by area (larger first)
        sorted_elements = sorted(elements, key=lambda e: e.get('area', e['width'] * e['height']), reverse=True)
        filtered = []
        
        for elem in sorted_elements:
            # Check if this element overlaps significantly with any kept element
            is_duplicate = False
            for kept in filtered:
                iou = self._calculate_iou(elem, kept)
                if iou > overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(elem)
        
        return filtered
    
    def _calculate_iou(self, elem1: Dict, elem2: Dict) -> float:
        """
        Calculate Intersection over Union (IoU) between two elements.
        
        Args:
            elem1: First element
            elem2: Second element
            
        Returns:
            IoU value between 0 and 1
        """
        # Get coordinates
        x1_min, y1_min = elem1['x'], elem1['y']
        x1_max, y1_max = elem1['x'] + elem1['width'], elem1['y'] + elem1['height']
        x2_min, y2_min = elem2['x'], elem2['y']
        x2_max, y2_max = elem2['x'] + elem2['width'], elem2['y'] + elem2['height']
        
        # Calculate intersection
        x_inter_min = max(x1_min, x2_min)
        y_inter_min = max(y1_min, y2_min)
        x_inter_max = min(x1_max, x2_max)
        y_inter_max = min(y1_max, y2_max)
        
        if x_inter_max < x_inter_min or y_inter_max < y_inter_min:
            return 0.0
        
        intersection = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)
        
        # Calculate union
        area1 = elem1['width'] * elem1['height']
        area2 = elem2['width'] * elem2['height']
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
        
    def load_screenshot(self, screenshot_data: str) -> np.ndarray:
        """
        Load screenshot from base64 string or file path.
        
        Args:
            screenshot_data: Base64 encoded image or file path
            
        Returns:
            OpenCV image array
        """
        print(f"\n[LOAD_SCREENSHOT] Called with data length: {len(screenshot_data) if screenshot_data else 0}")
        print(f"[LOAD_SCREENSHOT] Data type: {type(screenshot_data)}")
        print(f"[LOAD_SCREENSHOT] First 50 chars: {screenshot_data[:50] if screenshot_data else 'EMPTY'}")
        
        try:
            # Try as base64 first
            original_data = screenshot_data
            if screenshot_data.startswith('data:image'):
                print(f"[LOAD_SCREENSHOT] Detected data URL, extracting base64 part...")
                screenshot_data = screenshot_data.split(',')[1]
                print(f"[LOAD_SCREENSHOT] After split, length: {len(screenshot_data)}")
            
            print(f"[LOAD_SCREENSHOT] Attempting base64 decode...")
            img_data = base64.b64decode(screenshot_data)
            print(f"[LOAD_SCREENSHOT] Decoded {len(img_data)} bytes")
            
            print(f"[LOAD_SCREENSHOT] Opening image with PIL...")
            img = Image.open(BytesIO(img_data))
            print(f"[LOAD_SCREENSHOT] PIL image loaded: size={img.size}, mode={img.mode}")
            
            print(f"[LOAD_SCREENSHOT] Converting to numpy array...")
            img_array = np.array(img)
            print(f"[LOAD_SCREENSHOT] Numpy array shape: {img_array.shape}")
            
            print(f"[LOAD_SCREENSHOT] Converting RGB to BGR...")
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            self.last_screenshot = img_bgr
            logger.info(f"[VISUAL] ✓ Screenshot loaded successfully: shape={img_bgr.shape}")
            print(f"[LOAD_SCREENSHOT] ✓ SUCCESS: Final shape={img_bgr.shape}\n")
            return img_bgr
        except Exception as e:
            print(f"[LOAD_SCREENSHOT] ✗ Base64 decode failed: {e}")
            print(f"[LOAD_SCREENSHOT] Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            logger.error(f"[VISUAL] Base64 decode failed: {e}")
            
            # Try as file path
            try:
                print(f"[LOAD_SCREENSHOT] Trying as file path...")
                img_bgr = cv2.imread(screenshot_data)
                if img_bgr is not None:
                    self.last_screenshot = img_bgr
                    logger.info(f"[VISUAL] Screenshot loaded from file: shape={img_bgr.shape}")
                    print(f"[LOAD_SCREENSHOT] ✓ Loaded from file: shape={img_bgr.shape}\n")
                    return img_bgr
                else:
                    logger.error(f"[VISUAL] File path failed: {screenshot_data[:100]}...")
                    print(f"[LOAD_SCREENSHOT] ✗ File path returned None\n")
                    return None
            except Exception as e2:
                logger.error(f"[VISUAL] Both base64 and file path failed: {e2}")
                print(f"[LOAD_SCREENSHOT] ✗ File path exception: {e2}\n")
                return None
    
    def detect_buttons(self, image: np.ndarray) -> List[Dict]:
        """
        Detect button elements in the image with adaptive thresholds.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of detected buttons with coordinates and properties
        """
        buttons = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # UNIVERSAL: Fully adaptive thresholds based on actual image characteristics
        img_area = image.shape[0] * image.shape[1]
        img_height, img_width = image.shape[:2]
        
        # Dynamic thresholds scale with image size
        min_button_area = max(200, int(img_area * 0.0002))  # VERY relaxed - even small buttons
        max_button_area = min(100000, int(img_area * 0.08))  # Very flexible maximum
        
        logger.info(f"[VISUAL-DEBUG] Adaptive button thresholds: area={min_button_area}-{max_button_area}")
        
        # MULTI-PASS: Try multiple edge detection sensitivities
        edges_aggressive = cv2.Canny(gray, 30, 100)  # Catch subtle edges
        edges_moderate = cv2.Canny(gray, 50, 150)   # Standard edges
        edges_conservative = cv2.Canny(gray, 70, 200) # Only strong edges
        
        # Combine all edge maps
        edges = cv2.bitwise_or(edges_aggressive, edges_moderate)
        edges = cv2.bitwise_or(edges, edges_conservative)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        logger.info(f"[VISUAL-DEBUG] Button detection: found {len(contours)} total contours")
        logger.info(f"[VISUAL-DEBUG] Button thresholds: area={min_button_area}-{max_button_area}, height=20-60, width=70-400, aspect=1.8-5.5")
        
        rejected_count = 0
        rejection_reasons = []
        
        # UNIVERSAL: Dynamic button thresholds that scale with image size
        min_aspect = 1.2  # Nearly square to wide
        max_aspect = 10.0  # Very wide buttons
        min_height = max(10, int(img_height * 0.015))  # Scale with image
        max_height = min(100, int(img_height * 0.12))  # Scale with image
        min_width = max(40, int(img_width * 0.03))     # Scale with image
        max_width = min(800, int(img_width * 0.5))     # Scale with image
        
        logger.info(f"[VISUAL-DEBUG] Button thresholds: aspect={min_aspect}-{max_aspect}, height={min_height}-{max_height}, width={min_width}-{max_width}, area={min_button_area}-{max_button_area}")
        
        for idx, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate metrics
            aspect_ratio = w / float(h) if h > 0 else 0
            area = w * h
            
            # LOG: Show why contours are rejected (first 5 only)
            reasons = []
            if not (min_aspect <= aspect_ratio <= max_aspect):
                reasons.append(f"aspect={aspect_ratio:.2f}")
            if not (min_button_area <= area <= max_button_area):
                reasons.append(f"area={area}")
            if not (min_height <= h <= max_height):
                reasons.append(f"height={h}")
            if not (min_width <= w <= max_width):
                reasons.append(f"width={w}")
            
            if reasons:
                rejected_count += 1
                if rejected_count <= 5:  # Log first 5 rejections
                    rejection_reasons.append(f"Contour {idx}: [{', '.join(reasons)}]")
            
            # Apply the dynamic thresholds
            if (min_aspect <= aspect_ratio <= max_aspect and
                min_button_area <= area <= max_button_area and 
                min_height <= h <= max_height and
                min_width <= w <= max_width):
                
                # Extract button region for color analysis
                button_roi = image[y:y+h, x:x+w]
                avg_color = cv2.mean(button_roi)[:3]
                
                # Calculate color variance (buttons often have solid colors)
                std_dev = np.std(button_roi)
                
                button = {
                    'type': 'button',
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'center_x': int(x + w/2),
                    'center_y': int(y + h/2),
                    'color': [int(c) for c in avg_color],
                    'area': int(area),
                    'aspect_ratio': round(aspect_ratio, 2),
                    'color_variance': float(std_dev)
                }
                buttons.append(button)
                logger.info(f"[VISUAL-DEBUG] ✓ ACCEPTED Button: x={x}, y={y}, w={w}, h={h}, aspect={aspect_ratio:.2f}, area={area}")
        
        # Log rejection summary
        if rejection_reasons:
            logger.warning(f"[VISUAL-DEBUG] ✗ REJECTED {rejected_count} button candidates:")
            for reason in rejection_reasons:
                logger.warning(f"[VISUAL-DEBUG]   {reason}")
        
        logger.info(f"[VISUAL-DEBUG] Found {len(buttons)} buttons before overlap removal")
        
        # Remove overlapping buttons (IoU threshold 0.6 for buttons)
        buttons = self._remove_overlapping_elements(buttons, overlap_threshold=0.6)
        
        # Sort by vertical position (top to bottom)
        buttons = sorted(buttons, key=lambda b: b['y'])
        
        logger.info(f"[VISUAL] Detected {len(buttons)} buttons after overlap removal (adaptive)")
        return buttons
    
    def detect_input_fields(self, image: np.ndarray) -> List[Dict]:
        """
        Detect input field elements using robust multi-method computer vision.
        Works like "robot eyes" to find actual form input fields.
        
        Args:
            image: OpenCV image array
            
        Returns:
            List of detected input fields with coordinates
        """
        logger.info(f"[VISUAL] ========== ROBOT EYES INPUT DETECTION ==========")
        logger.info(f"[VISUAL] Image shape: {image.shape}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_height, img_width = image.shape[:2]
        img_area = img_height * img_width
        
        # METHOD 1: Detect rectangular borders (most input fields have borders)
        logger.info(f"[VISUAL] Method 1: Detecting bordered rectangles...")
        bordered_inputs = self._detect_bordered_rectangles(gray, img_width, img_height)
        logger.info(f"[VISUAL]   Found {len(bordered_inputs)} bordered rectangles")
        
        # METHOD 2: Detect white/light rectangular regions (input backgrounds)
        logger.info(f"[VISUAL] Method 2: Detecting light background rectangles...")
        light_bg_inputs = self._detect_light_rectangles(gray, img_width, img_height)
        logger.info(f"[VISUAL]   Found {len(light_bg_inputs)} light rectangles")
        
        # METHOD 3: Detect filled regions with uniform color
        logger.info(f"[VISUAL] Method 3: Detecting uniform filled regions...")
        uniform_inputs = self._detect_uniform_regions(gray, img_width, img_height)
        logger.info(f"[VISUAL]   Found {len(uniform_inputs)} uniform regions")
        
        # Combine all detected candidates
        all_candidates = bordered_inputs + light_bg_inputs + uniform_inputs
        logger.info(f"[VISUAL] Total candidates from all methods: {len(all_candidates)}")
        
        # Combine all detected candidates
        all_candidates = bordered_inputs + light_bg_inputs + uniform_inputs
        logger.info(f"[VISUAL] Total candidates from all methods: {len(all_candidates)}")
        
        # Aggressive deduplication - remove overlapping detections
        unique_inputs = self._remove_overlapping_elements(all_candidates, overlap_threshold=0.3)
        logger.info(f"[VISUAL] After overlap removal: {len(unique_inputs)} unique inputs")
        
        # Filter by typical input field characteristics
        valid_inputs = []
        for inp in unique_inputs:
            w, h = inp['width'], inp['height']
            aspect = w / h if h > 0 else 0
            area = w * h
            
            # Input fields are typically:
            # - Horizontal rectangles (aspect > 1.5)
            # - Not too small (area > 1000px)
            # - Not too large (area < 20% of screen)
            # - Height between 20-80px for most forms
            
            min_area = 1000
            max_area = int(img_area * 0.2)
            min_aspect = 1.5
            max_aspect = 15.0
            min_height = 15
            max_height = 100
            
            if (min_aspect <= aspect <= max_aspect and
                min_area <= area <= max_area and
                min_height <= h <= max_height):
                valid_inputs.append(inp)
                logger.info(f"[VISUAL]   ✓ VALID INPUT: {w}x{h} @ ({inp['x']},{inp['y']}) aspect={aspect:.2f}")
            else:
                logger.debug(f"[VISUAL]   ✗ Rejected: {w}x{h} @ ({inp['x']},{inp['y']}) aspect={aspect:.2f} area={area}")
        
        # Sort by vertical position
        valid_inputs = sorted(valid_inputs, key=lambda i: i['y'])
        
        logger.info(f"[VISUAL] ========== FINAL: {len(valid_inputs)} INPUT FIELDS DETECTED ==========")
        return valid_inputs
    
    def _detect_bordered_rectangles(self, gray: np.ndarray, img_width: int, img_height: int) -> List[Dict]:
        """Detect input fields by finding bordered rectangles."""
        # Use moderate edge detection to find borders
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect broken edges
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect = w / h if h > 0 else 0
            
            # Look for horizontal rectangles with reasonable size
            if aspect > 1.5 and area > 1000 and w > 100 and 15 < h < 100:
                candidates.append({
                    'type': 'input',
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'center_x': x + w//2, 'center_y': y + h//2,
                    'area': area, 'aspect_ratio': round(aspect, 2),
                    'method': 'bordered'
                })
        
        return candidates
    
    def _detect_light_rectangles(self, gray: np.ndarray, img_width: int, img_height: int) -> List[Dict]:
        """Detect input fields by finding light/white rectangular regions."""
        # Threshold to find light areas (input fields often have white/light backgrounds)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect = w / h if h > 0 else 0
            
            # Look for horizontal rectangles
            if aspect > 1.5 and area > 1000 and w > 100 and 15 < h < 100:
                candidates.append({
                    'type': 'input',
                    'x': x, 'y': y, 'width': w, 'height': h,
                    'center_x': x + w//2, 'center_y': y + h//2,
                    'area': area, 'aspect_ratio': round(aspect, 2),
                    'method': 'light_bg'
                })
        
        return candidates
    
    def _detect_uniform_regions(self, gray: np.ndarray, img_width: int, img_height: int) -> List[Dict]:
        """Detect input fields by finding regions with uniform color/texture."""
        # Use adaptive threshold to segment uniform regions
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 21, 10)
        
        # Find contours in uniform regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect = w / h if h > 0 else 0
            
            # Look for horizontal rectangles
            if aspect > 1.5 and area > 1000 and w > 100 and 15 < h < 100:
                # Check if region has uniform intensity (typical of input fields)
                roi = gray[y:y+h, x:x+w]
                std_dev = np.std(roi)
                
                # Input fields typically have low variance (uniform background)
                if std_dev < 50:
                    candidates.append({
                        'type': 'input',
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'center_x': x + w//2, 'center_y': y + h//2,
                        'area': area, 'aspect_ratio': round(aspect, 2),
                        'method': 'uniform'
                    })
        
        return candidates

    
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
    
    def detect_links(self, image: np.ndarray) -> List[Dict]:
        """
        Detect clickable links (typically underlined text or text with special styling).
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of link dictionaries
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 40, 120)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        links = []
        for idx, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Links are typically wide and short (aspect ratio > 2)
            if 2.0 < aspect_ratio < 20.0 and 15 < w < 300 and 8 < h < 30 and w * h > 100:
                links.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': w * h,
                    'text': f'Link {idx}',  # Will be filled by OCR
                    'type': 'link',
                    'index': idx
                })
        
        logger.info(f"[VISUAL] Detected {len(links)} potential links (before dedup)")
        return self._remove_overlapping_elements(links, overlap_threshold=0.3)
    
    def detect_checkboxes(self, image: np.ndarray) -> List[Dict]:
        """
        Detect checkboxes (small squares).
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of checkbox dictionaries
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        checkboxes = []
        for idx, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Checkboxes are small squares (aspect ratio ~1.0)
            if 0.8 < aspect_ratio < 1.2 and 10 < w < 30 and 10 < h < 30:
                checkboxes.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': w * h,
                    'label': f'Checkbox {idx}',  # Will be filled by OCR
                    'type': 'checkbox',
                    'index': idx
                })
        
        logger.info(f"[VISUAL] Detected {len(checkboxes)} potential checkboxes (before dedup)")
        return self._remove_overlapping_elements(checkboxes, overlap_threshold=0.5)
    
    def detect_dropdowns(self, image: np.ndarray) -> List[Dict]:
        """
        Detect dropdown/select elements (rectangles with arrow indicator).
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of dropdown dictionaries
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        dropdowns = []
        for idx, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Dropdowns are similar to inputs but slightly different dimensions
            if 3.0 < aspect_ratio < 10.0 and 80 < w < 400 and 20 < h < 50 and w * h > 2000:
                dropdowns.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': w * h,
                    'label': f'Dropdown {idx}',  # Will be filled by OCR
                    'type': 'dropdown',
                    'index': idx
                })
        
        logger.info(f"[VISUAL] Detected {len(dropdowns)} potential dropdowns (before dedup)")
        return self._remove_overlapping_elements(dropdowns, overlap_threshold=0.4)
    
    def detect_all_elements(self, screenshot_data: str) -> Dict[str, List[Dict]]:
        """
        Detect all UI elements in a screenshot.
        
        Args:
            screenshot_data: Base64 encoded screenshot or file path
            
        Returns:
            Dictionary containing all detected elements by type
        """
        logger.info(f"[VISUAL] detect_all_elements() called with data length: {len(screenshot_data) if screenshot_data else 0}")
        image = self.load_screenshot(screenshot_data)
        
        if image is None:
            logger.error("[VISUAL] Failed to load screenshot - image is None!")
            return {'buttons': [], 'inputs': [], 'text_regions': []}
        
        logger.info(f"[VISUAL] Screenshot loaded successfully: shape={image.shape}")
        
        # Detect ALL actionable elements
        buttons = self.detect_buttons(image)
        inputs = self.detect_input_fields(image)
        links = self.detect_links(image)
        checkboxes = self.detect_checkboxes(image)
        dropdowns = self.detect_dropdowns(image)
        text_regions = self.detect_text_regions(image)
        
        logger.info(f"[VISUAL] Detected: {len(buttons)} buttons, {len(inputs)} inputs, {len(links)} links, {len(checkboxes)} checkboxes, {len(dropdowns)} dropdowns")
        
        return {
            'buttons': buttons,
            'inputs': inputs,
            'links': links,
            'checkboxes': checkboxes,
            'dropdowns': dropdowns,
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
