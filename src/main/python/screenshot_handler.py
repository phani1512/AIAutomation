"""
Screenshot API Handler for Multi-modal AI
Handles screenshot uploads and visual code generation endpoints
"""

from flask import Blueprint, request, jsonify
import logging
import base64
from visual_element_detector import VisualElementDetector
from multimodal_generator import MultiModalCodeGenerator

logger = logging.getLogger(__name__)

screenshot_bp = Blueprint('screenshot', __name__, url_prefix='/screenshot')

# Initialize visual components
visual_detector = VisualElementDetector()
multimodal_generator = MultiModalCodeGenerator(visual_detector)

@screenshot_bp.route('/analyze', methods=['POST'])
def analyze_screenshot():
    """
    Analyze a screenshot with professional QA features.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image or file_path",
        "intent": "Optional user description",
        "use_ocr": true,  // Enable OCR text extraction
        "generate_pom": false  // Generate Page Object Model
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        use_ocr = data.get('use_ocr', True)
        generate_pom = data.get('generate_pom', False)
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Analyze with professional features
        analysis = multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr, generate_pom
        )
        
        logger.info(f"[SCREENSHOT] Analyzed - found {analysis['total_elements']} elements (OCR: {use_ocr})")
        
        return jsonify(analysis), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/generate-code', methods=['POST'])
def generate_code_from_screenshot():
    """
    Generate test code from a screenshot.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image",
        "intent": "User description like 'Test login flow'",
        "test_name": "LoginTest"
    }
    
    Response:
    {
        "code": "Generated Python test code",
        "elements_detected": 10,
        "actions_generated": 5
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        test_name = data.get('test_name', 'VisualTest')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Generate test code
        code = multimodal_generator.generate_test_code_from_screenshot(
            screenshot, user_intent, test_name
        )
        
        # Get analysis for response
        analysis = multimodal_generator.analyze_screenshot(screenshot, user_intent)
        
        logger.info(f"[SCREENSHOT] Generated test code: {test_name}")
        
        return jsonify({
            'code': code,
            'elements_detected': analysis['total_elements'],
            'actions_generated': len(analysis['suggested_actions']),
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Code generation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/generate-from-sequence', methods=['POST'])
def generate_from_sequence():
    """
    Generate test code from a sequence of screenshots.
    
    Request JSON:
    {
        "screenshots": ["base64_1", "base64_2", ...],
        "descriptions": ["Step 1: Login", "Step 2: Navigate", ...]
    }
    
    Response:
    {
        "code": "Generated test code for complete flow",
        "total_steps": 3
    }
    """
    try:
        data = request.get_json()
        screenshots = data.get('screenshots', [])
        descriptions = data.get('descriptions', [])
        
        if not screenshots:
            return jsonify({'error': 'At least one screenshot is required'}), 400
        
        # Generate test code from sequence
        code = multimodal_generator.generate_from_screenshot_sequence(
            screenshots, descriptions
        )
        
        logger.info(f"[SCREENSHOT] Generated flow test from {len(screenshots)} screenshots")
        
        return jsonify({
            'code': code,
            'total_steps': len(screenshots)
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Sequence generation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/detect-elements', methods=['POST'])
def detect_elements():
    """
    Detect UI elements in a screenshot (visual only, no AI).
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image"
    }
    
    Response:
    {
        "buttons": [...],
        "inputs": [...],
        "text_regions": [...],
        "screenshot_width": 1920,
        "screenshot_height": 1080
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Detect elements
        elements = visual_detector.detect_all_elements(screenshot)
        
        logger.info(f"[SCREENSHOT] Detected {len(elements['buttons'])} buttons, "
                   f"{len(elements['inputs'])} inputs")
        
        return jsonify(elements), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Element detection error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/annotate', methods=['POST'])
def annotate_screenshot():
    """
    Annotate a screenshot with detected element bounding boxes.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image"
    }
    
    Response:
    {
        "annotated_screenshot": "base64_encoded_annotated_image",
        "elements": {...}
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Detect elements
        elements = visual_detector.detect_all_elements(screenshot)
        
        # Annotate screenshot
        import cv2
        import numpy as np
        from io import BytesIO
        from PIL import Image
        
        annotated_img = visual_detector.annotate_screenshot(elements)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', annotated_img)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info(f"[SCREENSHOT] Annotated screenshot with {len(elements['buttons'])} buttons")
        
        return jsonify({
            'annotated_screenshot': f'data:image/png;base64,{annotated_base64}',
            'elements': elements
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Annotation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for screenshot service."""
    return jsonify({
        'status': 'healthy',
        'service': 'screenshot-analyzer',
        'visual_detector': 'active',
        'multimodal_generator': 'active'
    }), 200
