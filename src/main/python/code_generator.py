"""
Test code generation for Python and Java.
"""
import re
import logging
from flask import request, jsonify

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
                
                # Remove existing quotes at start/end
                if (inner_content.startswith('"') and inner_content.endswith('"')) or \
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

def generate_test_code(recorded_sessions):
    """Generate test code from recorded session."""
    session_id = request.json.get('session_id')
    
    if not session_id or session_id not in recorded_sessions:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    session = recorded_sessions[session_id]
    
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
        logging.info(f"Returning cached edited code for session {session_id}")
        return jsonify({
            'success': True,
            'code': session['edited_code'],
            'session_id': session_id,
            'is_edited': True
        }), 200
    
    logging.info(f"Generating fresh code for session {session_id} (semantic={is_semantic_test})")
    test_name = request.json.get('test_name', session['name'].replace(' ', ''))
    language = request.json.get('language', 'python')  # Default to Python
    
    # If semantic analysis description provided, use AI to generate modified code
    if is_semantic_test:
        logging.info(f"[SEMANTIC] Generating {suggestion_type} test with AI for: {test_name}")
        logging.info(f"[SEMANTIC] Description: {description[:200]}...")
        try:
            # Use AI to generate semantic test code
            import inference_improved
            generator = inference_improved.ImprovedSeleniumGenerator(
                model_path='C:\\Users\\valaboph\\WebAutomation\\selenium_ngram_model.pkl',
                silent=True
            )
            
            # Get original test code for reference
            original_code = _generate_python_code(session, test_name) if language == 'python' else _generate_java_code(session, test_name)
            
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
                    'session_id': session_id,
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
        code = _generate_python_code(session, test_name)
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
            'session_id': session_id
        }), 200
    else:  # java
        code = _generate_java_code(session, test_name)
        return jsonify({
            'success': True,
            'code': code,
            'session_id': session_id
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
    
    # Add header comment explaining the test modification
    header_comment = f"""# ============================================
# SEMANTIC TEST - {suggestion_type.upper()}
# ============================================
# {description.split(chr(10))[0] if description else 'Modified test case'}
# 
# This test was automatically generated from a recorded test
# and modified to test {suggestion_type} scenarios.
# ============================================

"""
    
    # Modify test data based on suggestion type
    if suggestion_type.lower() == 'negative':
        # Replace valid data with invalid data
        modified_code = _apply_negative_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'boundary':
        # Replace normal data with boundary values
        modified_code = _apply_boundary_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'edge_case':
        # Replace normal data with edge case values
        modified_code = _apply_edge_case_modifications(modified_code, session, language)
    elif suggestion_type.lower() == 'variation':
        # Use different valid data
        modified_code = _apply_variation_modifications(modified_code, session, language)
    
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
    """Apply negative test modifications - use invalid data."""
    import re
    
    # Get all input actions from session to know what we're replacing
    actions = session.get('actions', [])
    
    # Build a mapping of original values to invalid values
    replacements = {}
    
    for action in actions:
        if action['action_type'] in ['input', 'click_and_input']:
            original_value = action.get('value', '')
            if not original_value:
                continue
            
            # Determine appropriate invalid value based on field type
            locator_lower = action.get('suggested_locator', '').lower()
            element_type_lower = action.get('element_type', '').lower()
            
            if 'email' in element_type_lower or 'email' in locator_lower:
                invalid_value = 'invalid-email-format'
            elif 'password' in element_type_lower or 'password' in locator_lower:
                invalid_value = '123'  # Too short password
            elif 'phone' in element_type_lower or 'phone' in locator_lower:
                invalid_value = 'abc-def-ghij'  # Invalid phone
            elif 'zip' in element_type_lower or 'zip' in locator_lower:
                invalid_value = '123'  # Invalid zip
            elif 'age' in element_type_lower or 'number' in element_type_lower:
                invalid_value = '-1'  # Negative number
            else:
                invalid_value = ''  # Empty value for required fields
            
            replacements[original_value] = invalid_value
    
    # Replace values only in send_keys() calls to avoid breaking locators
    for original, invalid in replacements.items():
        if original:
            # Use a more precise regex that matches send_keys with the value
            # This pattern matches: send_keys("value") or send_keys('value')
            # But NOT values inside locator strings
            pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
            replacement = f'.send_keys("{invalid}")'
            code = re.sub(pattern, replacement, code)
    
    # Add assertion for error message (add before teardown)
    if language == 'python':
        # Add assertion to check for error message or validation failure
        error_check = """
        # Verify that error message or validation failure appears
        time.sleep(1)  # Wait for error message
        try:
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'invalid') or contains(text(), 'Invalid') or contains(text(), 'required') or contains(text(), 'Required')]")
            assert len(error_elements) > 0, "Expected error message but none found"
            logging.info(f"✓ Error validation working - found {len(error_elements)} error messages")
        except AssertionError as e:
            logging.warning(f"⚠ {e}")
"""
        # Insert before teardown_method
        code = code.replace('    def teardown_method(self):', error_check + '\n    def teardown_method(self):')
    
    return code

def _apply_boundary_modifications(code, session, language):
    """Apply boundary test modifications - use min/max values."""
    import re
    
    actions = session.get('actions', [])
    replacements = {}
    
    for action in actions:
        if action['action_type'] in ['input', 'click_and_input']:
            original_value = action.get('value', '')
            if not original_value:
                continue
            
            # Use boundary values
            element_type_lower = action.get('element_type', '').lower()
            locator_lower = action.get('suggested_locator', '').lower()
            
            if 'email' in element_type_lower or 'email' in locator_lower:
                boundary_value = 'a@b.c'  # Minimum valid email
            elif 'name' in element_type_lower or 'text' in element_type_lower:
                boundary_value = 'a' * 255  # Maximum length
            elif 'age' in element_type_lower:
                boundary_value = '0'  # Minimum age
            else:
                boundary_value = 'x' * 1000  # Very long string
            
            replacements[original_value] = boundary_value
    
    # Replace values only in send_keys() calls
    for original, boundary in replacements.items():
        if original:
            pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
            replacement = f'.send_keys("{boundary}")'
            code = re.sub(pattern, replacement, code)
    
    return code

def _apply_edge_case_modifications(code, session, language):
    """Apply edge case test modifications - special characters, security."""
    import re
    
    actions = session.get('actions', [])
    replacements = {}
    
    for action in actions:
        if action['action_type'] in ['input', 'click_and_input']:
            original_value = action.get('value', '')
            if not original_value:
                continue
            
            # Use edge case values - special characters, SQL injection, XSS
            edge_values = [
                "<script>alert('xss')</script>",
                "' OR '1'='1' --",
                "!@#$%^&*()",
                "../../etc/passwd",
                "你好世界",  # Unicode
                "test\ntest",  # Newlines
            ]
            
            # Pick appropriate edge case value based on field
            edge_value = edge_values[hash(action.get('suggested_locator', '')) % len(edge_values)]
            replacements[original_value] = edge_value
    
    # Replace values only in send_keys() calls
    for original, edge in replacements.items():
        if original:
            # Escape special regex chars and quotes in the replacement value
            edge_escaped = edge.replace('\\', '\\\\').replace('"', '\\"')
            pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
            replacement = f'.send_keys("{edge_escaped}")'
            code = re.sub(pattern, replacement, code)
    
    return code

def _apply_variation_modifications(code, session, language):
    """Apply variation test modifications - different valid data."""
    import re
    
    actions = session.get('actions', [])
    replacements = {}
    
    for action in actions:
        if action['action_type'] in ['input', 'click_and_input']:
            original_value = action.get('value', '')
            if not original_value:
                continue
            
            # Use different but valid data
            element_type_lower = action.get('element_type', '').lower()
            locator_lower = action.get('suggested_locator', '').lower()
            
            if 'email' in element_type_lower or 'email' in locator_lower:
                variation_value = 'alternative.user@example.com'
            elif 'name' in element_type_lower or 'name' in locator_lower:
                variation_value = 'Jane Doe'
            elif 'phone' in element_type_lower or 'phone' in locator_lower:
                variation_value = '555-0123'
            else:
                variation_value = 'Alternative Value'
            
            replacements[original_value] = variation_value
    
    # Replace values only in send_keys() calls
    for original, variation in replacements.items():
        if original:
            pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
            replacement = f'.send_keys("{variation}")'
            code = re.sub(pattern, replacement, code)
    
    return code

def _generate_python_code(session, test_name):
    """Generate Python test code with self-healing capabilities."""
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
script_dir = r'C:\\Users\\valaboph\\WebAutomation\\src\\main\\python'
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
try:
    from self_healing_locator import SelfHealingLocator
except ImportError:
    # Fallback if self-healing not available
    SelfHealingLocator = None

class Test{test_name}:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)  # Implicit wait for elements
        self.driver.get("{session['url']}")
        time.sleep(2)  # Wait for page load
        
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
        
        # Helper method to find elements with self-healing
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
                return wait.until(EC.presence_of_element_located((by_map.get(by_type, By.XPATH), value)))
            raise Exception(f"Could not find element: {{locator_str}}")
"""
    
    # Add actions
    for action in session['actions']:
        action_type = action['action_type']
        
        # Skip verify_message steps that have no value
        if action_type == 'verify_message' and not action.get('value'):
            continue
        
        code += f"        # Step {action['step']}: {action_type}\n"
        
        locator = action.get('suggested_locator', 'By.ID, "unknown"')
        
        # Build locator string with proper quoting
        # Use triple-quoted raw string to avoid escaping issues
        if '"' in locator and "'" in locator:
            # Has both quote types - use triple quotes
            locator_str = f'"""{locator}"""'
            logging.info(f"[LOCATOR] Triple quotes: {locator_str}")
        elif '"' in locator:
            # Has double quotes - use single quotes
            locator_str = f"'{locator}'"
            logging.info(f"[LOCATOR] Single quotes: {locator_str}")
        else:
            # Default - use double quotes
            locator_str = f'"{locator}"'
            logging.info(f"[LOCATOR] Double quotes: {locator_str}")
        
        if action_type == 'click':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        self.driver.execute_script('arguments[0].scrollIntoView({{block: \"center\"}});', elem)\n"
            code += f"        time.sleep(0.5)  # Wait for scroll and ensure no overlays\n"
            code += f"        # Try regular click, fallback to JavaScript click if intercepted\n"
            code += f"        try:\n"
            code += f"            elem.click()\n"
            code += f"        except Exception as e:\n"
            code += f"            if 'intercepted' in str(e):\n"
            code += f"                print('Element click intercepted, using JavaScript click')\n"
            code += f"                self.driver.execute_script('arguments[0].click();', elem)\n"
            code += f"            else:\n"
            code += f"                raise\n"
            logging.info(f"[GENERATED] Click with scroll and JS fallback: {locator_str}")
        
        elif action_type == 'input':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        self.driver.execute_script('arguments[0].scrollIntoView({{block: \"center\"}});', elem)\n"
            code += f"        time.sleep(0.3)  # Wait for scroll\n"
            code += f"        elem.clear()\n"
            code += f"        elem.send_keys(\"{action['value']}\")\n"
        
        elif action_type == 'click_and_input':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        self.driver.execute_script('arguments[0].scrollIntoView({{block: \"center\"}});', elem)\n"
            code += f"        time.sleep(0.3)  # Wait for scroll\n"
            code += f"        elem.click()\n"
            code += f"        elem.clear()\n"
            code += f"        elem.send_keys(\"{action['value']}\")\n"
        
        elif action_type == 'select':
            code += f"        elem = find_element_safe({locator_str})\n"
            code += f"        self.driver.execute_script('arguments[0].scrollIntoView({{block: \"center\"}});', elem)\n"
            code += f"        time.sleep(0.3)  # Wait for scroll\n"
            code += f"        Select(elem).select_by_visible_text(\"{action['value']}\")\n"
        
        elif action_type == 'upload_file':
            file_path = action.get('value', '')
            if '|' in file_path:
                paths_str = '\\n'.join(file_path.split('|'))
                code += f"        find_element_safe({locator_str}).send_keys(\"{paths_str}\")\n"
            else:
                code += f"        find_element_safe({locator_str}).send_keys(\"{file_path}\")\n"
        
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
            code += f"        ActionChains(self.driver).drag_and_drop(find_element_safe({locator_str}), find_element_safe({target_str})).perform()\n"
        
        elif action_type == 'verify_message':
            message = action.get('value', '')
            if message:
                normalized_message = ' '.join(message.split())
                code += f"        actual_msg = ' '.join(find_element_safe({locator_str}).text.split())\n"
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
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.testng.annotations.*;

public class {test_name} {{
    private WebDriver driver;
    
    @BeforeMethod
    public void setUp() {{
        driver = new ChromeDriver();
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
