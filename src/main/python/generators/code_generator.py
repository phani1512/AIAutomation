"""
Test code generation for Python and Java.

REFACTORING STATUS:
- PHASE 2 COMPLETE: All functions delegate to modular components
- PHASE 3 READY: ~800 lines of _ORIGINAL backup functions can be removed once fully tested
- Current line count: 1849 lines (1000 lines active code, 800 lines backups)
"""
import re
import logging
from flask import request, jsonify
from typing import Dict, List, Tuple, Any, Optional

# Import modular components (Phase 2: Integration COMPLETE)
from code_generation.field_analyzer import FieldAnalyzer
from code_generation.test_data_generator import TestDataGenerator
from code_generation.context_analyzer import ContextAnalyzer
from code_generation.semantic_modifier import SemanticModifier

def fix_locator_quotes(code):
    """Fix quote issues in find_element_safe calls to avoid syntax errors.
    
    Converts: find_element_safe("By.id("email")")
    To: find_element_safe('By.id("email")')
    
    Handles nested parentheses in XPath expressions.
    """
    import re
    
    # Log original code sample for debugging
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if 'find_element_safe' in line and 'By.' in line:
            logging.info(f"[QUOTE-FIX] BEFORE line {i}: {line.strip()}")
    
    # Strategy: Find find_element_safe calls and properly balance parentheses
    result = []
    i = 0
    while i < len(code):
        # Look for find_element_safe(
        if code[i:i+19] == 'find_element_safe(':
            # Found it, now find the matching closing parenthesis
            start = i + 18  # Position of opening (
            paren_count = 1
            j = start + 1
            
            # Scan forward to find matching )
            while j < len(code) and paren_count > 0:
                if code[j] == '(':
                    paren_count += 1
                elif code[j] == ')':
                    paren_count -= 1
                j += 1
            
            if paren_count == 0:
                # Found matching ), extract the content
                inner_content = code[start+1:j-1].strip()
                
                # Remove existing quotes at start/end (including triple quotes)
                if inner_content.startswith('"""') and inner_content.endswith('"""'):
                    inner_content = inner_content[3:-3]
                elif inner_content.startswith("'''") and inner_content.endswith("'''"):
                    inner_content = inner_content[3:-3]
                elif (inner_content.startswith('"') and inner_content.endswith('"')) or \
                   (inner_content.startswith("'") and inner_content.endswith("'")):
                    inner_content = inner_content[1:-1]
                
                # Remove escaped quotes if present
                inner_content = inner_content.replace("\\'", "'")
                
                # Build the fixed call with single quotes
                fixed = f"find_element_safe('{inner_content}')"
                logging.info(f"[QUOTE-FIX] Fixed: {code[i:j]} -> {fixed}")
                result.append(fixed)
                i = j
                continue
        
        result.append(code[i])
        i += 1
    
    code = ''.join(result)
    
    # Log fixed code sample
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if 'find_element_safe' in line and 'By.' in line:
            logging.info(f"[QUOTE-FIX] AFTER line {i}: {line.strip()}")
    
    return code

def _infer_action_type_from_prompt(prompt, code=''):
    """Infer action type from prompt text and code for BUILDER test case steps ONLY.
    
    IMPORTANT: This function is ONLY called when converting Builder test cases to session format.
    Recorder sessions already have action_type set by recorder_handler.py and do NOT use this.
    
    Args:
        prompt: The prompt/action description from Builder
        code: The generated code (if available) from Builder
        
    Returns:
        str: The inferred action_type (click, input, select, etc.)
    """
    if not prompt:
        return 'click'  # Default fallback
    
    prompt_lower = prompt.lower()
    code_lower = code.lower() if code else ''
    
    # Check for input actions
    if any(keyword in prompt_lower for keyword in ['enter', 'type', 'fill', 'input', 'write']):
        # Check if it's also clicking first (click_and_input)
        if any(keyword in prompt_lower for keyword in ['click', 'tap']) or \
           ('click' in code_lower and ('send_keys' in code_lower or 'type' in code_lower)):
            return 'click_and_input'
        return 'input'
    
    # Check for select/dropdown actions
    if any(keyword in prompt_lower for keyword in ['select', 'choose', 'dropdown', 'option']):
        return 'select'
    
    # Check for scroll actions
    if 'scroll' in prompt_lower:
        return 'scroll'
    
    # Check for file upload
    if any(keyword in prompt_lower for keyword in ['upload', 'file', 'attach']):
        return 'upload_file'
    
    # Check for drag and drop
    if 'drag' in prompt_lower or 'drop' in prompt_lower:
        return 'drag_and_drop'
    
    # Check for verification
    if any(keyword in prompt_lower for keyword in ['verify', 'check', 'assert', 'confirm', 'validate']):
        return 'verify_message'
    
    # Default to click for everything else
    return 'click'

