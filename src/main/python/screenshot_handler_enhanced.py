"""
Enhanced Screenshot API Handler with Professional QA Features
Includes: OCR, POM generation, smart locators, test data generation
"""

from flask import Blueprint, request, jsonify
import logging
import base64
from visual_element_detector import VisualElementDetector
from multimodal_generator import MultiModalCodeGenerator
from test_data_generator import TestDataGenerator
from complete_test_generator import CompleteTestGenerator
from test_file_manager import TestFileManager

logger = logging.getLogger(__name__)

screenshot_bp = Blueprint('screenshot', __name__, url_prefix='/screenshot')

# Initialize components
visual_detector = VisualElementDetector()
multimodal_generator = MultiModalCodeGenerator(visual_detector)
test_data_gen = TestDataGenerator()
complete_test_gen = CompleteTestGenerator()
file_manager = TestFileManager()

@screenshot_bp.route('/analyze', methods=['POST'])
def analyze_screenshot():
    """
    COMPREHENSIVE SCREENSHOT ANALYSIS & AUTO-SAVE
    Analyzes screenshot, generates test suite, and SAVES to project automatically.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image",
        "intent": "Test scenario description",
        "language": "java" or "python" (default: "java"),
        "test_name": "LoginTest" (default: "ScreenshotTest"),
        "auto_save": true (default: true)
    }
    
    Returns complete test suite AND saves files to:
    - Java: src/test/java/com/testing/tests/
    - Python: tests/
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        language = data.get('language', 'java')
        test_name = data.get('test_name', 'ScreenshotTest')
        auto_save = data.get('auto_save', True)
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        logger.info(f"[SCREENSHOT] Analysis started - {language} - Auto-save: {auto_save}")
        
        # Full analysis with OCR and smart locators
        analysis = multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr=True, generate_pom=False
        )
        
        # Generate complete test suite
        test_suite = complete_test_gen.generate_complete_test_suite(
            analysis, language, test_name
        )
        
        # Generate test data for inputs
        field_data = {}
        for inp in analysis['elements'].get('inputs', []):
            field_name = inp.get('suggested_name', f"field_{inp.get('index', 0)}")
            field_data[field_name] = test_data_gen.generate_for_field(inp)
        
        logger.info(f"[SCREENSHOT] ✓ Generated {test_suite['test_count']} test cases")
        
        # Auto-save to project structure
        save_result = None
        if auto_save:
            try:
                save_result = file_manager.save_test_suite(test_suite, test_name)
                logger.info(f"[FILE-SAVE] ✓ Saved {len(save_result['files'])} files")
                logger.info(f"[FILE-SAVE] ✓ Run command: {save_result['execution']['command']}")
            except Exception as e:
                logger.error(f"[FILE-SAVE] Error saving files: {e}")
                save_result = {'status': 'error', 'message': str(e)}
        
        return jsonify({
            # Analysis
            'elements': analysis['elements'],
            'total_elements': analysis['total_elements'],
            'ocr_enabled': analysis['ocr_enabled'],
            
            # Complete Test Suite
            'test_suite': test_suite,
            
            # Test Data
            'test_data': field_data,
            
            # File Save Result (NEW!)
            'saved_files': save_result,
            
            # Summary
            'summary': {
                'buttons_count': len(analysis['elements'].get('buttons', [])),
                'inputs_count': len(analysis['elements'].get('inputs', [])),
                'test_cases_generated': test_suite['test_count'],
                'language': language,
                'framework': test_suite['framework'],
                'files_saved': len(save_result.get('files', {})) if save_result and save_result.get('status') == 'success' else 0,
                'ready_to_execute': save_result.get('ready_to_run', False) if save_result and save_result.get('status') == 'success' else False
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Analysis error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/generate-code', methods=['POST'])
def generate_code_from_screenshot():
    """Generate test code from screenshot."""
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
        
        # Get analysis
        analysis = multimodal_generator.analyze_screenshot(screenshot, user_intent, use_ocr=True)
        
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

@screenshot_bp.route('/generate-pom', methods=['POST'])
def generate_pom():
    """
    Generate Page Object Model from screenshot.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image",
        "intent": "Login page test",
        "language": "java" or "python",
        "page_name": "Login"
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        language = data.get('language', 'java')
        page_name = data.get('page_name', 'Test')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Analyze with POM generation
        analysis = multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr=True, generate_pom=True
        )
        
        pom_code = analysis.get(f'pom_{language}', '')
        
        # Debug logging
        buttons_count = len(analysis['elements'].get('buttons', []))
        inputs_count = len(analysis['elements'].get('inputs', []))
        logger.info(f"[SCREENSHOT] POM Generation - Buttons: {buttons_count}, Inputs: {inputs_count}, Total: {analysis['total_elements']}")
        logger.info(f"[SCREENSHOT] POM Code Length: {len(pom_code)} characters")
        
        if not pom_code:
            logger.warning(f"[SCREENSHOT] Empty POM code generated! Elements detected: {analysis['total_elements']}")
        
        logger.info(f"[SCREENSHOT] Generated {language} POM for {page_name}")
        
        return jsonify({
            'pom_code': pom_code,
            'language': language,
            'page_name': page_name,
            'elements_count': analysis['total_elements'],
            'buttons_count': buttons_count,
            'inputs_count': inputs_count
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] POM generation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/get-test-data', methods=['POST'])
def get_test_data():
    """
    Generate test data for detected form fields.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image",
        "intent": "Form test"
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Analyze with OCR
        analysis = multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr=True
        )
        
        # Generate test data for input fields
        field_data = {}
        scenarios = []
        
        for inp in analysis['elements'].get('inputs', []):
            field_name = inp.get('suggested_name', f"field_{inp.get('index', 0)}")
            field_data[field_name] = test_data_gen.generate_for_field(inp)
        
        # Generate data-driven scenarios
        if analysis['elements'].get('inputs'):
            scenarios = test_data_gen.generate_data_driven_scenarios(
                analysis['elements']['inputs']
            )
        
        logger.info(f"[SCREENSHOT] Generated test data for {len(field_data)} fields")
        
        return jsonify({
            'field_data': field_data,
            'scenarios': scenarios,
            'fields_count': len(field_data)
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Test data generation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/get-locator-strategies', methods=['POST'])
def get_locator_strategies():
    """
    Get smart locator strategies for specific element.
    
    Request JSON:
    {
        "screenshot": "base64_encoded_image",
        "intent": "Test description",
        "element_index": 0,
        "element_type": "button"
    }
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        element_index = data.get('element_index', 0)
        element_type = data.get('element_type', 'button')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Analyze screenshot
        analysis = multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr=True
        )
        
        # Get specific element
        elements = analysis['elements'].get(f"{element_type}s", [])
        if element_index >= len(elements):
            return jsonify({'error': 'Element index out of range'}), 400
        
        element = elements[element_index]
        strategies = element.get('locator_strategies', [])
        
        logger.info(f"[SCREENSHOT] Returned {len(strategies)} locator strategies")
        
        return jsonify({
            'element': element,
            'locator_strategies': strategies,
            'total_strategies': len(strategies)
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Locator strategies error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/detect-elements', methods=['POST'])
def detect_elements():
    """Raw element detection without code generation."""
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        elements = visual_detector.detect_all_elements(screenshot)
        
        logger.info(f"[SCREENSHOT] Detected {len(elements['buttons'])} buttons, {len(elements['inputs'])} inputs")
        
        return jsonify(elements), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Detection error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/annotate', methods=['POST'])
def annotate_screenshot():
    """Return annotated screenshot with element boxes."""
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Detect elements
        elements = visual_detector.detect_all_elements(screenshot)
        
        # Annotate screenshot
        import cv2
        annotated_img = visual_detector.annotate_screenshot(elements)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', annotated_img)
        annotated_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info(f"[SCREENSHOT] Annotated with {len(elements['buttons'])} buttons")
        
        return jsonify({
            'annotated_screenshot': f'data:image/png;base64,{annotated_base64}',
            'elements': elements
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Annotation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/generate-from-sequence', methods=['POST'])
def generate_from_sequence():
    """Generate end-to-end test from sequence of screenshots."""
    try:
        data = request.get_json()
        screenshots = data.get('screenshots', [])
        user_intent = data.get('intent', '')
        test_name = data.get('test_name', 'SequenceTest')
        
        if not screenshots or len(screenshots) == 0:
            return jsonify({'error': 'At least one screenshot is required'}), 400
        
        # Analyze each screenshot
        steps = []
        for idx, screenshot in enumerate(screenshots):
            analysis = multimodal_generator.analyze_screenshot(screenshot, user_intent, use_ocr=True)
            steps.append({
                'step': idx + 1,
                'elements': analysis['elements'],
                'actions': analysis['suggested_actions']
            })
        
        # Generate multi-step test
        code = multimodal_generator.generate_multi_step_test(steps, user_intent, test_name)
        
        logger.info(f"[SCREENSHOT] Generated {len(steps)}-step test")
        
        return jsonify({
            'code': code,
            'steps': len(steps),
            'total_actions': sum(len(s['actions']) for s in steps)
        }), 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Sequence generation error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    ocr_info = multimodal_generator.ocr_extractor.get_engine_info()
    test_summary = file_manager.get_test_summary()
    
    return jsonify({
        'status': 'healthy',
        'service': 'screenshot-analyzer-pro',
        'ocr_engine': ocr_info,
        'saved_tests': test_summary,
        'features': {
            'visual_detection': 'active',
            'ocr_extraction': 'active',
            'ocr_mode': ocr_info['mode'],
            'pom_generation': 'active',
            'smart_locators': 'active',
            'test_data_generation': 'active',
            'auto_save': 'active',
            'xpath_generation': 'active',
            'trained_ai_model': multimodal_generator.inference_model is not None,
            'external_dependencies': ocr_info['dependencies']
        }
    }), 200

@screenshot_bp.route('/saved-tests', methods=['GET'])
def get_saved_tests():
    """Get list of all saved tests."""
    try:
        summary = file_manager.get_test_summary()
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"[SAVED-TESTS] Error: {e}")
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/test-index', methods=['GET'])
def create_test_index():
    """Create and return HTML index of all saved tests."""
    try:
        index_path = file_manager.create_test_index()
        return jsonify({
            'status': 'success',
            'index_path': index_path,
            'message': f'Test index created at: {index_path}'
        }), 200
    except Exception as e:
        logger.error(f"[TEST-INDEX] Error: {e}")
        return jsonify({'error': str(e)}), 500
