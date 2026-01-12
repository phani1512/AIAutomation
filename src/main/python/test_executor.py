"""
Test execution handlers for single tests and test suites.
"""
import time
import logging
import tempfile
import subprocess
import os
import re
from flask import request, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def execute_edited_code(session, data_overrides=None):
    """Execute edited test code (Java or Python)."""
    edited_code = session['edited_code']
    test_name = session.get('name', 'Test').replace(' ', '_')
    
    # Apply data overrides to replace placeholders in the code
    if data_overrides:
        logging.info(f"[FILE UPLOAD] Applying data_overrides: {data_overrides}")
        for step_num, file_path in data_overrides.items():
            # Replace placeholders like {{FILE_UPLOAD_7_1}} or {{FILE_UPLOAD_7_1}}|{{FILE_UPLOAD_7_2}}
            # For single file: replace {{FILE_UPLOAD_<step>_1}} with the actual path
            # For multiple files: file_path will contain pipe-separated paths
            if '|' in str(file_path):
                # Multiple files - replace each placeholder
                file_paths = str(file_path).split('|')
                for i, path in enumerate(file_paths, 1):
                    placeholder = f'{{{{FILE_UPLOAD_{step_num}_{i}}}}}'
                    logging.info(f"[FILE UPLOAD] Replacing '{placeholder}' with '{path}'")
                    edited_code = edited_code.replace(placeholder, path)
            else:
                # Single file - replace the placeholder
                placeholder = f'{{{{FILE_UPLOAD_{step_num}_1}}}}'
                logging.info(f"[FILE UPLOAD] Replacing '{placeholder}' with '{file_path}'")
                edited_code = edited_code.replace(placeholder, str(file_path))
    else:
        logging.info("[FILE UPLOAD] No data_overrides provided")
    
    # Detect language
    is_python = 'from selenium' in edited_code or 'import pytest' in edited_code or 'def ' in edited_code
    is_java = 'public class' in edited_code or 'import org.openqa.selenium' in edited_code
    
    try:
        if is_python:
            # Execute Python code
            logging.info(f"[EDITED CODE] Executing Python test: {test_name}")
            
            # Add a runner script to execute the test class
            runner_code = f"""
import sys
import traceback

# Import the test code
{edited_code}

# Run the test
if __name__ == '__main__':
    try:
        # Find the test class
        test_classes = [obj for name, obj in locals().items() 
                       if isinstance(obj, type) and name.startswith('Test')]
        
        if not test_classes:
            print("ERROR: No test class found")
            sys.exit(1)
        
        test_class = test_classes[0]
        test_instance = test_class()
        
        # Run setup if it exists
        if hasattr(test_instance, 'setup_method'):
            test_instance.setup_method()
        
        # Find and run test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_') and callable(getattr(test_instance, method))]
        
        if not test_methods:
            print("ERROR: No test methods found")
            sys.exit(1)
        
        print(f"Running {{len(test_methods)}} test(s)...")
        
        for method_name in test_methods:
            print(f"\\n▶ Running: {{method_name}}")
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"✓ {{method_name}} PASSED")
            except Exception as e:
                print(f"✗ {{method_name}} FAILED")
                traceback.print_exc()
                raise
        
        # Run teardown if it exists
        if hasattr(test_instance, 'teardown_method'):
            test_instance.teardown_method()
        
        print("\\n✓ All tests PASSED")
        sys.exit(0)
        
    except Exception as e:
        print(f"\\n✗ Test execution FAILED: {{e}}")
        traceback.print_exc()
        sys.exit(1)
"""
            
            # Create temporary Python file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                temp_file = f.name
                f.write(runner_code)
            
            # Execute Python script directly
            try:
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                # Clean up
                os.unlink(temp_file)
                
                # Check result
                success = result.returncode == 0
                output = result.stdout + result.stderr
                
                # Try to count steps from the test code (count actions/waits)
                steps_executed = 0
                total_steps = 0
                if success:
                    # Count steps by looking for Step comments in the code
                    step_matches = re.findall(r'# Step \d+:', edited_code)
                    total_steps = len(step_matches)
                    steps_executed = total_steps
                
                logging.info(f"[EDITED CODE] Python test execution {'PASSED' if success else 'FAILED'}")
                
                return jsonify({
                    'success': True,
                    'passed': success,
                    'is_edited_code': True,
                    'test_name': test_name,
                    'steps_executed': steps_executed,
                    'total_steps': total_steps,
                    'output': output,
                    'error': result.stderr if not success else None
                }), 200
                
            except subprocess.TimeoutExpired:
                os.unlink(temp_file)
                return jsonify({
                    'success': False,
                    'error': 'Test execution timeout (exceeded 120 seconds)'
                }), 400
            except Exception as e:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                raise
        
        elif is_java:
            # Execute Java code (implementation omitted for brevity)
            return jsonify({
                'success': False,
                'error': 'Java execution not implemented in this module'
            }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to detect code language (expected Python)'
            }), 400
            
    except subprocess.TimeoutExpired:
        logging.error(f"[EDITED CODE] Execution timeout")
        return jsonify({
            'success': False,
            'error': 'Test execution timeout (exceeded 120 seconds)'
        }), 400
    except Exception as e:
        logging.error(f"[EDITED CODE] Execution error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Execution error: {str(e)}'
        }), 500