def _extract_locator_and_value_from_code(code, action_type):
    """Extract locator and value from Builder-generated Selenium code.
    
    Args:
        code: The generated Selenium code from Builder
        action_type: The inferred action type
        
    Returns:
        tuple: (suggested_locator, value)
    """
    import re
    
    if not code:
        return '', ''
    
    # Builder code uses CSS selector arrays - extract first valid selector
    # Pattern: selectors = ["input[id='producer-email']", "input[type='email']", ...]
    # Or: selectors = ['sign-in-button', 'button', ...]
    
    # Use a more robust approach: find the array, then extract first complete selector
    # The code might have comments and whitespace before selectors line
    selector_array_pattern = r'selectors\s*=\s*\[(.*?)\]'
    selector_match = re.search(selector_array_pattern, code, re.DOTALL | re.MULTILINE)
    
    suggested_locator = ''
    if selector_match:
        selectors_str = selector_match.group(1).strip()
        
        # Remove any newlines and extra whitespace from the selectors string
        selectors_str = ' '.join(selectors_str.split())
        
        # Extract first selector more carefully - handle nested quotes
        # Match either "..." or '...' but capture the content properly
        css_selector = ''
        if selectors_str.startswith('"'):
            # Array uses double quotes: ["selector1", "selector2"]
            # Extract content between first " and second " (before comma)
            first_end = selectors_str.find('"', 1)
            if first_end > 0:
                css_selector = selectors_str[1:first_end]
        elif selectors_str.startswith("'"):
            # Array uses single quotes: ['selector1', 'selector2']
            first_end = selectors_str.find("'", 1)
            if first_end > 0:
                css_selector = selectors_str[1:first_end]
        
        if css_selector:
            # Convert CSS selector to By.CSS_SELECTOR format
            # Escape any quotes in the selector for Python string
            css_selector_escaped = css_selector.replace('"', '\\"')
            suggested_locator = f'By.CSS_SELECTOR("{css_selector_escaped}")'
    
    # For builder, value should come from step's value field, not code
    # (code has {VALUE} placeholder)
    value = ''
    
    return suggested_locator, value


def generate_test_from_actions(actions: List[Dict], test_name: str, url: str = '', compact_mode: bool = True) -> str:
    """
    Generate Python test code from recorded actions.
    Used when saving tests to avoid regenerating code on every view.
    
    Args:
        actions: List of recorded action dictionaries
        test_name: Name of the test
        url: Starting URL
        compact_mode: If True, generates compact code (default: True)
        
    Returns:
        Python test code as string
    """
    from datetime import datetime
    
    lines = []
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', test_name.lower())
    
    # Minimal compact header
    lines.append(f'"""')
    lines.append(f'Test: {test_name}')
    lines.append(f'Generated: {datetime.now().isoformat()}')
    lines.append(f'"""')
    lines.append('')
    lines.append('import pytest')
    lines.append('from selenium import webdriver')
    lines.append('from selenium.webdriver.common.by import By')
    lines.append('from selenium.webdriver.support.ui import WebDriverWait')
    lines.append('from selenium.webdriver.support import expected_conditions as EC')
    lines.append('')
    
    # Compact fixture
    lines.append('@pytest.fixture')
    lines.append('def driver():')
    lines.append('    driver = webdriver.Chrome()')
    lines.append('    driver.maximize_window()')
    lines.append('    yield driver')
    lines.append('    driver.quit()')
    lines.append('')
    
    # Test function
    lines.append(f'def test_{safe_name}(driver):')
    lines.append(f'    """Recorded test: {test_name}"""')
    
    if url:
        lines.append(f'    driver.get("{url}")')
    
    # Generate code for each action
    for idx, action in enumerate(actions, 1):
        action_type = action.get('action_type', 'click')
        element = action.get('element', {})
        value = action.get('value', '')
        suggested_locator = action.get('suggested_locator', '')
        
        lines.append(f'    # Step {idx}: {action_type}')
        
        # Extract locator strategy and value from suggested_locator
        if suggested_locator:
            # Parse "By.id("email")" format
            if 'By.id(' in suggested_locator:
                locator_value = re.search(r'By\.id\(["\']([^"\']+)["\']\)', suggested_locator)
                if locator_value:
                    lines.append(f'    element = driver.find_element(By.ID, "{locator_value.group(1)}")')
            elif 'By.name(' in suggested_locator:
                locator_value = re.search(r'By\.name\(["\']([^"\']+)["\']\)', suggested_locator)
                if locator_value:
                    lines.append(f'    element = driver.find_element(By.NAME, "{locator_value.group(1)}")')
            elif 'By.xpath(' in suggested_locator or 'By.XPATH(' in suggested_locator:
                locator_value = re.search(r'By\.(?:xpath|XPATH)\(["\']([^"\']+)["\']\)', suggested_locator)
                if locator_value:
                    xpath = locator_value.group(1).replace('"', '\\"')
                    lines.append(f'    element = driver.find_element(By.XPATH, "{xpath}")')
            elif 'By.CSS_SELECTOR(' in suggested_locator:
                locator_value = re.search(r'By\.CSS_SELECTOR\(["\']([^"\']+)["\']\)', suggested_locator)
                if locator_value:
                    css = locator_value.group(1).replace('"', '\\"')
                    lines.append(f'    element = driver.find_element(By.CSS_SELECTOR, "{css}")')
            else:
                # Fallback: use the locator string as-is
                lines.append(f'    # {suggested_locator}')
                lines.append(f'    pass')
                continue
            
            # Add action
            if action_type == 'click':
                lines.append(f'    element.click()')
            elif action_type in ['click_and_input', 'type', 'input']:
                if value:
                    lines.append(f'    element.clear()')
                    lines.append(f'    element.send_keys("{value}")')
            elif action_type == 'select':
                lines.append(f'    from selenium.webdriver.support.ui import Select')
                lines.append(f'    select = Select(element)')
                if value:
                    lines.append(f'    select.select_by_visible_text("{value}")')
        else:
            lines.append(f'    # No locator available for this action')
            lines.append(f'    pass')
        
        lines.append('')
    
    return '\n'.join(lines)


