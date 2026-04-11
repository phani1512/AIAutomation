"""
Trained Vision Model Detector
Uses your custom-trained deep learning model for accurate element detection
"""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)


class ElementDetectorModel(nn.Module):
    """Vision model for element detection - must match training architecture."""
    
    def __init__(self, num_classes=6):
        super(ElementDetectorModel, self).__init__()
        self.backbone = resnet18(weights=None)
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class TrainedVisionDetector:
    """Element detector using your custom trained vision model."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize detector with trained model.
        
        Args:
            model_path: Path to trained model .pth file
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_loaded = False
        
        # Index to element type mapping
        self.idx_to_type = {
            0: 'input',
            1: 'button',
            2: 'checkbox',
            3: 'link',
            4: 'select',
            5: 'textarea'
        }
        
        # Transform for inference
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Load model if path provided
        if model_path:
            self.load_model(model_path)
        else:
            # Try to find latest model
            self.auto_load_latest_model()
    
    def auto_load_latest_model(self):
        """Automatically load the latest trained model."""
        model_dir = 'trained_models'
        if not os.path.exists(model_dir):
            logger.warning("[TRAINED-VISION] No trained_models directory found")
            return
        
        # Find latest .pth file
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
        if not model_files:
            logger.warning("[TRAINED-VISION] No trained models found in trained_models/")
            return
        
        # Get most recent
        model_files.sort(reverse=True)
        latest_model = os.path.join(model_dir, model_files[0])
        
        self.load_model(latest_model)
    
    def load_model(self, model_path: str):
        """Load trained model from file."""
        try:
            logger.info(f"[TRAINED-VISION] Loading model from {model_path}")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Create model
            self.model = ElementDetectorModel(num_classes=6)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.model_loaded = True
            
            val_acc = checkpoint.get('val_acc', 0)
            logger.info(f"[TRAINED-VISION] ✅ Model loaded! Validation accuracy: {val_acc:.2f}%")
            
        except Exception as e:
            logger.error(f"[TRAINED-VISION] ❌ Failed to load model: {e}")
            self.model_loaded = False
    
    def detect_elements(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """
        Detect elements in screenshot using trained vision model.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Dict with detected inputs, buttons, etc.
        """
        if not self.model_loaded:
            logger.error("[TRAINED-VISION] No model loaded!")
            return {'inputs': [], 'buttons': [], 'checkboxes': [], 'links': []}
        
        logger.info("[TRAINED-VISION] ========== TRAINED VISION DETECTION ==========")
        
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Find candidate regions using edge detection
        regions = self._find_candidate_regions(image_rgb)
        logger.info(f"[TRAINED-VISION] Found {len(regions)} candidate regions")
        
        # Classify each region with trained model
        detected = {'inputs': [], 'buttons': [], 'checkboxes': [], 'links': [], 'selects': [], 'textareas': []}
        
        for region in regions:
            x, y, w, h = region
            
            # Extract region with padding
            padding = 20
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(image_rgb.shape[1], x + w + padding)
            y2 = min(image_rgb.shape[0], y + h + padding)
            
            region_img = image_rgb[y1:y2, x1:x2]
            
            if region_img.size == 0:
                continue
            
            # Classify with trained model
            elem_type, confidence = self._classify_region(region_img)
            
            # Only keep high confidence detections
            if confidence > 0.7:
                element = {
                    'type': elem_type,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'confidence': int(confidence * 100),
                    'trained_model': True
                }
                
                # Add to appropriate list
                if elem_type == 'input':
                    detected['inputs'].append(element)
                elif elem_type == 'button':
                    detected['buttons'].append(element)
                elif elem_type == 'checkbox':
                    detected['checkboxes'].append(element)
                elif elem_type == 'link':
                    detected['links'].append(element)
                elif elem_type == 'select':
                    detected['selects'].append(element)
                elif elem_type == 'textarea':
                    detected['textareas'].append(element)
                
                logger.info(f"[TRAINED-VISION] ✓ {elem_type} at ({x},{y}) confidence: {confidence:.2%}")
        
        # Log summary
        logger.info(f"[TRAINED-VISION] RESULTS:")
        logger.info(f"[TRAINED-VISION]   - {len(detected['inputs'])} inputs")
        logger.info(f"[TRAINED-VISION]   - {len(detected['buttons'])} buttons")
        logger.info(f"[TRAINED-VISION]   - {len(detected['checkboxes'])} checkboxes")
        logger.info(f"[TRAINED-VISION]   - {len(detected['links'])} links")
        
        return detected
    
    def _find_candidate_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Find candidate regions for element detection using CV."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Multi-scale edge detection
        edges1 = cv2.Canny(gray, 50, 150)
        edges2 = cv2.Canny(gray, 30, 100)
        edges = cv2.bitwise_or(edges1, edges2)
        
        # Dilate to connect nearby edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        height, width = image.shape[:2]
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size and aspect ratio
            aspect = w / h if h > 0 else 0
            area = w * h
            
            # Interactive elements are typically:
            # - Width: 50-800px
            # - Height: 15-100px
            # - Aspect ratio: 1:1 to 20:1
            if (50 < w < 800 and 15 < h < 100 and 
                0.5 < aspect < 20 and area > 1000):
                regions.append((x, y, w, h))
        
        return regions
    
    def _classify_region(self, region_img: np.ndarray) -> Tuple[str, float]:
        """Classify a region using trained model."""
        try:
            # Transform for model
            input_tensor = self.transform(region_img)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_batch)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            elem_type = self.idx_to_type.get(predicted.item(), 'unknown')
            confidence_val = confidence.item()
            
            return elem_type, confidence_val
            
        except Exception as e:
            logger.error(f"[TRAINED-VISION] Classification error: {e}")
            return 'unknown', 0.0


# For backward compatibility with local_ai_vision.py
class HybridVisionDetector:
    """
    Hybrid detector that uses trained model + OCR for best results.
    Combines deep learning vision with text understanding.
    """
    
    def __init__(self):
        self.trained_detector = TrainedVisionDetector()
        
        # Import OCR
        try:
            from .simple_ocr import SimpleOCR
            self.ocr = SimpleOCR()
        except:
            self.ocr = None
            logger.warning("[HYBRID-VISION] OCR not available")
    
    def analyze_screenshot(self, image: np.ndarray) -> Dict:
        """Analyze screenshot with trained model + OCR labels."""
        logger.info("[HYBRID-VISION] ========== HYBRID VISION ANALYSIS ==========")
        
        # Step 1: Detect elements with trained model
        detected = self.trained_detector.detect_elements(image)
        
        # Step 2: Extract text with OCR
        text_regions = []
        if self.ocr and self.ocr.available:
            text_regions = self.ocr.extract_all_text(image)
            logger.info(f"[HYBRID-VISION] Extracted {len(text_regions)} text regions")
        
        # Step 3: Match text to detected elements
        for elem_list in [detected['inputs'], detected['buttons']]:
            for elem in elem_list:
                nearby_text = self._find_nearby_text(elem, text_regions)
                if nearby_text:
                    elem['label'] = nearby_text['text']
                    elem['display_name'] = nearby_text['text']
                    elem['text'] = nearby_text['text']
                else:
                    elem['label'] = f"{elem['type'].title()} Field"
                    elem['display_name'] = elem['label']
                    elem['text'] = elem['label']
        
        logger.info("[HYBRID-VISION] Analysis complete!")
        
        return {
            'inputs': detected['inputs'],
            'buttons': detected['buttons'],
            'checkboxes': detected.get('checkboxes', []),
            'links': detected.get('links', []),
            'text_regions': text_regions,
            'context': {'type': 'form', 'expected_elements': []}
        }
    
    def _find_nearby_text(self, element: Dict, text_regions: List[Dict]) -> Optional[Dict]:
        """Find text label near element."""
        elem_x = element['center_x']
        elem_y = element['center_y']
        
        nearest = None
        min_distance = float('inf')
        
        for region in text_regions:
            dx = region['center_x'] - elem_x
            dy = region['center_y'] - elem_y
            distance = (dx**2 + dy**2) ** 0.5
            
            # Prefer text above or to the left
            if distance < min_distance and distance <= 100:
                if dy < 0 or (abs(dy) < 30 and dx < 0):
                    min_distance = distance
                    nearest = region
        
        return nearest
