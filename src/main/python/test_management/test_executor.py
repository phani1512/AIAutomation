"""
Test execution handlers for single tests and test suites.
"""
import time
import logging
import tempfile
import subprocess
import os
import re
import json
from datetime import datetime
from flask import request, jsonify, session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from self_healing.self_healing_locator import SelfHealingLocator

# ============================================================================
# FEATURE FLAG: Advanced Self-Healing (v2)
# ============================================================================
# Set to True to enable advanced self-healing with confidence scoring,
# visual highlighting, and approval workflow. Default is False to use 
# the existing self-healing system (v1).
ENABLE_ADVANCED_HEALING = False  # Feature flag - DISABLED by default
# ============================================================================

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
    1. Files in resources/uploads/ directory (default for CI/CD)
    2. Relative paths from project root
    3. Absolute paths
    
    Returns normalized absolute path with forward slashes, or None if not found.
    """
    # Get project root (4 levels up from this file: python -> main -> src -> project)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    
    # Strategy 1: Check if file exists in resources/uploads/ (default location)
    # This allows users to just specify filename like "file.pdf" or "module/file.pdf"
    uploads_dir = os.path.join(project_root, 'resources', 'uploads')
    uploads_path = os.path.join(uploads_dir, file_path)
    if os.path.exists(uploads_path):
        logging.info(f"[PATH RESOLVE] Found in uploads: {uploads_path}")
        return os.path.abspath(uploads_path).replace('\\', '/')
    
    # Strategy 2: Check if it's a relative path from resources/
    # This supports "uploads/file.pdf" pattern
    if file_path.startswith('uploads/') or file_path.startswith('uploads\\'):
        resources_path = os.path.join(project_root, 'resources', file_path)
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

def _save_execution_result(execution_result: dict, test_type: str = 'recorder'):
    """Save execution result to JSON file.
    
    Args:
        execution_result: Dictionary containing execution data
        test_type: 'recorder' or 'builder' to determine subdirectory
    """
    try:
        # Get project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        # Create execution_results directory structure
        results_base = os.path.join(project_root, 'execution_results', test_type)
        os.makedirs(results_base, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = execution_result.get('test_name', 'test').replace(' ', '_')
        filename = f"{test_name}_{timestamp}.json"
        filepath = os.path.join(results_base, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(execution_result, f, indent=2, ensure_ascii=False)
        
        logging.info(f"[EXECUTION RESULT] Saved to: {filepath}")
        
        # Also generate HTML report
        html_path = _generate_html_report(execution_result, results_base, timestamp, test_name)
        if html_path:
            logging.info(f"[HTML REPORT] Generated: {html_path}")
        
        return filepath
    except Exception as e:
        logging.error(f"[EXECUTION RESULT] Failed to save: {str(e)}")
        return None


def _generate_html_report(execution_result: dict, results_base: str, timestamp: str, test_name: str):
    """Generate HTML report from execution result.
    
    Args:
        execution_result: Dictionary containing execution data
        results_base: Base directory for results
        timestamp: Timestamp string for filename
        test_name: Name of the test
    """
    try:
        status = execution_result.get('status', 'unknown')
        duration_ms = execution_result.get('duration_ms', 0)
        duration_sec = duration_ms / 1000.0
        steps = execution_result.get('steps_tested', [])
        steps_executed = execution_result.get('steps_executed', len(steps))
        error_message = execution_result.get('error_message', '')
        
        # Determine status styling
        if status == 'passed':
            status_color = '#28a745'
            status_bg = '#d4edda'
            status_icon = '✅'
        elif status == 'failed':
            status_color = '#dc3545'
            status_bg = '#f8d7da'
            status_icon = '❌'
        else:
            status_color = '#ffc107'
            status_bg = '#fff3cd'
            status_icon = '⚠️'
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report - {test_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-top: 0;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 15px;
        }}
        .summary {{
            background: {status_bg};
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 5px solid {status_color};
        }}
        .summary h2 {{
            margin-top: 0;
            color: {status_color};
        }}
        .summary-stat {{
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
        }}
        .summary-stat strong {{
            font-size: 1.2em;
            color: {status_color};
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            background: {status_color};
            color: white;
            font-weight: bold;
            font-size: 1.1em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f0f0f0;
        }}
        .error-box {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }}
        .error-box h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .error-message {{
            color: #721c24;
            font-family: monospace;
            white-space: pre-wrap;
            background: #f8d7da;
            padding: 10px;
            border-radius: 3px;
        }}
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{status_icon} Test Execution Report</h1>
        <p style="color: #666;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="summary">
            <h2>Test: {execution_result.get('test_name', 'Unknown')}</h2>
            <div class="summary-stat">
                Status: <span class="status-badge">{status.upper()}</span>
            </div>
            <div class="summary-stat">
                Duration: <strong>{duration_sec:.2f}s</strong>
            </div>
            <div class="summary-stat">
                Steps: <strong>{steps_executed}/{len(steps)}</strong>
            </div>
        </div>
"""
        
        # Add error section if present
        if error_message:
            html += f"""
        <div class="error-box">
            <h3>❌ Error Details</h3>
            <div class="error-message">{error_message}</div>
        </div>
"""
        
        # Add steps table
        html += """
        <h2>Execution Steps</h2>
        <table>
            <tr>
                <th>Step</th>
                <th>Action</th>
                <th>Target</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
"""
        
        for i, step in enumerate(steps, 1):
            step_status = '✅ Completed' if i <= steps_executed else '⏸️ Not Executed'
            action = step.get('action_type', 'unknown')
            element = step.get('element', {})
            target = element.get('suggested_locator', element.get('xpath', ''))
            value = step.get('value', '')
            
            html += f"""
            <tr>
                <td>{i}</td>
                <td>{action}</td>
                <td style="font-family: monospace; font-size: 0.9em;">{target}</td>
                <td>{value}</td>
                <td>{step_status}</td>
            </tr>
"""
        
        html += """
        </table>
        
        <div class="metadata">
            <p><strong>Test ID:</strong> """ + execution_result.get('session_id', 'N/A') + """</p>
            <p><strong>Execution Time:</strong> """ + execution_result.get('start_time', 'N/A') + """</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        html_filename = f"test_report_{test_name}_{timestamp}.html"
        html_filepath = os.path.join(results_base, html_filename)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return html_filepath
    except Exception as e:
        logging.error(f"[HTML REPORT] Failed to generate: {str(e)}")
        return None


def execute_test(browser_executor_class, recorded_sessions):
    """Execute a single test case with execution results and failure screenshots."""
    start_time = time.time()  # Track execution duration
    execution_result = {
        'session_id': None,
        'test_name': None,
        'start_time': datetime.now().isoformat(),
        'end_time': None,
        'status': 'running',
        'steps_executed': 0,
        'total_steps': 0,
        'failed_step': None,
        'error_message': None,
        'duration_ms': 0,
        'screenshots': []  # Only failure screenshots
    }
    
    # Get session_id, data_overrides, browser, and healing_mode from request
    try:
        session_id = request.json.get('session_id')
        data_overrides = request.json.get('data_overrides', {})
        browser = request.json.get('browser', 'chrome')  # Get browser selection (chrome, firefox, edge)
        healing_mode = request.json.get('healing_mode', 'v1')  # Get healing mode (v1 or v2, default v1)
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID is required'}), 400
        
        # Try to get session from memory first
        if session_id in recorded_sessions:
            session = recorded_sessions[session_id]
            logging.debug(f"[EXECUTOR] Found session in memory: {session_id}")
        else:
            # Try loading from disk (saved recorder test)
            from recorder.recorder_handler import load_saved_test_from_disk
            session = load_saved_test_from_disk(session_id)
            if not session:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            logging.info(f"[EXECUTOR] Loaded saved test from disk: {session_id}")
        
        execution_result['session_id'] = session_id
        execution_result['test_name'] = session.get('name', 'Test')
        
        # Check if this is a builder test with generated code (including semantic tests)
        is_builder_test = session.get('source') == 'builder'
        has_generated_code = 'generated_code' in session and session['generated_code']
        
        if is_builder_test and has_generated_code:
            # Use TestSuiteRunner for builder tests (handles semantic tests properly)
            logging.info(f"[EXECUTOR] Detected builder test, using TestSuiteRunner for execution")
            from test_management.test_suite_runner import TestSuiteRunner
            
            # Execute with TestSuiteRunner (it will load the test case from disk)
            runner = TestSuiteRunner()
            result = runner.execute_test_case(
                test_case_id=session_id,
                headless=False,
                browser_name=browser,
                data_overrides=data_overrides,
                execution_mode='json_steps'  # Use JSON step-by-step execution
            )
            
            # Convert TestResult to dict and return in same format as recorder tests
            result_dict = result.to_dict()
            return jsonify({
                'success': result.status == 'passed',
                'passed': result.status == 'passed',
                'execution_result': result_dict,
                'session_id': session_id,
                'test_name': result.test_name,
                'steps_executed': len(result.steps),
                'total_steps': len(result.steps),
                'duration_ms': int(result.duration * 1000) if result.duration else 0,
                'error': result.error_message if result.status in ['failed', 'error'] else None,
                'screenshots': result.screenshots,
                'logs': result.logs
            }), 200
        
        # For recorder tests, get total steps from actions
        execution_result['total_steps'] = len(session.get('actions', []))
        
        # Initialize self-healing locator based on healing_mode (overrides global flag)
        use_advanced = (healing_mode == 'v2') or ENABLE_ADVANCED_HEALING
        
        if use_advanced:
            try:
                from self_healing.advanced_self_healing import AdvancedSelfHealingLocator, ElementIdentity
                healer = AdvancedSelfHealingLocator()
                logging.info(f"[EXECUTOR] Using Advanced Self-Healing (v2) - Mode: {healing_mode}")
            except ImportError as e:
                logging.warning(f"[EXECUTOR] Advanced healing not available: {e}. Falling back to v1.")
                healer = SelfHealingLocator()
        else:
            healer = SelfHealingLocator()
            logging.debug(f"[EXECUTOR] Using Standard Self-Healing (v1) - Mode: {healing_mode}")
        
        # Log test execution start
        logging.info("=" * 80)
        logging.info(f"▶ EXECUTING TEST CASE: {session['name']}")
        logging.info(f"  Session ID: {session_id}")
        logging.info(f"  URL: {session.get('url', '')}")
        logging.info(f"  Total Steps: {len(session.get('actions', []))}")
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
        browser_executor.initialize_driver(browser, False)
        logging.info(f"[TEST EXECUTE] Initialized fresh {browser.upper()} browser session")
        
        # Navigate to URL
        browser_executor.driver.get(session['url'])
        time.sleep(3)
        
        # Close sticky popup after page load with explicit wait
        try:
            logging.info("[TEST EXECUTE] Checking for sticky popup...")
            popup_result = browser_executor.driver.execute_script("""
                var stickyClose = document.getElementById('sticky-close');
                if (stickyClose && stickyClose.offsetParent !== null) {
                    stickyClose.click();
                    // Wait for popup to actually disappear
                    var startTime = Date.now();
                    while (stickyClose.offsetParent !== null && (Date.now() - startTime) < 2000) {
                        // Busy wait for popup to disappear (max 2 seconds)
                    }
                    return stickyClose.offsetParent === null ? 'Popup closed and hidden' : 'Popup clicked but still visible';
                }
                return 'No visible popup found';
            """)
            logging.info(f"[TEST EXECUTE] Popup handling: {popup_result}")
            time.sleep(1)
        except Exception as e:
            logging.info(f"[TEST EXECUTE] No popup to close: {str(e)}")
        
        # Execute each action
        steps_executed = 0
        total_steps = len(session['actions'])
        current_url = session.get('url', '')
        
        for action in session['actions']:
            step_num = action['step']
            action_type = action['action_type']
            step_url = action.get('url', '')
            
            # Navigate to step URL if different from current URL
            if step_url and step_url != current_url:
                logging.info(f"[STEP {step_num}] Navigating to step URL: {step_url}")
                browser_executor.driver.get(step_url)
                current_url = step_url
                time.sleep(2)  # Wait for page load
                
                # Close popup after navigation
                try:
                    browser_executor.driver.execute_script("""
                        var stickyClose = document.getElementById('sticky-close');
                        if (stickyClose && stickyClose.offsetParent !== null) {
                            stickyClose.click();
                        }
                    """)
                    time.sleep(1)
                except Exception as e:
                    logging.debug(f"[STEP {step_num}] No popup after navigation: {str(e)}")
            
            # Close popup before EVERY action (silent - don't fail if already closed)
            try:
                popup_closed = browser_executor.driver.execute_script("""
                    try {
                        var popup = document.getElementById('sticky-close');
                        if (popup && popup.offsetParent !== null) {
                            popup.click();
                            return 'closed';
                        }
                        return 'already_closed';
                    } catch(e) {
                        return 'no_popup';
                    }
                """)
                if popup_closed == 'closed':
                    logging.info(f"[STEP {step_num}] Closed popup before action")
            except Exception as e:
                logging.debug(f"[STEP {step_num}] Popup close skipped: {str(e)}")
            
            logging.info(f"[STEP {step_num}] Executing: {action_type}")
            
            # Apply data override if exists
            value = data_overrides.get(str(step_num), action.get('value'))
            
            # Skip verify_message with no value
            if action_type == 'verify_message' and not value:
                continue
            
            # Get locator
            locator_str = action.get('suggested_locator', '')
            
            # Handle scroll action separately (no element locator needed)
            if action_type == 'scroll':
                try:
                    import json
                    scroll_data = json.loads(value) if value else {}
                    scroll_x = scroll_data.get('x', 0)
                    scroll_y = scroll_data.get('y', 0)
                    
                    logging.info(f"[SCROLL] Scrolling to position: x={scroll_x}, y={scroll_y}")
                    browser_executor.driver.execute_script(f"window.scrollTo({scroll_x}, {scroll_y});")
                    time.sleep(0.5)  # Brief pause after scroll
                    steps_executed += 1
                except Exception as e:
                    logging.error(f"[SCROLL] Step {step_num} failed: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': f"Step {step_num} failed: {str(e)}",
                        'step': step_num
                    }), 400
                continue
            
            if action_type != 'verify_message' and locator_str:
                try:
                    if action_type == 'click':
                        # Always scroll element into view for reliable clicking
                        try:
                            # Use self-healing locator with automatic fallback
                            element = healer.find_element(browser_executor.driver, locator_str)
                            if not element:
                                raise Exception(f"Could not find element with locator: {locator_str}")
                            
                            # Scroll to element (exactly like Java scrollToView)
                            browser_executor.driver.execute_script("arguments[0].scrollIntoView(false);", element)
                            time.sleep(0.5)
                            
                            # Wait for element to be clickable
                            wait = WebDriverWait(browser_executor.driver, 10)
                            by_type, by_value = _parse_locator(locator_str)
                            wait.until(EC.element_to_be_clickable((by_type, by_value)))
                            # Highlight element briefly to confirm it's visible (debugging aid)
                            browser_executor.driver.execute_script("""
                                arguments[0].style.border = '2px solid red';
                                setTimeout(() => arguments[0].style.border = '', 500);
                            """, element)
                            element.click()
                            time.sleep(2)
                        except Exception as e:
                            error_msg = str(e)
                            # If click is intercepted by sticky popup, close it and retry (environmental issue)
                            if 'click intercepted' in error_msg.lower():
                                logging.warning(f"[CLICK] Click intercepted by popup, closing it")
                                try:
                                    browser_executor.driver.execute_script("""
                                        var stickyClose = document.getElementById('sticky-close');
                                        if (stickyClose) {
                                            stickyClose.click();
                                            stickyClose.remove();
                                        }
                                    """)
                                    time.sleep(0.5)
                                    logging.info("[CLICK] Popup closed, retrying click")
                                except:
                                    pass
                                # Retry after closing popup - use healer again
                                element = healer.find_element(browser_executor.driver, locator_str)
                                if element:
                                    element.click()
                                    time.sleep(2)
                                else:
                                    raise Exception(f"Element still not found after popup close: {locator_str}")
                            else:
                                # Other error, just re-raise
                                raise
                    elif action_type == 'input':
                        # Extra popup close before input to ensure credentials are never blocked
                        try:
                            browser_executor.driver.execute_script("""
                                var popup = document.getElementById('sticky-close');
                                if (popup && popup.offsetParent !== null) {
                                    popup.click();
                                    popup.remove();
                                }
                            """)
                            time.sleep(0.3)  # Wait for popup to close
                        except:
                            pass
                        
                        # Use self-healing locator with automatic fallback
                        element = healer.find_element(browser_executor.driver, locator_str)
                        if not element:
                            raise Exception(f"Could not find element with locator: {locator_str}")
                        
                        # Scroll to element (exactly like Java scrollToView)
                        browser_executor.driver.execute_script("arguments[0].scrollIntoView(false);", element)
                        time.sleep(0.5)
                        
                        # Wait for visibility
                        wait = WebDriverWait(browser_executor.driver, 10)
                        by_type, by_value = _parse_locator(locator_str)
                        wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        
                        element.clear()
                        element.send_keys(value)
                    elif action_type == 'click_and_input':
                        # Extra popup close before input to ensure credentials are never blocked
                        try:
                            browser_executor.driver.execute_script("""
                                var popup = document.getElementById('sticky-close');
                                if (popup && popup.offsetParent !== null) {
                                    popup.click();
                                    popup.remove();
                                }
                            """)
                            time.sleep(0.3)  # Wait for popup to close
                        except:
                            pass
                        
                        # Use self-healing locator with automatic fallback
                        element = healer.find_element(browser_executor.driver, locator_str)
                        if not element:
                            raise Exception(f"Could not find element with locator: {locator_str}")
                        
                        # Scroll to element (exactly like Java scrollToView)
                        browser_executor.driver.execute_script("arguments[0].scrollIntoView(false);", element)
                        time.sleep(0.5)
                        
                        # Wait for element to be clickable
                        wait = WebDriverWait(browser_executor.driver, 10)
                        by_type, by_value = _parse_locator(locator_str)
                        wait.until(EC.element_to_be_clickable((by_type, by_value)))
                        
                        element.click()
                        time.sleep(0.5)
                        element.clear()
                        element.send_keys(value)
                    elif action_type == 'select':
                        # Use self-healing locator with automatic fallback
                        element = healer.find_element(browser_executor.driver, locator_str)
                        if not element:
                            raise Exception(f"Could not find element with locator: {locator_str}")
                        
                        # Scroll to element (exactly like Java scrollToView)
                        browser_executor.driver.execute_script("arguments[0].scrollIntoView(false);", element)
                        time.sleep(0.5)
                        
                        # Wait for visibility
                        wait = WebDriverWait(browser_executor.driver, 10)
                        by_type, by_value = _parse_locator(locator_str)
                        wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        
                        select = Select(element)
                        select.select_by_visible_text(value)
                    elif action_type == 'upload_file':
                        # Use self-healing locator with automatic fallback
                        element = healer.find_element(browser_executor.driver, locator_str)
                        if not element:
                            raise Exception(f"Could not find element with locator: {locator_str}")
                        
                        # Scroll to element (exactly like Java scrollToView)
                        browser_executor.driver.execute_script("arguments[0].scrollIntoView(false);", element)
                        time.sleep(0.5)
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
                        
                        # Use self-healing locator for source element
                        source = healer.find_element(browser_executor.driver, locator_str)
                        if not source:
                            raise Exception(f"Could not find source element with locator: {locator_str}")
                        
                        # Wait for source to be visible
                        wait = WebDriverWait(browser_executor.driver, 10)
                        by_type, by_value = _parse_locator(locator_str)
                        wait.until(EC.visibility_of_element_located((by_type, by_value)))
                        
                        # Get target locator from action
                        target_locator_str = action.get('target_locator', '')
                        if target_locator_str:
                            # Use self-healing locator for target element
                            target = healer.find_element(browser_executor.driver, target_locator_str)
                            if not target:
                                raise Exception(f"Could not find target element with locator: {target_locator_str}")
                            
                            # Wait for target to be visible
                            target_by_type, target_by_value = _parse_locator(target_locator_str)
                            wait.until(EC.visibility_of_element_located((target_by_type, target_by_value)))
                            
                            ActionChains(browser_executor.driver).drag_and_drop(source, target).perform()
                            time.sleep(1)  # Wait for drop animation
                    
                    steps_executed += 1
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"[STEP {step_num}] Failed: {str(e)}")
                    
                    # Capture failure screenshot - RECORDER tests
                    try:
                        screenshot_dir = os.path.join(os.getcwd(), 'execution_results', 'recorder', 'screenshots')
                        os.makedirs(screenshot_dir, exist_ok=True)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        test_id = execution_result.get('session_id', 'test')
                        screenshot_filename = f"{test_id}_step{step_num}_{timestamp}.png"
                        screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
                        
                        browser_executor.driver.save_screenshot(screenshot_path)
                        
                        # Store RELATIVE path for web access - execution_results/recorder/screenshots/
                        relative_path = os.path.join('execution_results', 'recorder', 'screenshots', screenshot_filename).replace('\\', '/')
                        
                        logging.info(f"[SCREENSHOT] RECORDER failure screenshot saved: {screenshot_path}")
                        logging.info(f"[SCREENSHOT] Relative path for web: {relative_path}")
                        
                        execution_result['screenshots'].append({
                            'step': step_num,
                            'type': 'failure',
                            'path': relative_path,  # execution_results/recorder/screenshots/
                            'filepath': screenshot_path,  # Full path for compatibility
                            'absolute_path': screenshot_path,  # Keep absolute for local access
                            'filename': screenshot_filename,
                            'timestamp': timestamp,
                            'error': str(e),
                            'source': 'recorder'  # Mark source for UI
                        })
                    except Exception as screenshot_error:
                        logging.warning(f"[SCREENSHOT] Failed to capture screenshot: {str(screenshot_error)}")
                    
                    # Update execution result
                    execution_result['status'] = 'failed'
                    execution_result['failed_step'] = step_num
                    execution_result['error_message'] = str(e)
                    execution_result['steps_executed'] = steps_executed
                    execution_result['end_time'] = datetime.now().isoformat()
                    execution_result['duration_ms'] = int((time.time() - start_time) * 1000)
                    
                    # Save execution result to file (persistent storage)
                    result_file = _save_execution_result(execution_result, 'recorder')
                    if result_file:
                        execution_result['result_file'] = result_file
                    
                    # Also store in session for backwards compatibility
                    if 'execution_history' not in session:
                        session['execution_history'] = []
                    session['execution_history'].append(execution_result)
                    
                    browser_executor.close()
                    return jsonify({
                        'success': False,
                        'error': f'Step {step_num} failed: {str(e)}',
                        'step': step_num,
                        'execution_result': execution_result
                    }), 400
        
        # Close browser
        browser_executor.close()
        
        duration_ms = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Update execution result for success
        execution_result['status'] = 'passed'
        execution_result['steps_executed'] = steps_executed
        execution_result['end_time'] = datetime.now().isoformat()
        execution_result['duration_ms'] = duration_ms
        
        # Save execution result to file (persistent storage)
        result_file = _save_execution_result(execution_result, 'recorder')
        if result_file:
            execution_result['result_file'] = result_file
        
        # Also store in session for backwards compatibility
        if 'execution_history' not in session:
            session['execution_history'] = []
        session['execution_history'].append(execution_result)
        
        logging.info("=" * 80)
        logging.info(f"✓ TEST PASSED: {session['name']}")
        logging.info(f"  Executed {steps_executed}/{total_steps} steps successfully")
        logging.info(f"  Duration: {duration_ms}ms")
        logging.info(f"  Result saved: {result_file}")
        logging.info("=" * 80)
        
        return jsonify({
            'success': True,
            'passed': True,
            'test_name': session.get('name', 'Test'),
            'steps_executed': steps_executed,
            'total_steps': total_steps,
            'duration': duration_ms,
            'result': execution_result,  # Frontend expects 'result' field
            'execution_result': execution_result  # Keep for backwards compatibility
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
        # Get module filter, browser selection, and healing mode from request
        module_filter = None
        browser = 'chrome'  # Default browser
        healing_mode = 'v1'  # Default to v1 (standard)
        if request.json:
            module_filter = request.json.get('module')
            browser = request.json.get('browser', 'chrome')  # Get browser selection
            healing_mode = request.json.get('healing_mode', 'v1')  # Get healing mode (v1 or v2)
        
        # Initialize self-healing locator based on healing_mode (overrides global flag)
        use_advanced = (healing_mode == 'v2') or ENABLE_ADVANCED_HEALING
        
        if use_advanced:
            try:
                from self_healing.advanced_self_healing import AdvancedSelfHealingLocator, ElementIdentity
                healer = AdvancedSelfHealingLocator()
                logging.info(f"[SUITE] Using Advanced Self-Healing (v2) - Mode: {healing_mode}")
            except ImportError as e:
                logging.warning(f"[SUITE] Advanced healing not available: {e}. Falling back to v1.")
                healer = SelfHealingLocator()
        else:
            healer = SelfHealingLocator()
            logging.debug(f"[SUITE] Using Standard Self-Healing (v1) - Mode: {healing_mode}")
        
        # Validate browser
        supported_browsers = ['chrome', 'firefox', 'edge']
        if browser not in supported_browsers:
            return jsonify({
                'success': False, 
                'error': f'Unsupported browser: {browser}. Supported: {", ".join(supported_browsers)}'
            }), 400
        
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
        logging.info(f"▶▶ EXECUTING TEST SUITE ON {browser.upper()}")
        logging.info(f"   Browser: {browser.upper()}")
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
                logging.info(f"▶ TEST {test_number}/{len(sessions_to_execute)}: {session['name']} on {browser.upper()}")
                logging.info(f"  Session ID: {session_id}")
                logging.info(f"  Browser: {browser.upper()}")
                logging.info("-" * 80)
                
                # Initialize new browser for each test with selected browser
                browser_executor = browser_executor_class()
                browser_executor.initialize_driver(browser, False)  # Use selected browser
                
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
                        try:
                            if action_type == 'click':
                                # Use self-healing locator with automatic fallback
                                element = healer.find_element(browser_executor.driver, locator_str)
                                if not element:
                                    raise Exception(f"Could not find element with locator: {locator_str}")
                                
                                # Wait for element to be clickable
                                wait = WebDriverWait(browser_executor.driver, 10)
                                by_type, by_value = _parse_locator(locator_str)
                                wait.until(EC.element_to_be_clickable((by_type, by_value)))
                                
                                element.click()
                                time.sleep(2)
                            elif action_type == 'input':
                                # Use self-healing locator with automatic fallback
                                element = healer.find_element(browser_executor.driver, locator_str)
                                if not element:
                                    raise Exception(f"Could not find element with locator: {locator_str}")
                                
                                # Wait for visibility
                                wait = WebDriverWait(browser_executor.driver, 10)
                                by_type, by_value = _parse_locator(locator_str)
                                wait.until(EC.visibility_of_element_located((by_type, by_value)))
                                
                                element.send_keys(value)
                            elif action_type == 'click_and_input':
                                # Use self-healing locator with automatic fallback
                                element = healer.find_element(browser_executor.driver, locator_str)
                                if not element:
                                    raise Exception(f"Could not find element with locator: {locator_str}")
                                
                                # Wait for element to be clickable
                                wait = WebDriverWait(browser_executor.driver, 10)
                                by_type, by_value = _parse_locator(locator_str)
                                wait.until(EC.element_to_be_clickable((by_type, by_value)))
                                
                                element.click()
                                time.sleep(0.5)
                                element.send_keys(value)
                            elif action_type == 'select':
                                # Use self-healing locator with automatic fallback
                                element = healer.find_element(browser_executor.driver, locator_str)
                                if not element:
                                    raise Exception(f"Could not find element with locator: {locator_str}")
                                
                                # Wait for visibility
                                wait = WebDriverWait(browser_executor.driver, 10)
                                by_type, by_value = _parse_locator(locator_str)
                                wait.until(EC.visibility_of_element_located((by_type, by_value)))
                                
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
