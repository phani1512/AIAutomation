"""
Test Suite Runner - Executes saved test cases and generates reports

Features:
- Execute single test cases
- Run test suites (multiple test cases)
- Capture execution results (pass/fail, screenshots, logs)
- Generate HTML reports
- Parallel execution support

Integrates with:
- test_case_builder: Load test cases
- browser_executor: Execute tests
- smart_prompt_handler: Process steps
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback

from browser.browser_executor import BrowserExecutor
from nlp.smart_prompt_handler import SmartPromptHandler
from .test_case_builder import TestCaseBuilder, get_test_case_builder
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from core.inference_improved import ImprovedSeleniumGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult:
    """Represents the result of a test execution."""
    
    def __init__(self, test_case_id: str, test_name: str):
        self.test_case_id = test_case_id
        self.test_name = test_name
        self.status = "not_started"  # not_started, running, passed, failed, error
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.steps = []  # List of step results
        self.error_message = None
        self.screenshots = []
        self.logs = []
        
    def start(self):
        """Mark test as started."""
        self.status = "running"
        self.start_time = datetime.now().isoformat()
        
    def finish(self, status: str, error_message: str = None):
        """Mark test as finished."""
        self.status = status
        self.end_time = datetime.now().isoformat()
        self.error_message = error_message
        
        # Calculate duration
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration = (end - start).total_seconds()
    
    def add_step_result(self, step_number: int, step_prompt: str, 
                       status: str, error: str = None):
        """Add result for a test step."""
        self.steps.append({
            'step': step_number,
            'prompt': step_prompt,
            'status': status,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_screenshot(self, filepath: str, description: str = ""):
        """Add screenshot reference."""
        self.screenshots.append({
            'filepath': filepath,
            'path': filepath,  # Add 'path' for UI compatibility
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'type': 'failure',  # Only failure screenshots are captured
            'source': 'builder'  # Mark source for UI
        })
    
    def add_log(self, level: str, message: str):
        """Add log entry."""
        self.logs.append({
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'test_case_id': self.test_case_id,
            'test_name': self.test_name,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'steps': self.steps,
            'error_message': self.error_message,
            'screenshots': self.screenshots,
            'logs': self.logs
        }


class TestSuiteRunner:
    """
    Executes test cases and generates reports.
    
    Features:
    - Single test execution
    - Test suite execution
    - Screenshot capture
    - HTML report generation
    - Parallel execution
    """
    
    def __init__(self, results_dir: str = None):
        """Initialize test runner with results directory."""
        if results_dir is None:
            # Use new folder structure: execution_results/builder/
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
            results_dir = os.path.join(project_root, 'execution_results', 'builder')
        
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Screenshot directory
        self.screenshots_dir = os.path.join(self.results_dir, 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Test case builder for loading tests
        self.builder = get_test_case_builder()
        
        logger.info(f"[TEST RUNNER] Initialized with directory: {self.results_dir}")
    
    def _close_sticky_popup(self, driver, step_label=""):
        """
        Close sticky popup if present (same logic as recorder execution).
        
        Args:
            driver: WebDriver instance
            step_label: Label for logging (e.g., "Step 1", "After navigation")
        """
        try:
            popup_result = driver.execute_script("""
                try {
                    var popup = document.getElementById('sticky-close');
                    if (popup && popup.offsetParent !== null) {
                        popup.click();
                        // Wait for popup to disappear
                        var startTime = Date.now();
                        while (popup.offsetParent !== null && (Date.now() - startTime) < 2000) {
                            // Busy wait up to 2 seconds
                        }
                        return popup.offsetParent === null ? 'closed' : 'clicked_but_visible';
                    }
                    return 'no_popup';
                } catch(e) {
                    return 'error: ' + e.message;
                }
            """)
            if popup_result == 'closed':
                logger.info(f"[{step_label}] Sticky popup closed")
            elif popup_result == 'clicked_but_visible':
                logger.warning(f"[{step_label}] Popup clicked but still visible")
            return popup_result
        except Exception as e:
            logger.debug(f"[{step_label}] Popup close skipped: {str(e)}")
            return None
    
    def _wait_for_angular(self, driver, timeout=10):
        """
        Wait for Angular app to finish loading and become ready.
        
        Args:
            driver: WebDriver instance
            timeout: Maximum seconds to wait
        """
        try:
            logger.info("[ANGULAR] Waiting for Angular app to be ready...")
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Wait for Angular to be defined and ready
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("""
                    // Check if Angular is defined
                    if (typeof window.angular === 'undefined' && 
                        typeof window.getAllAngularRootElements === 'undefined' &&
                        typeof window.getAllAngularTestabilities === 'undefined') {
                        return true;  // Not an Angular app, proceed
                    }
                    
                    // Wait for Angular to stabilize (for Angular 1.x)
                    if (window.angular && window.angular.element) {
                        try {
                            var injector = window.angular.element(document.body).injector();
                            if (injector) {
                                var $browser = injector.get('$browser');
                                var $http = injector.get('$http');
                                if ($browser.notifyWhenNoOutstandingRequests) {
                                    return $http.pendingRequests.length === 0;
                                }
                            }
                        } catch(e) {}
                    }
                    
                    // For Angular 2+, wait for testability
                    if (window.getAllAngularTestabilities) {
                        try {
                            var testabilities = window.getAllAngularTestabilities();
                            return testabilities.every(function(t) {
                                return t.isStable();
                            });
                        } catch(e) {}
                    }
                    
                    // Fallback: check for common Angular loading indicators
                    var spinners = document.querySelectorAll('.ng-hide, [ng-hide], .ng-spinner, .loading-spinner');
                    return spinners.length === 0 || 
                           Array.from(spinners).every(function(s) { return !s.offsetParent; });
                """)
            )
            logger.info("[ANGULAR] Angular app is ready")
            time.sleep(0.5)  # Small additional buffer for rendering
        except Exception as e:
            logger.warning(f"[ANGULAR] Wait timeout or not an Angular app: {str(e)}")
            time.sleep(1)  # Fallback wait
    
    def _execute_python_code(self, driver, python_code: str, prompt: str):
        """
        Execute generated Python code directly.
        
        Args:
            driver: WebDriver instance
            python_code: Generated Python code to execute
            prompt: Original user prompt (for logging)
            
        Returns:
            tuple: (success: bool, error_msg: str or None)
        """
        try:
            logger.info(f"[EXECUTE] Running Python code:")
            for i, line in enumerate(python_code.split('\n'), 1):
                logger.info(f"  {i}: {line}")
            
            # Clean the code: Remove test framework imports and decorators
            logger.info(f"[EXECUTE] ====== STARTING CODE CLEANING ======")
            original_code = python_code
            python_code = self._clean_code_for_execution(python_code)
            logger.info(f"[EXECUTE] ====== CODE CLEANING COMPLETE ======")
            
            logger.info(f"[EXECUTE] After cleaning:")
            for i, line in enumerate(python_code.split('\n'), 1):
                logger.info(f"  {i}: {line}")
            
            # Verify no pytest imports remain
            if 'pytest' in python_code.lower():
                logger.error(f"[EXECUTE] ⚠️ WARNING: 'pytest' still found in cleaned code!")
                logger.error(f"[EXECUTE] Original code length: {len(original_code)} chars")
                logger.error(f"[EXECUTE] Cleaned code length: {len(python_code)} chars")
            
            # Create execution context with necessary imports and driver
            exec_context = {
                'driver': driver,
                'By': By,
                'WebDriverWait': WebDriverWait,
                'EC': EC,
                'time': time,
                'Select': Select,
                'Keys': Keys,
                'ActionChains': ActionChains
            }
            
            # Execute the generated code
            exec(python_code, exec_context)
            
            logger.info(f"[EXECUTE] ✓ Code executed successfully")
            time.sleep(0.5)  # Small delay after execution
            return (True, None)
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"[EXECUTE] ✗ Execution failed: {error_msg}")
            logger.error(f"[EXECUTE] Code that failed:")
            for i, line in enumerate(python_code.split('\n'), 1):
                logger.error(f"  {i}: {line}")
            import traceback
            logger.error(f"[EXECUTE] Traceback:")
            logger.error(traceback.format_exc())
            return (False, error_msg)
    
    def _clean_code_for_execution(self, code: str) -> str:
        """
        Clean generated code for direct execution.
        Removes test framework imports, decorators, and function wrappers.
        Uses simple line-by-line filtering for reliability.
        
        Args:
            code: Generated Python code
            
        Returns:
            Cleaned code ready for exec()
        """
        import re
        
        lines = code.split('\n')
        cleaned_lines = []
        skip_lines = 0  # Counter for lines to skip
        skip_mode = None  # Either 'extract_body' or 'skip_entirely'
        in_docstring = False  # Track if we're inside a multi-line docstring
        docstring_delimiter = None  # Track which delimiter (""" or ''')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle multi-line docstrings
            if not in_docstring:
                # Check if this line starts a docstring
                if stripped.startswith('"""'):
                    in_docstring = True
                    docstring_delimiter = '"""'
                    # Check if it's a single-line docstring
                    if stripped.count('"""') >= 2 and len(stripped) > 6:
                        in_docstring = False  # Single line docstring, skip it
                    continue
                elif stripped.startswith("'''"):
                    in_docstring = True
                    docstring_delimiter = "'''"
                    # Check if it's a single-line docstring
                    if stripped.count("'''") >= 2 and len(stripped) > 6:
                        in_docstring = False  # Single line docstring, skip it
                    continue
            else:
                # We're inside a docstring, check if this line ends it
                if docstring_delimiter in stripped:
                    in_docstring = False
                    docstring_delimiter = None
                continue  # Skip this line (it's part of the docstring)
            
            # If we're skipping lines (inside a function), decrement counter
            if skip_lines > 0:
                # Check if this line starts a new def (nested function end)
                if re.match(r'^\S', line) and line.strip():  # Back to column 0
                    skip_lines = 0  # Stop skipping
                    skip_mode = None
                else:
                    skip_lines -= 1
                    # Only extract function body if mode is 'extract_body'
                    if skip_mode == 'extract_body' and line.strip():  # Non-empty line
                        # Extract function body (dedent by 4 spaces)
                        dedented = line[4:] if len(line) > 4 else line.lstrip()
                        cleaned_lines.append(dedented)
                    # If mode is 'skip_entirely', we just skip without adding
                    continue
            
            # Skip empty lines and comments at file level
            if not stripped or stripped.startswith('#'):
                continue
            
            # Docstrings already handled at the top of the loop
            
            # Remove ANY line with pytest or unittest
            if 'pytest' in stripped or 'unittest' in stripped:
                logger.info(f"[CLEAN] Skipping line: {stripped[:80]}")
                continue
            
            # Remove selenium imports (we provide these)
            if re.match(r'^\s*from\s+selenium', stripped) or \
               re.match(r'^\s*import\s+selenium', stripped):
                logger.info(f"[CLEAN] Skipping selenium import: {stripped[:80]}")
                continue
            
            # Remove decorators
            if stripped.startswith('@'):
                logger.info(f"[CLEAN] Skipping decorator: {stripped[:80]}")
                continue
            
            # Detect fixture function - skip ENTIRELY (must check BEFORE test function)
            if re.match(r'^\s*def\s+\w+.*driver.*request', stripped) or \
               re.match(r'^\s*def\s+driver\s*\(', stripped):
                logger.info(f"[CLEAN] Skipping fixture function ENTIRELY: {stripped[:80]}")
                skip_lines = 99999  # Skip entire function
                skip_mode = 'skip_entirely'  # Don't extract body
                continue
            
            # Detect test function - skip def line but EXTRACT body
            if re.match(r'^\s*def\s+(test_|setup_|teardown_)', stripped):
                logger.info(f"[CLEAN] Entering function (extracting body): {stripped[:80]}")
                # Count lines to skip (until we hit column 0 again)
                # Set a large number, will reset when we hit column 0
                skip_lines = 99999
                skip_mode = 'extract_body'  # Extract and dedent function body
                continue
            
            # Keep this line
            cleaned_lines.append(line)
        
        cleaned_code = '\n'.join(cleaned_lines)
        
        # Final safety check: remove any remaining pytest mentions
        cleaned_code = re.sub(r'(?m)^.*import\s+pytest.*$', '', cleaned_code)
        cleaned_code = re.sub(r'(?m)^.*from\s+pytest.*$', '', cleaned_code)
        cleaned_code = re.sub(r'(?m)^.*import\s+unittest.*$', '', cleaned_code)
        cleaned_code = re.sub(r'(?m)^.*from\s+unittest.*$', '', cleaned_code)
        
        # Remove extra blank lines
        cleaned_code = re.sub(r'\n\n\n+', '\n\n', cleaned_code)
        
        logger.info(f"[CLEAN] Original: {len(lines)} lines → Cleaned: {len(cleaned_code.splitlines())} lines")
        
        # CRITICAL DEBUG: Check if fixture leaked into cleaned code
        if 'def driver' in cleaned_code:
            logger.error("[CLEAN] ❌ CRITICAL: 'def driver' found in cleaned code! Fixture leaked!")
            logger.error(f"[CLEAN] Cleaned code preview:\n{cleaned_code[:500]}")
        else:
            logger.info("[CLEAN] ✓ Fixture function successfully removed")
        
        if 'yield driver' in cleaned_code:
            logger.error("[CLEAN] ❌ CRITICAL: 'yield driver' found in cleaned code! Fixture body leaked!")
        
        return cleaned_code.strip()
    
    def _convert_java_to_python(self, java_code: str) -> str:
        """
        Convert Java Selenium code to Python (legacy support for old test cases).
        
        Args:
            java_code: Java-style Selenium code
            
        Returns:
            Python-style Selenium code
        """
        python_code = java_code
        
        # Convert WebDriverWait initialization
        python_code = python_code.replace('WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));', 
                                         'wait = WebDriverWait(driver, 10)')
        
        # Convert wait.until calls
        python_code = python_code.replace('WebElement element = wait.until(ExpectedConditions.', 
                                         'element = wait.until(EC.')
        
        # Convert locator methods
        python_code = python_code.replace('visibilityOfElementLocated(By.', 
                                         'visibility_of_element_located((By.')
        python_code = python_code.replace('elementToBeClickable(By.', 
                                         'element_to_be_clickable((By.')
        python_code = python_code.replace('presenceOfElementLocated(By.',
                                         'presence_of_element_located((By.')
        
        # Fix closing parentheses
        python_code = python_code.replace('));', ')))')
        
        # Convert method calls
        python_code = python_code.replace('.click();', '.click()')
        python_code = python_code.replace('.clear();', '.clear()')
        python_code = python_code.replace('.sendKeys(', '.send_keys(')
        python_code = python_code.replace('.getText()', '.text')
        python_code = python_code.replace('.getAttribute(', '.get_attribute(')
        
        # Remove remaining semicolons
        python_code = python_code.replace('");', '")')
        python_code = python_code.replace("');", "')")
        python_code = python_code.replace(';', '')
        
        # Clean up extra parentheses
        while ')))' in python_code and python_code.count('(') < python_code.count(')'):
            python_code = python_code.replace(')))', '))')
        
        return python_code
    
    def _execute_generated_code(self, driver, generated_code: str, xpath_locator: str, prompt: str) -> bool:
        """
        Execute generated Selenium code.
        
        Args:
            driver: WebDriver instance
            generated_code: Generated code from inference engine
            xpath_locator: XPath/locator string (e.g., "By.id('login-button')")
            prompt: Original user prompt
            
        Returns:
            bool: True if execution successful, False otherwise
        """
        try:
            # Parse locator from xpath_locator string
            # Format: "By.id('value')" or "By.cssSelector('.class')" etc.
            locator_type = None
            locator_value = None
            
            if xpath_locator:
                import re
                # Extract By type and value
                match = re.search(r'By\.(id|cssSelector|xpath|linkText|name|className|tagName)\(["\']([^"\']+)["\']\)', xpath_locator)
                if match:
                    by_type_str = match.group(1)
                    locator_value = match.group(2)
                    
                    # Map string to By constant
                    by_mapping = {
                        'id': By.ID,
                        'cssSelector': By.CSS_SELECTOR,
                        'xpath': By.XPATH,
                        'linkText': By.LINK_TEXT,
                        'name': By.NAME,
                        'className': By.CLASS_NAME,
                        'tagName': By.TAG_NAME
                    }
                    locator_type = by_mapping.get(by_type_str)
            
            if not locator_type or not locator_value:
                raise Exception(f"Could not parse locator from: {xpath_locator}")
            
            # Determine action type from prompt
            prompt_lower = prompt.lower()
            
            # Wait for element
            wait = WebDriverWait(driver, 30)
            
            if any(keyword in prompt_lower for keyword in ['click', 'press', 'tap', 'select']):
                # Click action
                element = wait.until(EC.element_to_be_clickable((locator_type, locator_value)))
                element.click()
                time.sleep(0.5)
                
            elif any(keyword in prompt_lower for keyword in ['enter', 'type', 'input', 'fill']):
                # Input action - extract value from prompt
                import re
                # Pattern: "enter VALUE in FIELD" or "type VALUE"
                value_match = re.search(r'(?:enter|type|input|fill)\s+(.+?)\s+(?:in|into)', prompt, re.IGNORECASE)
                if not value_match:
                    value_match = re.search(r'(?:enter|type|input|fill)\s+(.+?)$', prompt, re.IGNORECASE)
                
                if value_match:
                    value = value_match.group(1).strip()
                    element = wait.until(EC.visibility_of_element_located((locator_type, locator_value)))
                    element.clear()
                    time.sleep(0.2)
                    element.send_keys(value)
                    time.sleep(0.3)
                else:
                    raise Exception(f"Could not extract value from prompt: {prompt}")
                    
            elif any(keyword in prompt_lower for keyword in ['select', 'choose', 'pick']) and 'dropdown' in prompt_lower:
                # Dropdown selection - extract option from prompt
                import re
                # Pattern: "select OPTION from DROPDOWN"
                option_match = re.search(r'(?:select|choose|pick)\s+(.+?)\s+from', prompt, re.IGNORECASE)
                
                if option_match:
                    option_text = option_match.group(1).strip()
                    dropdown_element = wait.until(EC.element_to_be_clickable((locator_type, locator_value)))
                    select = Select(dropdown_element)
                    select.select_by_visible_text(option_text)
                    time.sleep(0.3)
                else:
                    raise Exception(f"Could not extract option from prompt: {prompt}")
            else:
                # Generic element interaction
                element = wait.until(EC.presence_of_element_located((locator_type, locator_value)))
                # Just verify element exists
            
            return True
            
        except Exception as e:
            logger.error(f"[EXECUTE] Error: {str(e)}")
            raise
    
    def execute_python_file(self, test_case_id: str, headless: bool = False) -> TestResult:
        """
        Execute test case by running the exported Python file directly (HYBRID MODE).
        
        This provides a cleaner execution path using the actual .py file,
        while still collecting results and metadata.
        
        Args:
            test_case_id: Test case ID to execute
            headless: Run browser in headless mode
            
        Returns:
            TestResult object
        """
        # Load test case metadata from JSON
        test_case = self.builder.load_test_case(test_case_id)
        if not test_case:
            result = TestResult(test_case_id, "Unknown Test")
            result.finish("error", f"Test case {test_case_id} not found")
            return result
        
        # Find the exported Python file in test_suites/general/exports/
        exports_dir = self.builder.exports_dir
        python_file = os.path.join(exports_dir, f"{test_case_id}_test.py")
        
        if not os.path.exists(python_file):
            result = TestResult(test_case_id, test_case.name)
            result.finish("error", f"Python file not found: {python_file}")
            return result
        
        result = TestResult(test_case_id, test_case.name)
        result.start()
        result.add_log("info", f"Starting test: {test_case.name} (Python file mode)")
        result.add_log("info", f"Executing: {python_file}")
        
        try:
            # Execute using pytest subprocess
            import subprocess
            import sys
            
            env = os.environ.copy()
            env['HEADLESS'] = 'true' if headless else 'false'
            env['TEST_CASE_ID'] = test_case_id
            
            # Run pytest with the specific test file
            cmd = [sys.executable, '-m', 'pytest', python_file, '-v', '--tb=short']
            
            logger.info(f"[PYTHON FILE] Running: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Parse results
            if process.returncode == 0:
                result.add_log("info", "Test passed")
                result.add_log("info", f"Output:\n{process.stdout}")
                
                # Mark all steps as passed (from metadata)
                for step in test_case.steps:
                    result.add_step_result(step['step'], step['prompt'], "passed")
                
                result.finish("passed")
            else:
                result.add_log("error", "Test failed")
                result.add_log("error", f"Output:\n{process.stdout}")
                result.add_log("error", f"Errors:\n{process.stderr}")
                result.finish("failed", f"Exit code: {process.returncode}")
            
        except Exception as e:
            logger.error(f"[PYTHON FILE] Error executing: {str(e)}")
            result.add_log("error", f"Execution error: {str(e)}")
            result.finish("error", str(e))
        
        return result
    
    def execute_test_case(self, test_case_id: str, 
                         headless: bool = False,
                         browser_name: str = 'chrome',
                         data_overrides: Dict[str, str] = None,
                         execution_mode: str = 'json_steps') -> TestResult:
        """
        Execute a single test case.
        
        Args:
            test_case_id: Test case ID to execute
            headless: Run browser in headless mode
            browser_name: Browser to use (chrome, firefox, edge)
            data_overrides: Dict mapping step numbers to override values
            execution_mode: 'json_steps' (step-by-step with UI control) or 
                          'python_file' (direct pytest execution)
            
        Returns:
            TestResult object
        """
        # HYBRID MODE: Choose execution method
        if execution_mode == 'python_file':
            logger.info(f"[HYBRID] Executing test via Python file: {test_case_id}")
            return self.execute_python_file(test_case_id, headless)
        
        # DEFAULT: JSON step-by-step execution (original behavior)
        logger.info(f"[HYBRID] Executing test via JSON steps: {test_case_id}")
        
        if data_overrides is None:
            data_overrides = {}
            
        # Load test case
        test_case = self.builder.load_test_case(test_case_id)
        if not test_case:
            result = TestResult(test_case_id, "Unknown Test")
            result.finish("error", f"Test case {test_case_id} not found")
            return result
        
        # For semantic tests, also load the raw JSON to get actions field
        test_case_json = None
        all_steps_are_strings = all(isinstance(step, str) for step in test_case.steps) if test_case.steps else False
        if all_steps_are_strings:
            try:
                import json
                import glob
                # Search for test case JSON file
                json_files = glob.glob(f'test_suites/**/builder/{test_case_id}*.json', recursive=True)
                if json_files:
                    with open(json_files[0], 'r', encoding='utf-8') as f:
                        test_case_json = json.load(f)
                    logger.info(f"[SEMANTIC TEST] Loaded raw JSON from {json_files[0]}")
                    logger.info(f"[SEMANTIC TEST] Has 'actions' field: {('actions' in test_case_json)}")
                    if 'actions' in test_case_json:
                        logger.info(f"[SEMANTIC TEST] Actions type: {type(test_case_json['actions'])}, count: {len(test_case_json['actions'])}")
                        if test_case_json['actions']:
                            logger.info(f"[SEMANTIC TEST] First action type: {type(test_case_json['actions'][0])}")
            except Exception as e:
                logger.warning(f"[SEMANTIC TEST] Could not load raw JSON: {e}")
        
        result = TestResult(test_case_id, test_case.name)
        result.start()
        result.add_log("info", f"Starting test: {test_case.name}")
        
        # Initialize browser and code generator
        browser_executor = BrowserExecutor()
        code_generator = ImprovedSeleniumGenerator(silent=True)
        current_url = None
        
        try:
            # Initialize browser with selected browser
            success = browser_executor.initialize_driver(browser=browser_name, headless=headless)
            if not success or not browser_executor.driver:
                error_msg = f"Failed to initialize {browser_name} browser. Check if {browser_name} is installed."
                result.add_log("error", error_msg)
                result.status = "failed"
                result.error = error_msg
                return result
            result.add_log("info", f"Browser initialized: {browser_name}")
            
            # Navigate to test URL if specified
            test_url = test_case.url if hasattr(test_case, 'url') and test_case.url else None
            if not test_url and test_case.steps:
                # Handle both dictionary steps (normal tests) and string steps (semantic tests)
                first_step = test_case.steps[0] if test_case.steps else None
                if first_step and isinstance(first_step, dict):
                    test_url = first_step.get('url')
                # For semantic tests with string steps, URL should be in test_case.url
            
            if test_url:
                logger.info(f"[TEST RUNNER] Navigating to: {test_url}")
                browser_executor.driver.get(test_url)
                current_url = test_url
                
                # Wait for page load completion
                time.sleep(2)  # Basic wait for network
                
                # Wait for Angular to be ready (if it's an Angular app)
                self._wait_for_angular(browser_executor.driver)
                
                result.add_log("info", f"Navigated to: {test_url}")
                
                # Close sticky popup after initial page load
                self._close_sticky_popup(browser_executor.driver, "After page load")
            
            # Execute each step
            # Check if semantic test (steps are documentation strings, real steps in prompts)
            has_prompts = hasattr(test_case, 'prompts') and test_case.prompts and len(test_case.prompts) > 0
            is_semantic_test = test_case.steps and all(isinstance(step, str) for step in test_case.steps)
            
            # For semantic tests with prompts, use prompts field instead of steps
            if is_semantic_test and has_prompts:
                logger.info(f"[SEMANTIC TEST] Using prompts field ({len(test_case.prompts)} prompts) instead of steps (documentation)")
                execution_steps = test_case.prompts  # Use prompts as steps
                # Log documentation steps for reference
                for i, doc_step in enumerate(test_case.steps, 1):
                    logger.info(f"[SEMANTIC TEST] Scenario #{i}: {doc_step}")
                    result.add_log("info", f"📋 Scenario #{i}: {doc_step}")
            else:
                execution_steps = test_case.steps  # Use regular steps
            
            for step in execution_steps:
                # Handle semantic tests where steps are strings (documentation - shouldn't execute these)
                if isinstance(step, str):
                    logger.info(f"[SEMANTIC TEST] Skipping documentation string: {step}")
                    result.add_log("info", f"📋 Test Scenario: {step}")
                    continue
                
                # Normal test with dictionary steps
                step_number = step['step']
                prompt = step['prompt']
                step_url = step.get('url')
                step_value = step.get('value')  # NEW: Get stored value
                
                # Navigate to step URL if different
                if step_url and step_url != current_url:
                    logger.info(f"[STEP {step_number}] Navigating to: {step_url}")
                    browser_executor.driver.get(step_url)
                    current_url = step_url
                    
                    # Wait for page load completion
                    time.sleep(2)  # Basic wait for network
                    
                    # Wait for Angular to be ready (if it's an Angular app)
                    self._wait_for_angular(browser_executor.driver)
                    
                    result.add_log("info", f"Step {step_number}: Navigated to {step_url}")
                    
                    # Close popup after navigation
                    self._close_sticky_popup(browser_executor.driver, f"Step {step_number} After navigation")
                
                # Determine the value to use: override > stored > extracted from prompt
                effective_value = None
                if str(step_number) in data_overrides:
                    # User provided override
                    effective_value = data_overrides[str(step_number)]
                    logger.info(f"[DATA OVERRIDE] Step {step_number}: Using override value: {effective_value}")
                elif step_value:
                    # Use stored value from when step was created
                    effective_value = step_value
                    logger.info(f"[STORED VALUE] Step {step_number}: Using stored value: {effective_value}")
                else:
                    # Try to extract from prompt (fallback for old tests)
                    import re
                    # Try input actions first
                    match = re.search(r'(?:type|enter|input|fill|search|write)\s+["\']?([^"\'\s]+)["\']?', prompt, re.IGNORECASE)
                    if not match:
                        # Try select/dropdown actions (e.g., "select California from state dropdown")
                        match = re.search(r'(?:select|choose|pick)\s+([^\s]+)\s+(?:from|in)', prompt, re.IGNORECASE)
                    if not match:
                        # Try filter/search actions (e.g., "filter table by Active")
                        match = re.search(r'(?:filter|find|lookup)\s+(?:table\s+)?(?:by|for)\s+([^\s]+)', prompt, re.IGNORECASE)
                    
                    if match:
                        effective_value = match.group(1).strip()
                        logger.info(f"[EXTRACTED VALUE] Step {step_number}: Extracted from prompt: {effective_value}")
                
                # DO NOT modify the prompt - keep it as-is for dataset matching
                # The value will be injected via placeholder replacement in generated code
                if effective_value:
                    logger.info(f"[VALUE READY] Step {step_number}: Value '{effective_value}' ready for placeholder replacement")
                
                result.add_log("info", f"Step {step_number}: {prompt}")
                logger.info(f"[STEP {step_number}] Processing: {prompt}")
                
                # Close popup before EVERY action
                self._close_sticky_popup(browser_executor.driver, f"Step {step_number} Before action")
                
                try:
                    # Use stored generated_code from step (should be Python now)
                    generated_code = step.get('generated_code', '')
                    
                    if not generated_code or generated_code.startswith('#'):
                        # No valid code stored, generate fresh Python code
                        logger.info(f"[STEP {step_number}] No stored code, generating fresh Python code...")
                        inference_result = code_generator.infer(prompt, return_alternatives=False, language='python')
                        if inference_result and 'code' in inference_result:
                            generated_code = inference_result['code']
                        else:
                            raise Exception(f"Failed to generate code for prompt: {prompt}")
                    else:
                        logger.info(f"[STEP {step_number}] Using stored generated code")
                    
                    # Legacy support: Convert Java syntax to Python if old test cases have Java code
                    if 'WebDriverWait wait = new WebDriverWait' in generated_code or 'WebElement element' in generated_code:
                        logger.warning(f"[CONVERSION] Detected Java code, converting to Python (legacy support)")
                        generated_code = self._convert_java_to_python(generated_code)
                    
                    # Substitute ALL placeholders in generated code with effective_value
                    if effective_value and generated_code:
                        # Replace all common placeholder types (uppercase with braces)
                        placeholders = ['{VALUE}', '{TEXT}', '{SEARCH_TEXT}', '{OPTION}', 
                                      '{STATE}', '{EMAIL}', '{DATA}', '{CRITERIA}']
                        for placeholder in placeholders:
                            if placeholder in generated_code:
                                generated_code = generated_code.replace(placeholder, effective_value)
                                logger.info(f"[PLACEHOLDER] Replaced {placeholder} with: {effective_value}")
                        
                        # Replace lowercase parameter-style placeholders (e.g., send_keys(value))
                        # These are used in the dataset as function parameters
                        import re
                        # Replace 'value' parameter in send_keys() calls
                        value_pattern = r'\.send_keys\(value\)'
                        if re.search(value_pattern, generated_code):
                            generated_code = re.sub(value_pattern, f'.send_keys("{effective_value}")', generated_code)
                            logger.info(f"[PLACEHOLDER] Replaced send_keys(value) with: {effective_value}")
                        
                        # Replace 'value' parameter in selectByVisibleText() calls
                        select_pattern = r'selectByVisibleText\(value\)'
                        if re.search(select_pattern, generated_code):
                            generated_code = re.sub(select_pattern, f'selectByVisibleText("{effective_value}")', generated_code)
                            logger.info(f"[PLACEHOLDER] Replaced selectByVisibleText(value) with: {effective_value}")
                    
                    logger.info(f"[STEP {step_number}] Final Python code to execute:")
                    logger.info(f"{generated_code}")
                    
                    # Execute the generated Python code directly
                    execution_result = self._execute_python_code(
                        browser_executor.driver,
                        generated_code,
                        prompt
                    )
                    
                    # execution_result is now (success: bool, error_msg: str or None)
                    if isinstance(execution_result, tuple):
                        execution_success, error_msg = execution_result
                    else:
                        # Backward compatibility - if old version returns just bool
                        execution_success = execution_result
                        error_msg = "Execution returned False" if not execution_success else None
                    
                    if execution_success:
                        result.add_step_result(step_number, prompt, "passed")
                        result.add_log("info", f"Step {step_number} passed")
                        logger.info(f"[STEP {step_number}] ✓ Passed")
                        
                        # Don't capture screenshots for passed steps (only failures)
                    else:
                        raise Exception(error_msg or "Execution returned False")
                    
                    # Small delay between steps
                    time.sleep(0.5)
                    
                except Exception as step_error:
                    error_msg = str(step_error)
                    result.add_step_result(step_number, prompt, "error", error_msg)
                    result.add_log("error", f"Step {step_number} error: {error_msg}")
                    logger.error(f"[STEP {step_number}] ✗ Error: {error_msg}")
                    
                    # Take screenshot on error ONLY - BUILDER tests
                    screenshot_path = self._capture_screenshot(
                        browser_executor,
                        f"{test_case_id}_step_{step_number}_ERROR",
                        f"Step {step_number} ERROR: {prompt}"
                    )
                    if screenshot_path:
                        # Convert to relative path for UI: execution_results/builder/screenshots/
                        relative_path = screenshot_path.replace(os.getcwd() + os.sep, '').replace('\\', '/')
                        result.add_screenshot(relative_path, f"Step {step_number} - ERROR")
                    
                    result.finish("error", f"Step {step_number} error: {error_msg}")
                    return result
            
            # After step loop: Check if this was a semantic test (all steps were strings)
            # If so, execute the full generated Python code
            all_steps_are_strings = all(isinstance(step, str) for step in test_case.steps) if test_case.steps else False
            
            if all_steps_are_strings and test_case.steps:
                logger.info("[SEMANTIC TEST] All steps are scenario descriptions, executing full generated code")
                result.add_log("info", "Executing semantic test with generated code")
                
                # Get the generated Python code
                python_code = test_case.generated_code.get('python', '') if hasattr(test_case, 'generated_code') else ''
                
                if python_code and python_code.strip():
                    try:
                        # APPLY DATA OVERRIDES: Replace hardcoded values with user-provided values
                        if data_overrides:
                            logger.info(f"[SEMANTIC TEST] Applying {len(data_overrides)} data overrides")
                            result.add_log("info", f"Applying user-provided test data: {len(data_overrides)} fields")
                            
                            # Get actions from raw JSON (TestCase.to_dict() doesn't include them)
                            actions = test_case_json.get('actions', []) if test_case_json else []
                            logger.info(f"[DATA OVERRIDE] Loaded {len(actions)} actions from JSON (test_case_json exists: {test_case_json is not None})")
                            
                            if not actions:
                                logger.warning("[DATA OVERRIDE] No actions found, trying prompts field")
                                actions = test_case_json.get('prompts', []) if test_case_json else []
                                logger.info(f"[DATA OVERRIDE] Loaded {len(actions)} prompts as fallback")
                            
                            # For each override, find the corresponding action and replace values
                            for override_key, override_value in data_overrides.items():
                                # override_key can be like "0", "1" (field indices) or "step_1", "step_2"
                                try:
                                    field_index = int(override_key) if override_key.isdigit() else int(override_key.replace('step_', '')) - 1
                                    
                                    if field_index < len(actions):
                                        action = actions[field_index]
                                        
                                        # Defensive check: action must be a dict
                                        if not isinstance(action, dict):
                                            logger.warning(f"[DATA OVERRIDE] Action at index {field_index} is not a dict (got {type(action).__name__}), skipping")
                                            continue
                                        
                                        # Get original value from action
                                        original_value = action.get('value', '')
                                        
                                        if original_value and override_value != original_value:
                                            logger.info(f"[DATA OVERRIDE] Field {field_index}: '{original_value[:50]}' → '{override_value[:50]}'")
                                            
                                            # Escape special regex characters in original value
                                            import re
                                            escaped_original = re.escape(original_value)
                                            
                                            # Replace all occurrences in the code
                                            # Match send_keys("original_value") patterns
                                            pattern = rf'\.send_keys\(["\']({escaped_original})["\']'
                                            if re.search(pattern, python_code):
                                                python_code = re.sub(pattern, f'.send_keys("{override_value}")', python_code)
                                                logger.info(f"[REPLACED] send_keys pattern matched")
                                            
                                            # Also try direct string replacement
                                            if f'"{original_value}"' in python_code:
                                                python_code = python_code.replace(f'"{original_value}"', f'"{override_value}"')
                                                logger.info(f"[REPLACED] Direct string match")
                                            elif f"'{original_value}'" in python_code:
                                                python_code = python_code.replace(f"'{original_value}'", f"'{override_value}'")
                                                logger.info(f"[REPLACED] Direct string match (single quotes)")
                                    else:
                                        logger.warning(f"[DATA OVERRIDE] Field index {field_index} out of range (only {len(actions)} actions)")
                                except (ValueError, IndexError) as e:
                                    logger.warning(f"[DATA OVERRIDE] Could not parse field index from '{override_key}': {e}")
                        
                        # CLEAN INVALID PYTHON 3 SYNTAX: Remove leading zeros from integer literals
                        # Python 3 doesn't allow octal literals with leading zeros (010 is invalid)
                        import re
                        
                        # Pattern 1: Find sleep(0XX) patterns - most common issue
                        sleep_pattern = r'\.sleep\(0(\d+)\)'
                        matches = re.findall(sleep_pattern, python_code)
                        if matches:
                            logger.warning(f"[CODE CLEAN] Found {len(matches)} sleep() calls with leading zeros")
                            for match in set(matches):
                                original = f'.sleep(0{match})'
                                fixed = f'.sleep({match})'
                                python_code = python_code.replace(original, fixed)
                                logger.info(f"[CODE CLEAN] Fixed: {original} → {fixed}")
                        
                        # Pattern 2: General integer literals with leading zeros
                        # Match 0+digits but NOT 0.digits (floats) and NOT 0x (hex)
                        general_pattern = r'(?<!\.)(?<!0x)(?<!0X)\b0+(\d+)\b(?!\.)'
                        matches = re.findall(general_pattern, python_code)
                        if matches:
                            logger.warning(f"[CODE CLEAN] Found {len(matches)} other integer literals with leading zeros")
                            for match in set(matches):
                                # Find the full pattern (including all leading zeros)
                                full_pattern = rf'\b0+{match}\b'
                                python_code = re.sub(full_pattern, match, python_code)
                                logger.info(f"[CODE CLEAN] Fixed: 0...{match} → {match}")
                        
                        # CRITICAL FIX: Remove double closing parentheses (syntax errors from code generation)
                        # Pattern: method_name("value")) - extra closing paren after method call
                        double_paren_pattern = r'\.(send_keys|click|clear|submit|get)\(([^)]*)\)\)'
                        matches = re.findall(double_paren_pattern, python_code)
                        if matches:
                            logger.warning(f"[SYNTAX FIX] Found {len(matches)} double closing parentheses")
                            for method, args in set(matches):
                                original = f'.{method}({args}))'
                                fixed = f'.{method}({args})'
                                python_code = python_code.replace(original, fixed)
                                logger.info(f"[SYNTAX FIX] Fixed: .{method}(...)) → .{method}(...)") 
                        
                        # Additional check: unmatched parentheses at end of lines
                        lines = python_code.split('\n')
                        fixed_lines = []
                        for line in lines:
                            stripped = line.strip()
                            # Check if line ends with )) and it's NOT a valid nested call
                            if stripped.endswith('))') and not any(pattern in stripped for pattern in ['wait.until(', 'EC.', 'print((', 'str((', 'int((']):
                                # Count opening and closing parens
                                open_count = stripped.count('(')
                                close_count = stripped.count(')')
                                if close_count > open_count:
                                    # Remove extra closing parens from end
                                    extra_closes = close_count - open_count
                                    fixed_line = line.rstrip(')' * extra_closes)
                                    logger.warning(f"[SYNTAX FIX] Line '{stripped[:60]}...' has {extra_closes} extra closing parens")
                                    logger.info(f"[SYNTAX FIX] Fixed to: '{fixed_line.strip()}'")
                                    fixed_lines.append(fixed_line)
                                else:
                                    fixed_lines.append(line)
                            else:
                                fixed_lines.append(line)
                        python_code = '\n'.join(fixed_lines)
                        
                        logger.info("[SEMANTIC TEST] Executing generated Python code:")
                        logger.info(python_code)
                        
                        execution_result = self._execute_python_code(
                            browser_executor.driver,
                            python_code,
                            "Full semantic test"
                        )
                        
                        if isinstance(execution_result, tuple):
                            execution_success, error_msg = execution_result
                        else:
                            execution_success = execution_result
                            error_msg = "Execution returned False" if not execution_success else None
                        
                        if execution_success:
                            result.add_log("info", "Semantic test executed successfully")
                            logger.info("[SEMANTIC TEST] ✓ Execution successful")
                        else:
                            raise Exception(error_msg or "Semantic test execution failed")
                            
                    except Exception as semantic_error:
                        error_msg = str(semantic_error)
                        result.add_log("error", f"Semantic test error: {error_msg}")
                        logger.error(f"[SEMANTIC TEST] ✗ Error: {error_msg}")
                        
                        # Take screenshot
                        screenshot_path = self._capture_screenshot(
                            browser_executor,
                            f"{test_case_id}_semantic_ERROR",
                            "Semantic test execution error"
                        )
                        if screenshot_path:
                            relative_path = screenshot_path.replace(os.getcwd() + os.sep, '').replace('\\', '/')
                            result.add_screenshot(relative_path, "Semantic test ERROR")
                        
                        result.finish("error", f"Semantic test error: {error_msg}")
                        return result
                else:
                    logger.warning("[SEMANTIC TEST] No generated Python code found")
                    result.add_log("warning", "No generated code available for semantic test")
            
            # All steps passed
            result.finish("passed")
            result.add_log("info",f"Test passed: {test_case.name}")
            
        except Exception as e:
            error_msg = f"Test execution error: {str(e)}\n{traceback.format_exc()}"
            result.finish("error", error_msg)
            result.add_log("error", error_msg)
            
        finally:
            # Clean up browser
            try:
                if browser_executor.driver:
                    browser_executor.driver.quit()
                    result.add_log("info", "Browser closed")
            except Exception as cleanup_error:
                result.add_log("warning", f"Browser cleanup error: {cleanup_error}")
        
        # Save result
        self._save_result(result)
        
        return result
    
    def _capture_screenshot(self, browser_executor: BrowserExecutor,
                           filename: str, description: str = "") -> Optional[str]:
        """Capture screenshot during test execution (BUILDER tests only)."""
        try:
            if browser_executor.driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(self.screenshots_dir, f"{filename}_{timestamp}.png")
                
                browser_executor.driver.save_screenshot(filepath)
                logger.info(f"[TEST RUNNER] BUILDER failure screenshot saved: {filepath}")
                return filepath
        except Exception as e:
            logger.warning(f"[TEST RUNNER] Screenshot failed: {e}")
        
        return None
    
    def _save_result(self, result: TestResult):
        """Save test result to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.test_case_id}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"[TEST RUNNER] Result saved: {filepath}")
    
    def execute_suite(self, test_case_ids: List[str],
                     parallel: bool = False,
                     max_workers: int = 3) -> List[TestResult]:
        """
        Execute multiple test cases.
        
        Args:
            test_case_ids: List of test case IDs to execute
            parallel: Run tests in parallel
            max_workers: Max parallel workers (if parallel=True)
            
        Returns:
            List of TestResult objects
        """
        if parallel:
            return self._execute_suite_parallel(test_case_ids, max_workers)
        else:
            return self._execute_suite_sequential(test_case_ids)
    
    def _execute_suite_sequential(self, test_case_ids: List[str]) -> List[TestResult]:
        """Execute test cases sequentially."""
        results = []
        
        for test_case_id in test_case_ids:
            logger.info(f"[TEST RUNNER] Executing {test_case_id}...")
            result = self.execute_test_case(test_case_id)
            results.append(result)
        
        return results
    
    def _execute_suite_parallel(self, test_case_ids: List[str],
                               max_workers: int) -> List[TestResult]:
        """Execute test cases in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test executions
            future_to_id = {
                executor.submit(self.execute_test_case, tc_id): tc_id
                for tc_id in test_case_ids
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_id):
                test_case_id = future_to_id[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"[TEST RUNNER] Completed {test_case_id}: {result.status}")
                except Exception as e:
                    logger.error(f"[TEST RUNNER] Execution error for {test_case_id}: {e}")
        
        return results
    
    def generate_report(self, results: List[TestResult]) -> str:
        """
        Generate HTML report from test results.
        
        Args:
            results: List of TestResult objects
            
        Returns:
            Path to HTML report
        """
        # Calculate summary
        total = len(results)
        passed = sum(1 for r in results if r.status == "passed")
        failed = sum(1 for r in results if r.status == "failed")
        errors = sum(1 for r in results if r.status == "error")
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary-stat {{ display: inline-block; margin-right: 30px; }}
        .passed {{ color: green; font-weight: bold; }}
        .failed {{ color: red; font-weight: bold; }}
        .error {{ color: orange; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .status-passed {{ background-color: #d4edda; }}
        .status-failed {{ background-color: #f8d7da; }}
        .status-error {{ background-color: #fff3cd; }}
    </style>
</head>
<body>
    <h1>Test Execution Report</h1>
    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-stat">Total: <strong>{total}</strong></div>
        <div class="summary-stat passed">Passed: {passed}</div>
        <div class="summary-stat failed">Failed: {failed}</div>
        <div class="summary-stat error">Errors: {errors}</div>
        <div class="summary-stat">Pass Rate: <strong>{pass_rate:.1f}%</strong></div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test ID</th>
            <th>Test Name</th>
            <th>Status</th>
            <th>Duration (s)</th>
            <th>Steps</th>
            <th>Error Message</th>
        </tr>
"""
        
        for result in results:
            status_class = f"status-{result.status}"
            error_msg = result.error_message or "-"
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            
            html += f"""
        <tr class="{status_class}">
            <td>{result.test_case_id}</td>
            <td>{result.test_name}</td>
            <td>{result.status.upper()}</td>
            <td>{result.duration:.2f}</td>
            <td>{len(result.steps)}</td>
            <td>{error_msg}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.html"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[TEST RUNNER] Report generated: {filepath}")
        return filepath


# Global test runner instance
_test_runner = None

def get_test_runner() -> TestSuiteRunner:
    """Get or create global test runner instance."""
    global _test_runner
    if _test_runner is None:
        _test_runner = TestSuiteRunner()
    return _test_runner


# Example usage
if __name__ == "__main__":
    # Test the runner
    runner = TestSuiteRunner()
    
    # Execute a test case (assumes TC001 exists)
    print("\n" + "="*80)
    print("EXECUTING TEST CASE: TC001")
    print("="*80)
    
    result = runner.execute_test_case("TC001", headless=False)
    
    print(f"\nTest Status: {result.status}")
    print(f"Duration: {result.duration:.2f} seconds")
    print(f"Steps: {len(result.steps)}")
    if result.error_message:
        print(f"Error: {result.error_message}")
    
    # Generate report
    report_path = runner.generate_report([result])
    print(f"\nReport saved to: {report_path}")