def generate_test_code(recorded_sessions):
    """Generate test code from recorded session or test case."""
    session_id = request.json.get('session_id')
    test_case_id = request.json.get('test_case_id')
    session_data = request.json.get('session_data')  # NEW: Accept pre-loaded session data
    
    # Accept either session_id or test_case_id
    identifier = session_id or test_case_id
    
    if not identifier:
        return jsonify({'success': False, 'error': 'Session ID or Test Case ID is required'}), 400
    
    # First check if session_data was provided (for saved tests)
    session = None
    if session_data:
        session = session_data
        session['source'] = 'recorder'
        logging.info(f"[GENERATE] ✓ Using provided session data for: {identifier}")
        logging.info(f"[GENERATE] Session has {len(session.get('actions', []))} actions")
    # Then check in-memory sessions (RECORDER ACTIVE SESSIONS)
    elif identifier in recorded_sessions:
        session = recorded_sessions[identifier]
        session['source'] = 'recorder'  # Track that this is from Recorder
        logging.info(f"[GENERATE] ✓ Found RECORDER session in memory: {identifier}")
        logging.info(f"[GENERATE] Session has {len(session.get('actions', []))} actions from RECORDER")
    else:
        # Since semantic analysis uses test suite (builder + recorder saved tests),
        # try BUILDER FIRST to avoid unnecessary recorder warnings
        try:
            from test_management.test_case_builder import get_test_case_builder
            builder = get_test_case_builder()
            test_case_obj = builder.load_test_case(identifier)
            
            if test_case_obj:
                # Found in builder - convert to session format
                logging.info(f"[GENERATE] ✓ Found BUILDER test case: {identifier} - starting conversion")
                test_case_dict = test_case_obj.to_dict()
                
                # Get URL from test case or try to extract from first step
                url = test_case_dict.get('url', '')
                if not url:
                    # Try to extract from first step's code
                    steps = test_case_dict.get('steps', [])
                    if steps and len(steps) > 0:
                        first_code = steps[0].get('code', '')
                        import re
                        url_match = re.search(r'driver\.get\(["\']([^"\']+)["\']\)', first_code)
                        if url_match:
                            url = url_match.group(1)
                            logging.info(f"[GENERATE] Extracted URL from code: {url}")
                
                if not url:
                    logging.warning(f"[GENERATE] No URL found for BUILDER test case: {identifier}")
                
                session = {
                    'id': identifier,
                    'name': test_case_dict.get('name', 'Test'),
                    'url': url,
                    'actions': [],
                    'source': 'builder'  # Track that this is from Builder
                }
                
                # Convert steps to actions format (ONLY FOR BUILDER)
                steps = test_case_dict.get('steps', [])
                logging.info(f"[GENERATE] Converting {len(steps)} BUILDER steps to action format")
                
                # Extract URL from first step if not already set
                if not url and steps and len(steps) > 0:
                    first_step_url = steps[0].get('url', '')
                    if first_step_url:
                        url = first_step_url
                        session['url'] = url
                        logging.info(f"[GENERATE] Extracted URL from first step: {url}")
                
                for idx, step in enumerate(steps, 1):
                    if isinstance(step, dict):
                        prompt = step.get('prompt', '')
                        code = step.get('generated_code', step.get('code', ''))
                        value = step.get('value', '')  # Get actual value from step, not code
                        
                        logging.info(f"[GENERATE] Processing step {idx}/{len(steps)}: {prompt[:50]}")
                        logging.info(f"[GENERATE] Code length: {len(code)} chars")
                        
                        # Infer action_type from prompt text (BUILDER ONLY)
                        action_type = _infer_action_type_from_prompt(prompt, code)
                        
                        # Extract locator from generated code
                        suggested_locator, _ = _extract_locator_and_value_from_code(code, action_type)
                        
                        if not suggested_locator:
                            logging.error(f"[GENERATE] ❌ EMPTY locator for step {idx}: {prompt}")
                            logging.error(f"[GENERATE] Code sample (first 300 chars): {code[:300]}")
                            # Try to use a generic locator based on element type
                            prompt_lower = prompt.lower()
                            if 'email' in prompt_lower:
                                suggested_locator = 'By.CSS_SELECTOR("input[type=\'email\']")'
                                logging.warning(f"[GENERATE] Using fallback email locator")
                            elif 'password' in prompt_lower:
                                suggested_locator = 'By.CSS_SELECTOR("input[type=\'password\']")'
                                logging.warning(f"[GENERATE] Using fallback password locator")
                            elif 'button' in prompt_lower or 'sign in' in prompt_lower:
                                suggested_locator = 'By.CSS_SELECTOR("button")'
                                logging.warning(f"[GENERATE] Using fallback button locator")
                            else:
                                logging.error(f"[GENERATE] Cannot generate fallback locator")
                        else:
                            logging.info(f"[GENERATE] ✓ Extracted locator: {suggested_locator[:80]}")
                        
                        # Infer element type from prompt/code
                        element_type = ''
                        prompt_lower = prompt.lower()
                        if 'email' in prompt_lower:
                            element_type = 'email'
                        elif 'password' in prompt_lower:
                            element_type = 'password'
                        elif 'phone' in prompt_lower:
                            element_type = 'phone'
                        elif 'name' in prompt_lower:
                            element_type = 'name'
                        
                        # Build action with extracted/inferred data
                        action = {
                            'step': idx,
                            'action': prompt,
                            'code': code,
                            'action_type': action_type,  # Inferred for builder
                            'selector': suggested_locator,  # Extracted from code
                            'value': value or '',  # From step's value field
                            'suggested_locator': suggested_locator,  # Extracted from code
                            'element_type': element_type  # Inferred from prompt
                        }
                        session['actions'].append(action)
                        
                        logging.info(f"[GENERATE] Step {idx} summary: {action_type} | locator={suggested_locator[:70] if suggested_locator else 'EMPTY❌'} | value={value[:30] if value else 'EMPTY'}")
                
                logging.info(f"[GENERATE] ✓ Converted BUILDER test case: {identifier} with {len(session['actions'])} actions")
                logging.info(f"[GENERATE] Action types: {[a.get('action_type') for a in session['actions']]}")
                logging.info(f"[GENERATE] URL: {session.get('url', 'EMPTY')}")
        except Exception as e:
            logging.info(f"[GENERATE] Builder load failed (expected if recorder test): {e}")
        
        # If not found in builder, try recorder saved tests on disk
        if not session:
            from recorder.recorder_handler import load_saved_test_from_disk
            session = load_saved_test_from_disk(identifier)
            
            if session:
                session['source'] = 'recorder'  # Track that this is from Recorder
                logging.info(f"[GENERATE] ✓ Loaded RECORDER saved test from disk: {identifier}")
                logging.info(f"[GENERATE] Session has {len(session.get('actions', []))} actions from RECORDER")
        
        if not session:
            return jsonify({'success': False, 'error': 'Session or test case not found'}), 404
        
        if identifier not in recorded_sessions:
            logging.info(f"[GENERATE] Loaded saved test from disk: {identifier}")
    
    # Check if this is a semantic analysis request with description/suggestions
    description = request.json.get('description', '')
    suggestion_type = request.json.get('suggestion_type', '')
    suggestion_priority = request.json.get('suggestion_priority', '')
    
    # For semantic tests, ALWAYS generate fresh code (never use cache)
    # This ensures latest popup closing and modifications are applied
    is_semantic_test = bool(description and suggestion_type)
    
    if is_semantic_test:
        logging.info(f"[SEMANTIC] This is a semantic test - bypassing any cached code")
        # Clear any cached edited_code to force fresh generation
        if 'edited_code' in session:
            logging.info(f"[SEMANTIC] Clearing cached edited_code for fresh generation")
            del session['edited_code']
    
    # Check if there's edited code for this session (but NEVER use cache for semantic tests)
    if not is_semantic_test and 'edited_code' in session and session['edited_code']:
        logging.info(f"Returning cached edited code for {identifier}")
        return jsonify({
            'success': True,
            'code': session['edited_code'],
            'session_id': identifier,
            'is_edited': True
        }), 200
    
    logging.info(f"Generating fresh code for {identifier} (semantic={is_semantic_test})")
    test_name = request.json.get('test_name', session['name'].replace(' ', ''))
    language = request.json.get('language', 'python')  # Default to Python
    compact_mode = request.json.get('compact_mode', False)  # Enable compact code generation
    
    if compact_mode:
        logging.info(f"[COMPACT MODE] Enabled - generating 70% smaller code for DB/CI-CD")
    
    # If semantic analysis description provided, use AI to generate modified code
    if is_semantic_test:
        logging.info(f"[SEMANTIC] Generating {suggestion_type} test with AI for: {test_name}")
        logging.info(f"[SEMANTIC] Description: {description[:200]}...")
        try:
            # Use AI to generate semantic test code
            from core import inference_improved
            import os
            # Get the model path relative to the project root
            # From src/main/python/generators/code_generator.py, go up 5 levels to project root
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
            model_path = os.path.join(project_root, 'resources', 'ml_data', 'models', 'selenium_ngram_model.pkl')
            
            # Verify the model file exists before trying to load it
            if not os.path.exists(model_path):
                logging.warning(f"[SEMANTIC] Model file not found at {model_path}, falling back to standard generation")
                is_semantic_test = False
                code = _generate_python_code(session, test_name, compact_mode) if language == 'python' else _generate_java_code(session, test_name)
                return jsonify({
                    'success': True,
                    'code': code,
                    'session_id': identifier,
                    'is_semantic': False,
                    'fallback': 'model_not_found'
                }), 200
            
            logging.info(f"[SEMANTIC] Loading model from: {model_path}")
            generator = inference_improved.ImprovedSeleniumGenerator(
                model_path=model_path,
                silent=True
            )
            
            # Get original test code for reference
            original_code = _generate_python_code(session, test_name, compact_mode) if language == 'python' else _generate_java_code(session, test_name)
            
            logging.info(f"[SEMANTIC] Modifying original test for {suggestion_type} scenario...")
            logging.info(f"[SEMANTIC] Original code length: {len(original_code)} chars")
            
            # Modify the original test code based on suggestion type
            ai_code = _modify_test_for_semantic_type(
                original_code=original_code,
                suggestion_type=suggestion_type,
                description=description,
                test_name=test_name,
                language=language,
                session=session
            )
            
            if ai_code and len(ai_code.strip()) > 50:
                # Check if AI code is different from original
                if ai_code.strip() == original_code.strip():
                    logging.warning("[SEMANTIC] AI returned identical code, will use original with comment")
                    ai_code = f"# WARNING: AI did not modify test for {suggestion_type}\n# Using original test as fallback\n{original_code}"
                else:
                    logging.info(f"[SEMANTIC] AI generated DIFFERENT code ({len(ai_code)} chars vs {len(original_code)} chars)")
                
                # Post-process AI code to fix quote issues with find_element_safe
                logging.info(f"[SEMANTIC] Applying quote fix to AI code...")
                code_before = ai_code
                ai_code = fix_locator_quotes(ai_code)
                if code_before != ai_code:
                    logging.info(f"[SEMANTIC] Quote fix applied - code was modified")
                else:
                    logging.info(f"[SEMANTIC] Quote fix - no changes needed")
                
                # Log a sample of the code for debugging
                lines = ai_code.split('\n')
                logging.info(f"[SEMANTIC] Sample of generated code (lines 50-60):")
                for i, line in enumerate(lines[50:60], start=50):
                    logging.info(f"  Line {i}: {line}")
                
                logging.info(f"[SEMANTIC] Returning AI-generated code")
                return jsonify({
                    'success': True,
                    'code': ai_code,
                    'session_id': identifier,
                    'is_semantic': True,
                    'suggestion_type': suggestion_type
                }), 200
            else:
                logging.warning("[SEMANTIC] AI generation failed, falling back to standard generation")
        except Exception as e:
            logging.error(f"[SEMANTIC] Error in AI generation: {e}, falling back to standard")
            import traceback
            logging.error(traceback.format_exc())
    
    logging.info(f"[CODE GEN] Generating {language.upper()} code for test: {test_name}")
    
    if language == 'python':
        code = _generate_python_code(session, test_name, compact_mode)
        # Log setup_method to verify popup closing is there
        lines = code.split('\n')
        logging.info(f"[CODE GEN] Generated code - checking setup_method:")
        for i, line in enumerate(lines):
            if 'def setup_method' in line:
                for j in range(i, min(i+15, len(lines))):
                    logging.info(f"  Line {j}: {lines[j]}")
                break
        return jsonify({
            'success': True,
            'code': code,
            'session_id': identifier
        }), 200
    else:  # java
        code = _generate_java_code(session, test_name)
        return jsonify({
            'success': True,
            'code': code,
            'session_id': identifier
        }), 200

