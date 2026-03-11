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
from comprehensive_test_generator import ComprehensiveTestGenerator
from simple_screenshot_test_generator import SimpleScreenshotTestGenerator
from test_file_manager import TestFileManager

logger = logging.getLogger(__name__)

screenshot_bp = Blueprint('screenshot', __name__, url_prefix='/screenshot')

# Initialize components
visual_detector = VisualElementDetector()
multimodal_generator = MultiModalCodeGenerator(visual_detector)
test_data_gen = TestDataGenerator()
comprehensive_test_gen = ComprehensiveTestGenerator()
simple_test_gen = SimpleScreenshotTestGenerator()  # NEW: Simple generator without POM
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
        "test_name": "MyTest" (default: "ScreenshotTest"),
        "auto_save": true (default: true)
    }
    
    Returns complete test suite AND saves files to:
    - Java: src/test/java/com/testing/tests/
    - Python: tests/
    """
    try:
        # CRITICAL: Create FRESH generator instances for each request to avoid state caching
        from visual_element_detector import VisualElementDetector
        from multimodal_generator import MultiModalCodeGenerator
        from universal_test_generator import UniversalTestGenerator
        
        logger.info("[SCREENSHOT] Creating fresh generator instances for new request")
        fresh_visual_detector = VisualElementDetector()
        fresh_multimodal_generator = MultiModalCodeGenerator(fresh_visual_detector)
        fresh_direct_test_gen = UniversalTestGenerator()  # CHANGED: Use universal generator for any page type
        
        # Add unique timestamp to verify no caching
        import time
        request_timestamp = int(time.time() * 1000)
        logger.info(f"[SCREENSHOT] Request timestamp: {request_timestamp}")
        logger.info(f"[SCREENSHOT] Fresh generator instance IDs: visual={id(fresh_visual_detector)}, modal={id(fresh_multimodal_generator)}, direct={id(fresh_direct_test_gen)}")
        
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        language = data.get('language', 'java')
        test_name = data.get('test_name', 'ScreenshotTest')
        auto_save = data.get('auto_save', True)
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # DIAGNOSTIC: Check base64 data
        print("\n" + "="*80)
        print(f"[DIAGNOSTIC] Screenshot data received:")
        print(f"[DIAGNOSTIC]   Type: {type(screenshot)}")
        print(f"[DIAGNOSTIC]   Length: {len(screenshot) if screenshot else 0}")
        print(f"[DIAGNOSTIC]   First 100 chars: {screenshot[:100] if screenshot else 'EMPTY'}")
        print(f"[DIAGNOSTIC]   Starts with 'data:': {screenshot.startswith('data:') if screenshot else False}")
        print(f"[DIAGNOSTIC]   User intent: {user_intent}")
        print(f"[DIAGNOSTIC]   Test name: {test_name}")
        print("="*80 + "\n")
        
        logger.info(f"[SCREENSHOT] Analysis started - {language} - Auto-save: {auto_save}")
        logger.info(f"[SCREENSHOT] Using FRESH generators (no cached state)")
        
        # Full analysis with OCR and smart locators using FRESH instance
        analysis = fresh_multimodal_generator.analyze_screenshot(
            screenshot, user_intent, use_ocr=True, generate_pom=False
        )
        
        logger.info(f"[SCREENSHOT] Analysis complete - Elements detected:")
        logger.info(f"[SCREENSHOT]   Buttons: {len(analysis['elements'].get('buttons', []))}")
        logger.info(f"[SCREENSHOT]   Inputs: {len(analysis['elements'].get('inputs', []))}")
        
        # DEBUG: Log OCR labels found
        for idx, inp in enumerate(analysis['elements'].get('inputs', [])):
            label = inp.get('label', 'NO LABEL')
            logger.info(f"[DEBUG] Input {idx}: label='{label}'")
        for idx, btn in enumerate(analysis['elements'].get('buttons', [])):
            text = btn.get('text', 'NO TEXT')
            logger.info(f"[DEBUG] Button {idx}: text='{text}'")
        
        # Validate we have elements to work with
        if analysis['total_elements'] == 0:
            logger.warning(f"[SCREENSHOT] No elements detected in screenshot!")
            logger.warning(f"[SCREENSHOT] Detection results: buttons={len(analysis['elements'].get('buttons', []))}, inputs={len(analysis['elements'].get('inputs', []))}, text_regions={len(analysis['elements'].get('text_regions', []))}")
            logger.warning(f"[SCREENSHOT] Screenshot dimensions: {analysis.get('screenshot_width', 0)}x{analysis.get('screenshot_height', 0)}")
            return jsonify({
                'error': 'No UI elements detected in screenshot',
                'suggestion': 'Please upload a screenshot showing buttons, input fields, links, checkboxes, or other UI elements. The screenshot should be clear and show visible interactive elements.',
                'debug': {
                    'dimensions': f"{analysis.get('screenshot_width', 0)}x{analysis.get('screenshot_height', 0)}",
                    'buttons': len(analysis['elements'].get('buttons', [])),
                    'inputs': len(analysis['elements'].get('inputs', [])),
                    'text_regions': len(analysis['elements'].get('text_regions', []))
                }
            }), 400
        
        # Generate UNIVERSAL test suite for ANY page type (dynamic test count based on detected elements)
        logger.info(f"[SCREENSHOT] Using UNIVERSAL generator for dynamic test generation...")
        test_suite = fresh_direct_test_gen.generate_tests(
            analysis['elements'],
            test_name=test_name,
            url='YOUR_URL_HERE'
        )
        
        logger.info(f"[SCREENSHOT] ✓ Generated {test_suite['test_count']} tests dynamically based on detected elements")
        logger.info(f"[SCREENSHOT]   Framework: {test_suite.get('framework', 'Unknown')}")
        logger.info(f"[SCREENSHOT]   Has POM: {test_suite.get('has_pom', False)}")
        
        # Generate test data for inputs
        field_data = {}
        for inp in analysis['elements'].get('inputs', []):
            field_name = inp.get('suggested_name', f"field_{inp.get('index', 0)}")
            field_data[field_name] = test_data_gen.generate_for_field(inp)
        
        logger.info(f"[SCREENSHOT] ✓ Generated {test_suite['test_count']} test cases (Direct format, no POM)")
        
        # Auto-save to project structure - DISABLED to prevent POM transformation
        # The DirectTestGenerator already returns the correct format
        save_result = None
        if auto_save:
            try:
                # Save ONLY the raw test_class without transformation
                import os
                test_file_path = os.path.join('target', 'generated-tests', f'{test_name}.java')
                os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(test_suite['test_class'])
                save_result = {
                    'status': 'success',
                    'files': [test_file_path],
                    'execution': {'command': f'mvn test -Dtest={test_name}'}
                }
                logger.info(f"[FILE-SAVE] ✓ Saved raw test class to {test_file_path}")
            except Exception as e:
                logger.error(f"[FILE-SAVE] Error saving files: {e}")
                save_result = {'status': 'error', 'message': str(e)}
        
        # Build actionable elements list for user selection
        actionable_elements = {
            'inputs': [{'id': f'input_{i}', 'name': inp.get('label', inp.get('text', f'Input {i+1}')), 'type': 'input'} 
                      for i, inp in enumerate(analysis['elements'].get('inputs', []))],
            'buttons': [{'id': f'button_{i}', 'name': btn.get('text', btn.get('label', f'Button {i+1}')), 'type': 'button'} 
                       for i, btn in enumerate(analysis['elements'].get('buttons', []))],
            'links': [{'id': f'link_{i}', 'name': link.get('text', f'Link {i+1}'), 'type': 'link'} 
                     for i, link in enumerate(analysis['elements'].get('links', []))],
            'checkboxes': [{'id': f'checkbox_{i}', 'name': chk.get('label', f'Checkbox {i+1}'), 'type': 'checkbox'} 
                          for i, chk in enumerate(analysis['elements'].get('checkboxes', []))],
            'dropdowns': [{'id': f'dropdown_{i}', 'name': dd.get('label', f'Dropdown {i+1}'), 'type': 'dropdown'} 
                         for i, dd in enumerate(analysis['elements'].get('dropdowns', []))]
        }
        
        # Create response with cache-busting headers
        response_data = {
            # Analysis
            'elements': analysis['elements'],
            'total_elements': analysis['total_elements'],
            'ocr_enabled': analysis['ocr_enabled'],
            'suggested_actions': analysis.get('suggested_actions', []),
            'descriptions': analysis.get('descriptions', {}),
            'text_regions': analysis.get('text_regions', []),
            
            # NEW: Actionable elements with OCR names for user selection
            'actionable_elements': actionable_elements,
            
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
            },
            
            # CRITICAL: Add unique timestamp to bust ALL caches
            'generated_at': request_timestamp,
            'cache_buster': f"fresh-{request_timestamp}"
        }
        
        # Create response with aggressive cache-busting headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Timestamp'] = str(request_timestamp)
        response.headers['ETag'] = f'"{request_timestamp}"'
        
        logger.info(f"[SCREENSHOT] Response generated at {request_timestamp} with cache-buster headers")
        
        return response, 200
        
    except Exception as e:
        logger.error(f"[SCREENSHOT] Analysis error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/get-actionable-elements', methods=['POST'])
def get_actionable_elements():
    """
    Get ALL actionable elements from screenshot for user selection.
    Returns elements with actual OCR names - user can choose which to test.
    """
    try:
        from visual_element_detector import VisualElementDetector
        from multimodal_generator import MultiModalCodeGenerator
        
        logger.info("[ACTIONABLE] Extracting all actionable elements")
        fresh_visual_detector = VisualElementDetector()
        fresh_multimodal_generator = MultiModalCodeGenerator(fresh_visual_detector)
        
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Get analysis with OCR
        analysis = fresh_multimodal_generator.analyze_screenshot(screenshot, user_intent, use_ocr=True)
        
        # Extract ALL actionable elements with their names
        actionable_elements = {
            'inputs': [],
            'buttons': [],
            'links': [],
            'checkboxes': [],
            'dropdowns': []
        }
        
        # Process inputs with OCR labels
        for idx, inp in enumerate(analysis['elements'].get('inputs', [])):
            actionable_elements['inputs'].append({
                'id': f'input_{idx}',
                'type': 'input',
                'name': inp.get('label', inp.get('text', f'Input Field {idx+1}')),
                'position': inp.get('position', {}),
                'locator_strategies': inp.get('locator_strategies', []),
                'suggested_name': inp.get('suggested_name', f'input{idx}')
            })
        
        # Process buttons with OCR text
        for idx, btn in enumerate(analysis['elements'].get('buttons', [])):
            actionable_elements['buttons'].append({
                'id': f'button_{idx}',
                'type': 'button',
                'name': btn.get('text', btn.get('label', f'Button {idx+1}')),
                'position': btn.get('position', {}),
                'locator_strategies': btn.get('locator_strategies', []),
                'suggested_name': btn.get('suggested_name', f'button{idx}')
            })
        
        # Process links
        for idx, link in enumerate(analysis['elements'].get('links', [])):
            actionable_elements['links'].append({
                'id': f'link_{idx}',
                'type': 'link',
                'name': link.get('text', link.get('label', f'Link {idx+1}')),
                'position': link.get('position', {}),
                'suggested_name': f'link{idx}'
            })
        
        # Process checkboxes
        for idx, chk in enumerate(analysis['elements'].get('checkboxes', [])):
            actionable_elements['checkboxes'].append({
                'id': f'checkbox_{idx}',
                'type': 'checkbox',
                'name': chk.get('label', f'Checkbox {idx+1}'),
                'position': chk.get('position', {}),
                'suggested_name': f'checkbox{idx}'
            })
        
        # Process dropdowns
        for idx, dd in enumerate(analysis['elements'].get('dropdowns', [])):
            actionable_elements['dropdowns'].append({
                'id': f'dropdown_{idx}',
                'type': 'dropdown',
                'name': dd.get('label', f'Dropdown {idx+1}'),
                'position': dd.get('position', {}),
                'suggested_name': f'dropdown{idx}'
            })
        
        total_count = sum(len(v) for v in actionable_elements.values())
        
        logger.info(f"[ACTIONABLE] Found {total_count} total elements: "
                   f"{len(actionable_elements['inputs'])} inputs, "
                   f"{len(actionable_elements['buttons'])} buttons, "
                   f"{len(actionable_elements['links'])} links, "
                   f"{len(actionable_elements['checkboxes'])} checkboxes, "
                   f"{len(actionable_elements['dropdowns'])} dropdowns")
        
        return jsonify({
            'status': 'success',
            'actionable_elements': actionable_elements,
            'total_count': total_count,
            'summary': {
                'inputs': len(actionable_elements['inputs']),
                'buttons': len(actionable_elements['buttons']),
                'links': len(actionable_elements['links']),
                'checkboxes': len(actionable_elements['checkboxes']),
                'dropdowns': len(actionable_elements['dropdowns'])
            },
            'message': f'Found {total_count} actionable elements. Select which ones to generate tests for.'
        }), 200
        
    except Exception as e:
        logger.error(f"[ACTIONABLE] Error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@screenshot_bp.route('/generate-code', methods=['POST'])
def generate_code_from_screenshot():
    """
    Generate test code from screenshot.
    Can accept selected_elements to generate tests only for specific elements.
    """
    try:
        # CRITICAL: Create FRESH UniversalTestGenerator
        from visual_element_detector import VisualElementDetector
        from multimodal_generator import MultiModalCodeGenerator
        from universal_test_generator import UniversalTestGenerator
        
        logger.info("[GENERATE-CODE] Creating fresh UniversalTestGenerator for any page type")
        fresh_visual_detector = VisualElementDetector()
        fresh_multimodal_generator = MultiModalCodeGenerator(fresh_visual_detector)
        fresh_direct_test_gen = UniversalTestGenerator()
        
        data = request.get_json()
        screenshot = data.get('screenshot')
        user_intent = data.get('intent', '')
        test_name = data.get('test_name', 'GeneratedTest')
        selected_elements = data.get('selected_elements', None)  # Optional: user can select specific elements
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        # Get analysis using FRESH instances
        analysis = fresh_multimodal_generator.analyze_screenshot(screenshot, user_intent, use_ocr=True)
        
        # If user selected specific elements, filter to only those
        elements_to_test = analysis['elements']
        if selected_elements:
            logger.info(f"[GENERATE-CODE] User selected specific elements: {selected_elements}")
            elements_to_test = self._filter_selected_elements(analysis['elements'], selected_elements)
        
        # Generate UNIVERSAL tests for ANY page type (dynamic test count based on elements)
        test_suite = fresh_direct_test_gen.generate_tests(
            elements_to_test,
            test_name,
            'YOUR_URL_HERE'
        )
        
        logger.info(f"[GENERATE-CODE] Generated {test_suite['test_count']} tests dynamically (Universal format for any page)")
        
        response_data = {
            'code': test_suite['test_class'],  # RAW test class code
            'test_suite': test_suite,
            'elements_detected': analysis['total_elements'],
            'elements_tested': sum(len(v) for v in elements_to_test.values()),
            'actions_generated': test_suite['test_count'],  # Dynamic count based on elements
            'analysis': analysis
        }
        
        # Add cache-busting headers
        response = jsonify(response_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 200
        
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
        "intent": "Test page functionality",
        "language": "java" or "python",
        "page_name": "Page"
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

@screenshot_bp.route('/debug', methods=['POST'])
def debug_screenshot():
    """
    DEBUG ENDPOINT - Detailed diagnostic information
    Helps troubleshoot screenshot analysis and code generation issues
    """
    try:
        data = request.get_json()
        screenshot = data.get('screenshot')
        
        if not screenshot:
            return jsonify({'error': 'Screenshot data is required'}), 400
        
        result = {'status': 'analyzing', 'steps': []}
        
        # Step 1: Image loading
        try:
            image_array = visual_detector.load_screenshot(screenshot)
            result['steps'].append({
                'step': '1. Image Loading',
                'status': '✓ success',
                'details': f'Shape: {image_array.shape}'
            })
        except Exception as e:
            result['steps'].append({'step': '1. Image Loading', 'status': '✗ failed', 'error': str(e)})
            return jsonify(result), 500
        
        # Step 2: Element detection
        try:
            elements = visual_detector.detect_all_elements(screenshot)
            btn_count = len(elements.get('buttons', []))
            inp_count = len(elements.get('inputs', []))
            result['steps'].append({
                'step': '2. Element Detection',
                'status': '✓ success',
                'details': f'Buttons: {btn_count}, Inputs: {inp_count}'
            })
        except Exception as e:
            result['steps'].append({'step': '2. Element Detection', 'status': '✗ failed', 'error': str(e)})
            return jsonify(result), 500
        
        # Step 3: Analysis
        try:
            analysis = multimodal_generator.analyze_screenshot(screenshot, 'debug test', use_ocr=True)
            result['steps'].append({
                'step': '3. Full Analysis',
                'status': '✓ success',
                'details': f'Total elements: {analysis["total_elements"]}, OCR: {analysis["ocr_enabled"]}'
            })
        except Exception as e:
            result['steps'].append({'step': '3. Full Analysis', 'status': '✗ failed', 'error': str(e)})
        
        # Step 4: Code generation
        try:
            test_suite = complete_test_gen.generate_complete_test_suite(analysis, 'java', 'DebugTest')
            test_class = test_suite.get('test_class', '')
            issues = []
            if 'unknown' in test_class.lower():
                issues.append('⚠ Contains "unknown" locators')
            if len(test_class) < 500:
                issues.append('⚠ Code seems too short')
            result['steps'].append({
                'step': '4. Code Generation',
                'status': '✓ success',
                'details': f'Tests: {test_suite["test_count"]}, Has POM: {test_suite.get("has_pom", False)}, Code length: {len(test_class)} chars'
            })
            result['issues'] = issues if issues else ['✓ No issues']
            result['code_preview'] = page_obj[:400] + '...'
        except Exception as e:
            result['steps'].append({'step': '4. Code Generation', 'status': '✗ failed', 'error': str(e)})
        
        result['status'] = 'complete'
        return jsonify(result), 200
        
    except Exception as e:
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