def _resolve_file_path(file_path):
    """
    Smart file path resolution with support for:
    1. Files in src/resources/uploads/ directory (default for CI/CD)
    2. Relative paths from project root
    3. Absolute paths
    
    Returns normalized absolute path with forward slashes, or None if not found.
    """
    # Get project root (3 levels up from this file: python -> main -> src -> project)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    # Strategy 1: Check if file exists in src/resources/uploads/ (default location)
    # This allows users to just specify filename like "file.pdf" or "module/file.pdf"
    uploads_dir = os.path.join(project_root, 'src', 'resources', 'uploads')
    uploads_path = os.path.join(uploads_dir, file_path)
    if os.path.exists(uploads_path):
        logging.info(f"[PATH RESOLVE] Found in uploads: {uploads_path}")
        return os.path.abspath(uploads_path).replace('\\', '/')
    
    # Strategy 2: Check if it's a relative path from src/resources/
    # This supports "uploads/file.pdf" pattern
    if file_path.startswith('uploads/') or file_path.startswith('uploads\\'):
        resources_path = os.path.join(project_root, 'src', 'resources', file_path)
        if os.path.exists(resources_path):
            logging.info(f"[PATH RESOLVE] Found in resources: {resources_path}")
            return os.path.abspath(resources_path).replace('\\', '/')
    
    # Strategy 3: Check if it's a relative path from project root
    project_relative = os.path.join(project_root, file_path)
    if os.path.exists(project_relative):
        logging.info(f"[PATH RESOLVE] Found relative to project: {project_relative}")
        return os.path.abspath(project_relative).replace('\\', '/')
    
    # Strategy 4: Check if it's an absolute path
    if os.path.isabs(file_path) and os.path.exists(file_path):
        logging.info(f"[PATH RESOLVE] Found absolute path: {file_path}")
        return os.path.abspath(file_path).replace('\\', '/')
    
    # File not found
    logging.warning(f"[PATH RESOLVE] File not found in any location: {file_path}")
    logging.warning(f"[PATH RESOLVE] Checked: {uploads_path}, {project_relative}, and absolute path")
    return None