def _modify_test_for_semantic_type(original_code, suggestion_type, description, test_name, language, session):
    """Modify the original test code based on semantic suggestion type."""
    
    logging.info(f"[SEMANTIC] Modifying test for {suggestion_type} scenario")
    logging.info(f"[SEMANTIC] Original code length: {len(original_code)} chars")
    
    # Log a snippet of original code for debugging
    lines = original_code.split('\n')
    logging.info(f"[SEMANTIC] Original code sample (lines 70-80):")
    for i, line in enumerate(lines[70:80], start=70):
        logging.info(f"  Line {i}: {line}")
    
    # Create the modified test based on type
    modified_code = original_code
    
    # Determine source (Builder or Recorder)
    source = session.get('source', 'recorder')
    source_label = 'Builder test case' if source == 'builder' else 'Recorder test'
    
    # Modify test data based on suggestion type and get suggested values
    suggested_values = []
    if suggestion_type.lower() == 'negative':
        # Replace valid data with invalid data
        modified_code, suggested_values = _apply_negative_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'boundary':
        # Replace normal data with boundary values
        modified_code, suggested_values = _apply_boundary_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'edge_case':
        # Replace normal data with edge case values
        modified_code, suggested_values = _apply_edge_case_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'variation':
        # Use different valid data
        modified_code, suggested_values = _apply_variation_modifications(modified_code, session, language)
    
    # Build suggested test data comment
    suggested_values_comment = ""
    if suggested_values:
        suggested_values_comment = f"# Suggested test data for {suggestion_type} testing:\n"
        for step, value, reason in suggested_values:
            suggested_values_comment += f"#   Step {step}: '{value}' ({reason})\n"
        suggested_values_comment += "# \n"
    
    # Add header comment explaining the test modification
    header_comment = f"""# ============================================
# SEMANTIC TEST - {suggestion_type.upper()}
# ============================================
# {description.split(chr(10))[0] if description else 'Modified test case'}
# 
# This test was automatically generated from a {source_label}
# and modified to test {suggestion_type} scenarios.
# ============================================
# 
{suggested_values_comment}"""
    
    # Update test name in the code
    if language == 'python':
        modified_code = modified_code.replace(
            f'def test_{test_name.lower()}(',
            f'def test_{test_name.lower()}_{suggestion_type.lower()}('
        )
        modified_code = modified_code.replace(
            f'class Test{test_name}',
            f'class Test{test_name}_{suggestion_type.title()}'
        )
    else:  # Java
        modified_code = modified_code.replace(
            f'public void test_{test_name}(',
            f'public void test_{test_name}_{suggestion_type.lower()}('
        )
    
    # Add header comment
    modified_code = header_comment + modified_code
    
    # NOTE: No quote fixes needed - smart quote selection already handles this correctly
    # in the action generation loop (lines 522-530)
    
    # Log modified code sample for debugging
    lines = modified_code.split('\n')
    logging.info(f"[SEMANTIC] Modified code sample (lines 80-90):")
    for i, line in enumerate(lines[80:90], start=80):
        logging.info(f"  Line {i}: {line}")
    
    logging.info(f"[SEMANTIC] Modified test code generated ({len(modified_code)} chars)")
    return modified_code

def _apply_negative_modifications(code, session, language):
    """Apply negative test modifications - use invalid data with AI-based context awareness.
    
    Delegates to SemanticModifier module.
    Returns: (modified_code, suggested_values_list)
    """
    return SemanticModifier.apply_negative_modifications(code, session, language)


def _analyze_test_context(test_name: str, test_url: str, actions: List[Dict]) -> Dict[str, Any]:
    """Analyze test to understand context for intelligent data generation using AI.
    
    Delegates to ContextAnalyzer module.
    """
    return ContextAnalyzer.analyze_test_context(test_name, test_url, actions)


def _extract_workflow_from_test(test_name: str, test_url: str, actions: List[Dict]) -> Dict[str, str]:
    """Dynamically extract workflow information from test characteristics.
    
    Delegates to ContextAnalyzer module.
    """
    return ContextAnalyzer.extract_workflow_from_test(test_name, test_url, actions)


def _extract_field_info_from_action(action: Dict) -> Optional[Dict[str, Any]]:
    """Extract field information from action without hardcoding field types.
    
    Delegates to FieldAnalyzer module.
    """
    return FieldAnalyzer.extract_field_info_from_action(action)


def _infer_field_type_from_text(text: str, value: str) -> str:
    """Infer field type by analyzing text and value patterns (Universal AI approach).
    
    Delegates to FieldAnalyzer module.
    """
    return FieldAnalyzer.infer_field_type_from_text(text, value)