def execute_test(browser_executor_class, recorded_sessions):
    """Execute a single test case."""
    try:
        session_id = request.json.get('session_id')
        data_overrides = request.json.get('data_overrides', {})
        
        if not session_id or session_id not in recorded_sessions:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session = recorded_sessions[session_id]
        
        # Log test execution start
        logging.info("=" * 80)
        logging.info(f"▶ EXECUTING TEST CASE: {session['name']}")
        logging.info(f"  Session ID: {session_id}")
        logging.info(f"  URL: {session['url']}")
        logging.info(f"  Total Steps: {len(session['actions'])}")
        logging.info("=" * 80)
        
        # Check if code has been edited
        has_edited_code = 'edited_code' in session and session['edited_code']
        if has_edited_code:
            return execute_edited_code(session, data_overrides)
        
        # Log data overrides if any
        if data_overrides:
            logging.info(f"[DATA OVERRIDE] Applying {len(data_overrides)} data overrides")
        
        # Create new browser executor
        browser_executor = browser_executor_class()
        browser_executor.initialize_driver('chrome', False)
        logging.info("[TEST EXECUTE] Initialized fresh browser session")
        
        # Navigate to URL
        browser_executor.driver.get(session['url'])
        time.sleep(3)
        
        # Execute each action
        steps_executed = 0
        total_steps = len(session['actions'])
        
        for action in session['actions']:
            step_num = action['step']
            action_type = action['action_type']
            
            logging.info(f"[STEP {step_num}] Executing: {action_type}")
            
            # Apply data override if exists
            value = data_overrides.get(str(step_num), action.get('value'))
            
            # Skip verify_message with no value
            if action_type == 'verify_message' and not value:
                continue
            
            # Get locator
            locator_str = action.get('suggested_locator', '')
            
            if action_type != 'verify_message' and locator_str:
                # Parse locator
                by_type, by_value = _parse_locator(locator_str)
                
                try:
                    wait = WebDriverWait(browser_executor.driver, 30)
                    
                    if action_type == 'click':
                        element = wait.until(EC.element_to_be_clickable((by_type, by_value)))
                        element.click()
                        time.sleep(2)  # Wait for page transition/AJAX
                    elif action_type == 'input':
                        element = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        element.send_keys(value)
                    elif action_type == 'click_and_input':
                        element = wait.until(EC.element_to_be_clickable((by_type, by_value)))
                        element.click()
                        time.sleep(0.5)
                        element.send_keys(value)
                    elif action_type == 'select':
                        element = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        select = Select(element)
                        select.select_by_visible_text(value)
                    elif action_type == 'upload_file':
                        # File upload - element must be <input type="file">
                        element = wait.until(EC.presence_of_element_located((by_type, by_value)))
                        # Support multiple files separated by pipe (|)
                        if '|' in value:
                            # Multiple files - send them with newline separator
                            file_paths = value.split('|')
                            # Verify all files exist and normalize paths
                            normalized_paths = []
                            for fp in file_paths:
                                # Remove quotes, whitespace, and invisible Unicode characters
                                fp = fp.strip().strip('"').strip("'").strip()
                                # Remove zero-width and control characters
                                fp = ''.join(char for char in fp if ord(char) >= 32 and char.isprintable())
                                
                                # Smart path resolution
                                resolved_path = _resolve_file_path(fp)
                                if not resolved_path:
                                    raise FileNotFoundError(f"File not found: {fp}")
                                normalized_paths.append(resolved_path)
                            element.send_keys('\n'.join(normalized_paths))
                            time.sleep(1.5)  # Wait for multiple files to upload
                        else:
                            # Single file - verify it exists
                            # Remove quotes, whitespace, and invisible Unicode characters
                            value = value.strip().strip('"').strip("'").strip()
                            # Remove zero-width and control characters (like Left-to-Right Embedding)
                            value = ''.join(char for char in value if ord(char) >= 32 and char.isprintable())
                            
                            # Smart path resolution
                            normalized_path = _resolve_file_path(value)
                            if not normalized_path:
                                logging.error(f"[FILE UPLOAD] File does not exist: {value}")
                                raise FileNotFoundError(f"File not found: {value}. Please check the path and try again.")
                            
                            logging.info(f"[FILE UPLOAD] File exists, uploading: {normalized_path}")
                            element.send_keys(normalized_path)
                            time.sleep(1)  # Wait for file to upload
                    elif action_type == 'drag_and_drop':
                        # Drag and drop requires source and target locators
                        from selenium.webdriver.common.action_chains import ActionChains
                        source = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        # Get target locator from action
                        target_locator_str = action.get('target_locator', '')
                        if target_locator_str:
                            target_by_type, target_by_value = _parse_locator(target_locator_str)
                            target = wait.until(EC.visibility_of_element_located((target_by_type, target_by_value)))
                            ActionChains(browser_executor.driver).drag_and_drop(source, target).perform()
                            time.sleep(1)  # Wait for drop animation
                    
                    steps_executed += 1
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"[STEP {step_num}] Failed: {str(e)}")
                    browser_executor.close()
                    return jsonify({
                        'success': False,
                        'error': f'Step {step_num} failed: {str(e)}',
                        'step': step_num
                    }), 400
        
        # Close browser
        browser_executor.close()
        
        logging.info("=" * 80)
        logging.info(f"✓ TEST PASSED: {session['name']}")
        logging.info(f"  Executed {steps_executed}/{total_steps} steps successfully")
        logging.info("=" * 80)
        
        return jsonify({
            'success': True,
            'passed': True,
            'test_name': session.get('name', 'Test'),
            'steps_executed': steps_executed,
            'total_steps': total_steps
        }), 200
        
    except Exception as e:
        logging.error(f"Error executing test: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _parse_locator(locator_str):
    """Parse locator string to By type and value."""
    # Example: By.xpath("//button[@id='submit']")
    match = re.search(r'By\.(\w+)\(["\'](.+)["\']\)', locator_str)
    if match:
        locator_type = match.group(1).lower()
        locator_value = match.group(2).replace('\\"', '"')
        
        # Map to Selenium By types
        by_map = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'cssselector': By.CSS_SELECTOR,
            'linktext': By.LINK_TEXT,
            'partiallinktext': By.PARTIAL_LINK_TEXT,
            'classname': By.CLASS_NAME,
            'tagname': By.TAG_NAME
        }
        
        return by_map.get(locator_type, By.XPATH), locator_value
    
    return By.XPATH, '//body'  # Fallback