def _infer_validation_rules(text: str, value: str) -> List[str]:
    """Infer validation rules from field characteristics.
    
    Delegates to FieldAnalyzer module.
    """
    return FieldAnalyzer.infer_validation_rules(text, value)


def _infer_if_required(text: str, locator: str) -> bool:
    """Check if field is required based on text analysis.
    
    Delegates to FieldAnalyzer module.
    """
    return FieldAnalyzer.infer_if_required(text, locator)


def _infer_max_length(text: str, value: str) -> Optional[int]:
    """Infer maximum length from value or text hints."""
    import re
    
    # Look for max length hints in text
    max_match = re.search(r'max(?:imum)?[:\s]*(\d+)', text)
    if max_match:
        return int(max_match.group(1))
    
    # For email, standard max is 254
    if '@' in value:
        return 254
    
    # For password, common max is 128
    if 'password' in text:
        return 128
    
    # Default: infer from value length (assume 2-3x current)
    if value:
        return len(value) * 3
    
    return None


def _generate_contextual_invalid_data(field_value: str, locator: str, action_text: str, 
                                      test_context: Dict, step: int) -> Tuple[str, str]:
    """Generate context-aware invalid test data for ANY test case type.
    
    Delegates to TestDataGenerator module.
    """
    return TestDataGenerator.generate_invalid_data(field_value, locator, action_text, test_context, step)


def _generate_contextual_boundary_data(field_value: str, locator: str, action_text: str, 
                                       test_context: Dict, step: int) -> Tuple[str, str]:
    """Generate boundary test data for ANY test case type (Universal).
    
    Delegates to TestDataGenerator module.
    """
    return TestDataGenerator.generate_boundary_data(field_value, locator, action_text, test_context, step)


def _generate_contextual_variation_data(field_value: str, locator: str, action_text: str, 
                                        test_context: Dict, step: int) -> Tuple[str, str]:
    """Generate variation test data for ANY test case type (Universal).
    
    Delegates to TestDataGenerator module.
    """
    return TestDataGenerator.generate_variation_data(field_value, locator, action_text, test_context, step)


def _apply_boundary_modifications(code, session, language):
    """Apply boundary test modifications - use min/max values with context awareness.
    
    Delegates to SemanticModifier module.
    Returns: (modified_code, suggested_values_list)
    """
    return SemanticModifier.apply_boundary_modifications(code, session, language)


def _apply_edge_case_modifications(code, session, language):
    """Apply edge case test modifications - special characters, security.
    
    Delegates to SemanticModifier module.
    Returns: (modified_code, suggested_values_list)
    """
    return SemanticModifier.apply_edge_case_modifications(code, session, language)


def _apply_variation_modifications(code, session, language):
    """Apply variation test modifications - different valid data with context awareness.
    
    Delegates to SemanticModifier module.
    Returns: (modified_code, suggested_values_list)
    """
    return SemanticModifier.apply_variation_modifications(code, session, language)


def _generate_python_code(session, test_name, compact_mode=False):
    """Generate Python test code with self-healing capabilities.
    
    Args:
        session: Test session with recorded actions
        test_name: Name for the test
        compact_mode: If True, generates compact code (not currently used in recorder path)
    """
    if compact_mode:
        logging.info(f"[COMPACT MODE] Generating compact Python code for {test_name}")
    
    code = f"""import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import sys
import os

# Add self-healing locator support
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
try:
    from self_healing_locator import SelfHealingLocator
except ImportError:
    # Fallback if self-healing not available
    SelfHealingLocator = None

class Test{test_name}:
    def setup_method(self, browser='chrome'):
        # Browser-agnostic setup - supports chrome, firefox, edge
        if browser.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        elif browser.lower() == 'edge':
            self.driver = webdriver.Edge()
        else:
            self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)  # Increased wait for elements
        self.driver.get("{session['url']}")
        time.sleep(3)  # Increased wait for page load
        
        # Initialize self-healing locator if available
        self.healer = SelfHealingLocator() if SelfHealingLocator else None
        
        # Close sticky popup - simple direct approach
        try:
            close_btn = self.driver.find_element(By.ID, "sticky-close")
            self.driver.execute_script("arguments[0].click();", close_btn)
            time.sleep(1)
        except:
            pass
    
    def test_{test_name.lower()}(self):
        wait = WebDriverWait(self.driver, 20)
        
        # Helper method to find elements with self-healing and better waits
        def find_element_safe(locator_str):
            if self.healer:
                element = self.healer.find_element(self.driver, locator_str)
                if element:
                    return element
            # Fallback to traditional method if healer fails or not available
            by_parts = locator_str.replace('By.', '').split('(')
            if len(by_parts) == 2:
                by_type = by_parts[0].strip()
                value = by_parts[1].strip(')"\\'')
                by_map = {{'ID': By.ID, 'NAME': By.NAME, 'XPATH': By.XPATH, 'CSS_SELECTOR': By.CSS_SELECTOR,
                          'CLASS_NAME': By.CLASS_NAME, 'TAG_NAME': By.TAG_NAME, 'LINK_TEXT': By.LINK_TEXT}}
                locator = (by_map.get(by_type, By.XPATH), value)
                # First wait for presence, then wait for visibility
                element = wait.until(EC.presence_of_element_located(locator))
                wait.until(EC.visibility_of(element))
                return element
            raise Exception(f"Could not find element: {{locator_str}}")
"""
    
    # Add actions
    actions = session.get('actions', [])
    if not actions:
        logging.warning(f"[CODE GEN] No actions found in session {session.get('name', 'unknown')}")
        code += "        # No actions recorded yet\n"
        code += "        pass\n"
    
    first_action = True
    for action in actions:
        action_type = action.get('action_type')
        
        # Skip actions without proper action_type
        if not action_type or action_type == 'undefined':
            logging.warning(f"[CODE GEN] Skipping action with undefined type: {action}")
            continue
        
        # Skip verify_message steps that have no value
        if action_type == 'verify_message' and not action.get('value'):
            continue
        
        # Close popup before first input/click action to avoid interference
        if first_action and action_type in ['input', 'click', 'click_and_input']:
            code += "        # Close any sticky popups that might interfere with actions\n"
            code += "        try:\n"
            code += "            close_btn = self.driver.find_element(By.ID, 'sticky-close')\n"
            code += "            self.driver.execute_script('arguments[0].click();', close_btn)\n"
            code += "            time.sleep(0.5)\n"
            code += "        except:\n"
            code += "            pass  # Popup might not exist\n"
            code += "        \n"
            first_action = False
        
        code += f"        # Step {action['step']}: {action_type}\n"
        
        # Only build locator for actions that need it (not scroll or verify_message)
        locator_str = None
        if action_type not in ['scroll', 'verify_message']:
            locator = action.get('suggested_locator', 'By.ID, "unknown"')
            
            # Build locator string with proper quoting
            # Always use single quotes on the outside, escape single quotes inside
            if "'" in locator:
                # Has single quotes - escape them
                locator_escaped = locator.replace("'", "\\'")
                locator_str = f"'{locator_escaped}'"
                logging.info(f"[LOCATOR] Escaped single quotes: {locator_str}")
            else:
                # No single quotes - simple wrap
                locator_str = f"'{locator}'"
                logging.info(f"[LOCATOR] Simple quotes: {locator_str}")
        
        if action_type == 'click':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        # Scroll to element (exactly like Java scrollToView)\n"
            code += f"        try:\n"
            code += f"            self.driver.execute_script(\"arguments[0].scrollIntoView(false);\", elem)\n"
            code += f"            time.sleep(0.5)\n"
            code += f"        except Exception as scroll_err:\n"
            code += f"            print(f'Scroll warning: {{scroll_err}}')\n"
            code += f"        # Try regular click, fallback to JavaScript click if intercepted\n"
            code += f"        try:\n"
            code += f"            elem.click()\n"
            code += f"        except Exception as e:\n"
            code += f"            if 'intercepted' in str(e).lower() or 'not clickable' in str(e).lower():\n"
            code += f"                print('Element click intercepted, using JavaScript click')\n"
            code += f"                self.driver.execute_script('arguments[0].click();', elem)\n"
            code += f"            else:\n"
            code += f"                raise\n"
            code += f"        time.sleep(0.5)  # Brief pause after click\n"
            logging.info(f"[GENERATED] Click with improved scrollIntoView and JS fallback: {locator_str}")
        
        elif action_type == 'input':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        # Scroll to element (exactly like Java scrollToView)\n"
            code += f"        try:\n"
            code += f"            self.driver.execute_script(\"arguments[0].scrollIntoView(false);\", elem)\n"
            code += f"            time.sleep(0.5)\n"
            code += f"        except Exception as scroll_err:\n"
            code += f"            print(f'Scroll warning: {{scroll_err}}')\n"
            code += f"        elem.clear()\n"
            code += f"        time.sleep(0.2)\n"
            code += f"        elem.send_keys(\"{action['value']}\")\n"
        
        elif action_type == 'click_and_input':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        # Scroll to element (exactly like Java scrollToView)\n"
            code += f"        try:\n"
            code += f"            self.driver.execute_script(\"arguments[0].scrollIntoView(false);\", elem)\n"
            code += f"            time.sleep(0.5)\n"
            code += f"        except Exception as scroll_err:\n"
            code += f"            print(f'Scroll warning: {{scroll_err}}')\n"
            code += f"        elem.click()\n"
            code += f"        time.sleep(0.3)\n"
            code += f"        elem.clear()\n"
            code += f"        time.sleep(0.2)\n"
            code += f"        elem.send_keys(\"{action['value']}\")\n"
        
        elif action_type == 'select':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        # Scroll to element (exactly like Java scrollToView)\n"
            code += f"        try:\n"
            code += f"            self.driver.execute_script(\"arguments[0].scrollIntoView(false);\", elem)\n"
            code += f"            time.sleep(0.5)\n"
            code += f"        except Exception as scroll_err:\n"
            code += f"            print(f'Scroll warning: {{scroll_err}}')\n"
            code += f"        Select(elem).select_by_visible_text(\"{action['value']}\")\n"
            code += f"        time.sleep(0.3)  # Wait for selection to register\n"
        
        elif action_type == 'scroll':
            # Handle explicit scroll actions recorded by user
            import json
            try:
                scroll_data = json.loads(action.get('value', '{}'))
                scroll_x = scroll_data.get('x', 0)
                scroll_y = scroll_data.get('y', 0)
                code += f"        # Explicit scroll recorded by user\n"
                code += f"        self.driver.execute_script('window.scrollTo({scroll_x}, {scroll_y});')\n"
                code += f"        time.sleep(0.5)  # Wait for scroll to complete\n"
                logging.info(f"[GENERATED] Scroll to position: x={scroll_x}, y={scroll_y}")
            except:
                logging.warning(f"[GENERATED] Could not parse scroll data: {action.get('value')}")
                pass
        
        elif action_type == 'upload_file':
            file_path = action.get('value', '')
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        # Scroll to element (exactly like Java scrollToView)\n"
            code += f"        self.driver.execute_script(\"arguments[0].scrollIntoView(false);\", elem)\n"
            code += f"        time.sleep(0.5)\n"
            if '|' in file_path:
                paths_str = '\\n'.join(file_path.split('|'))
                code += f"        elem.send_keys(\"{paths_str}\")\n"
            else:
                code += f"        elem.send_keys(\"{file_path}\")\n"
        
        elif action_type == 'drag_and_drop':
            target_locator = action.get('target_locator', 'By.ID, "drop-target"')
            # Build target locator string with proper quoting
            if '"' in target_locator and "'" in target_locator:
                target_str = f'"""{target_locator}"""'
            elif '"' in target_locator:
                target_str = f"'{target_locator}'"
            else:
                target_str = f'"{target_locator}"'
            code += f"        from selenium.webdriver.common.action_chains import ActionChains\n"
            code += f"        source_elem = find_element_safe({locator_str})\n"
            code += f"        target_elem = find_element_safe({target_str})\n"
            code += f"        # Scroll source element into view\n"
            code += f"        self.driver.execute_script(\"arguments[0].scrollIntoView({{behavior: 'auto', block: 'center'}});\", source_elem)\n"
            code += f"        time.sleep(0.5)\n"
            code += f"        ActionChains(self.driver).drag_and_drop(source_elem, target_elem).perform()\n"
        
        elif action_type == 'verify_message':
            message = action.get('value', '')
            if message:
                normalized_message = ' '.join(message.split())
                code += f"        elem = find_element_safe({locator_str})\n"
                code += f"        # Scroll element into view\n"
                code += f"        self.driver.execute_script(\"arguments[0].scrollIntoView({{behavior: 'auto', block: 'center'}});\", elem)\n"
                code += f"        time.sleep(0.5)\n"
                code += f"        actual_msg = ' '.join(elem.text.split())\n"
                code += f"        assert '{normalized_message}' in actual_msg, f'Expected: {normalized_message}, Got: {{actual_msg}}'\n"
        
        code += f"\n"
    
    code += f"""    
    def teardown_method(self):
        if self.driver:
            self.driver.quit()
"""
    
    # Log a sample of the generated code for debugging
    lines = code.split('\n')
    logging.info(f"[GENERATED CODE] Total lines: {len(lines)}")
    logging.info(f"[GENERATED CODE] Sample (lines 70-80):")
    for i in range(70, min(80, len(lines))):
        if i < len(lines):
            logging.info(f"  Line {i}: {lines[i]}")
    
    return code