def execute_test_suite(browser_executor_class, recorded_sessions):
    """Execute all test cases in the suite or filtered by module."""
    try:
        # Get module filter from request
        module_filter = None
        if request.json:
            module_filter = request.json.get('module')
        
        # Filter sessions by module if specified
        sessions_to_execute = {}
        if module_filter:
            for session_id, session in recorded_sessions.items():
                if session.get('module') == module_filter:
                    sessions_to_execute[session_id] = session
        else:
            sessions_to_execute = recorded_sessions
        
        if len(sessions_to_execute) == 0:
            error_msg = f'No test cases to execute' if not module_filter else f'No test cases found in module: {module_filter}'
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Log suite execution start
        logging.info("\n" + "=" * 80)
        logging.info(f"▶▶ EXECUTING TEST SUITE")
        logging.info(f"   Total Tests: {len(sessions_to_execute)}")
        if module_filter:
            logging.info(f"   Module Filter: {module_filter}")
        logging.info("=" * 80 + "\n")
        
        results = []
        passed_count = 0
        test_number = 0
        
        for session_id, session in sessions_to_execute.items():
            try:
                test_number += 1
                
                # Log individual test execution start
                logging.info("\n" + "-" * 80)
                logging.info(f"▶ TEST {test_number}/{len(sessions_to_execute)}: {session['name']}")
                logging.info(f"  Session ID: {session_id}")
                logging.info("-" * 80)
                
                # Initialize new browser for each test
                browser_executor = browser_executor_class()
                browser_executor.initialize_driver('chrome', False)
                
                # Navigate to URL
                browser_executor.driver.get(session['url'])
                time.sleep(3)
                
                # Execute each action
                steps_executed = 0
                total_steps = len(session['actions'])
                test_passed = True
                error_msg = None
                
                for action in session['actions']:
                    step_num = action['step']
                    action_type = action['action_type']
                    value = action.get('value')
                    
                    # Skip verify_message with no value
                    if action_type == 'verify_message' and not value:
                        continue
                    
                    # Get locator
                    locator_str = action.get('suggested_locator', '')
                    
                    if action_type != 'verify_message' and locator_str:
                        by_type, by_value = _parse_locator(locator_str)
                        
                        try:
                            wait = WebDriverWait(browser_executor.driver, 30)
                            
                            if action_type == 'click':
                                element = wait.until(EC.element_to_be_clickable((by_type, by_value)))
                                element.click()
                                time.sleep(2)
                            elif action_type == 'input':
                                element = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                                element.send_keys(value)
                            elif action_type == 'click_and_input':
                                element = wait.until(EC.element_to_be_clickable((by_type, by_value)))
                                element.click()
                                time.sleep(0.5)
                                element.send_keys(value)
                            elif action_type == 'select':
                                element = wait.until(EC.visibility_of_element_located((by_type, by_value)))
                                select = Select(element)
                                select.select_by_visible_text(value)
                            
                            steps_executed += 1
                            time.sleep(0.5)
                            
                        except Exception as e:
                            logging.error(f"[TEST {test_number}] Step {step_num} failed: {str(e)}")
                            test_passed = False
                            error_msg = f"Step {step_num} failed: {str(e)}"
                            break
                
                # Close browser
                browser_executor.close()
                
                # Record result
                if test_passed:
                    passed_count += 1
                    results.append({
                        'test_name': session['name'],
                        'status': 'passed',
                        'steps_executed': steps_executed,
                        'total_steps': total_steps
                    })
                    logging.info(f"✓ TEST {test_number} PASSED: {session['name']}")
                else:
                    results.append({
                        'test_name': session['name'],
                        'status': 'failed',
                        'error': error_msg,
                        'steps_executed': steps_executed,
                        'total_steps': total_steps
                    })
                    logging.error(f"✗ TEST {test_number} FAILED: {session['name']}")
                
            except Exception as e:
                logging.error(f"✗ TEST {test_number} FAILED: {session['name']} - {str(e)}")
                results.append({
                    'test_name': session['name'],
                    'status': 'failed',
                    'error': str(e),
                    'steps_executed': 0,
                    'total_steps': len(session['actions'])
                })
        
        # Suite summary
        failed_count = len(sessions_to_execute) - passed_count
        logging.info("\n" + "=" * 80)
        logging.info(f"SUITE EXECUTION COMPLETE")
        logging.info(f"  Total: {len(sessions_to_execute)} | Passed: {passed_count} | Failed: {failed_count}")
        logging.info("=" * 80 + "\n")
        
        return jsonify({
            'success': True,
            'total_tests': len(sessions_to_execute),
            'passed': passed_count,
            'failed': failed_count,
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Suite execution error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