def _generate_java_code(session, test_name):
    """Generate Java test code."""
    code = f"""package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.testng.annotations.*;

public class {test_name} {{
    private WebDriver driver;
    
    @BeforeMethod
    public void setUp() {{
        // Browser-agnostic setup - supports chrome, firefox, edge
        String browser = System.getProperty("browser", "chrome");
        if (browser.equalsIgnoreCase("firefox")) {{
            driver = new FirefoxDriver();
        }} else if (browser.equalsIgnoreCase("edge")) {{
            driver = new EdgeDriver();
        }} else {{
            driver = new ChromeDriver();
        }}
        driver.get("{session['url']}");
        
        // Close sticky popup
        try {{
            Thread.sleep(2000);
            ((JavascriptExecutor) driver).executeScript(
                "var s = document.getElementById('sticky-close'); if (s) s.click();"
            );
        }} catch (Exception e) {{ }}
    }}
    
    @Test
    public void recordedTest() {{
"""
    
    for action in session['actions']:
        action_type = action['action_type']
        
        if action_type == 'verify_message' and not action.get('value'):
            continue
            
        code += f"        // Step {action['step']}: {action_type}\n"
        
        locator = action.get('suggested_locator', 'By.id("unknown")')
        
        if locator.startswith('driver.findElement('):
            locator = locator.replace('driver.findElement(', '').replace(')', '')
        
        if action_type == 'click':
            code += f"        driver.findElement({locator}).click();\n"
        elif action_type == 'input':
            code += f"        driver.findElement({locator}).sendKeys(\"{action['value']}\");\n"
        elif action_type == 'click_and_input':
            code += f"        WebElement element = driver.findElement({locator});\n"
            code += f"        element.click();\n"
            code += f"        element.sendKeys(\"{action['value']}\");\n"
        elif action_type == 'select':
            code += f"        Select select = new Select(driver.findElement({locator}));\n"
            code += f"        select.selectByVisibleText(\"{action['value']}\");\n"
        elif action_type == 'verify_message':
            message = action.get('value', '')
            if message:
                normalized_message = ' '.join(message.split())
                code += f"        // Verify message appears\n"
                code += f"        String actualMessage = driver.findElement({locator}).getText().trim();\n"
                code += f"        assert actualMessage.contains(\"{normalized_message}\");\n"
        
        code += f"\n"
    
    code += """    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
"""
    return code

def update_test_code(recorded_sessions):
    """Update the generated test code for a session."""
    session_id = request.json.get('session_id')
    edited_code = request.json.get('code')
    
    if not session_id or session_id not in recorded_sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    if not edited_code:
        return jsonify({'success': False, 'error': 'Code is required'}), 400
    
    # Store the edited code in the session
    recorded_sessions[session_id]['edited_code'] = edited_code
    
    logging.info(f"Updated test code for session: {session_id}")
    
    return jsonify({
        'success': True,
        'message': 'Test code updated successfully',
        'session_id': session_id
    }), 200
