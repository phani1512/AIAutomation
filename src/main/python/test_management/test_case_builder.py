"""
Test Case Builder - Converts multi-prompt sessions into executable test cases

Integrates with:
- test_session_manager: Get prompt sequences
- smart_prompt_handler: Process natural language
- browser_executor: For element discovery and execution

Features:
- Build complete test cases from sessions
- Generate code in multiple languages (Python, Java, JS, Cypress)
- Save test cases with metadata
- Load and manage test case library
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from nlp.smart_prompt_handler import SmartPromptHandler
from browser.browser_executor import BrowserExecutor
from core.inference_improved import ImprovedSeleniumGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCase:
    """Represents a complete, executable test case."""
    
    def __init__(self, test_case_id: str, name: str, description: str = "", url: str = ""):
        self.test_case_id = test_case_id
        self.name = name
        self.description = description
        self.url = url or ""  # Base URL for the test
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.tags = []
        self.priority = "medium"  # low, medium, high, critical
        self.status = "active"  # active, disabled, deprecated
        
        # Test steps from session prompts
        self.steps = []
        
        # Prompts field for semantic tests (actions converted to prompts with generated_code)
        self.prompts = []
        
        # Parent test case ID for semantic variants
        self.parent_test_case_id = None
        
        # Generated code for different languages
        self.generated_code = {
            'python': '',
            'java': '',
            'javascript': '',
            'cypress': ''
        }
        
        # Execution history
        self.execution_history = []
        
    def to_dict(self) -> Dict:
        """Convert test case to dictionary."""
        data = {
            'test_case_id': self.test_case_id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'priority': self.priority,
            'status': self.status,
            'steps': self.steps,
            'prompts': self.prompts,  # Include prompts for semantic tests
            'generated_code': self.generated_code,
            'execution_history': self.execution_history
        }
        # Include parent_test_case_id if it exists (for semantic variants)
        if self.parent_test_case_id:
            data['parent_test_case_id'] = self.parent_test_case_id
        return data
    
    @staticmethod
    def from_dict(data: Dict) -> 'TestCase':
        """Create TestCase from dictionary."""
        tc = TestCase(
            test_case_id=data['test_case_id'],
            name=data['name'],
            description=data.get('description', ''),
            url=data.get('url', '')
        )
        tc.created_at = data.get('created_at', tc.created_at)
        tc.updated_at = data.get('updated_at', tc.updated_at)
        tc.tags = data.get('tags', [])
        tc.priority = data.get('priority', 'medium')
        tc.status = data.get('status', 'active')
        tc.prompts = data.get('prompts', [])  # Load prompts for semantic tests
        tc.steps = data.get('steps', [])
        tc.generated_code = data.get('generated_code', tc.generated_code)
        tc.execution_history = data.get('execution_history', [])
        tc.parent_test_case_id = data.get('parent_test_case_id')  # Preserve parent ID for semantic variants
        return tc


class TestCaseBuilder:
    """
    Builds executable test cases from test sessions.
    
    Workflow:
    1. Takes TestSession with multiple prompts
    2. Uses SmartPromptHandler to process each prompt
    3. Generates complete test code in multiple languages
    4. Saves as TestCase with metadata
    """
    
    def __init__(self, test_cases_dir: str = None):
        """Initialize test case builder."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        self.project_root = Path(project_root)
        
        if test_cases_dir is None:
            # Use new unified structure: test_suites/general/builder/
            test_cases_dir = os.path.join(project_root, 'test_suites', 'general', 'builder')
        
        self.test_cases_dir = test_cases_dir
        os.makedirs(self.test_cases_dir, exist_ok=True)
        
        # Create exports subdirectory under test_suites/general/exports/
        suite_root = os.path.join(project_root, 'test_suites', 'general')
        self.exports_dir = os.path.join(suite_root, 'exports')
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Cache loaded test cases (test_case_id -> TestCase)
        self.test_cases: Dict[str, TestCase] = {}
        
        # Initialize inference engine for multi-language code generation
        self.inference_engine = ImprovedSeleniumGenerator(silent=True)
        
        logger.info(f"[TEST BUILDER] Initialized with directory: {self.test_cases_dir}")
    
    def build_from_session(self, session_data: Dict, 
                          test_case_id: str = None,
                          tags: List[str] = None,
                          priority: str = "medium",
                          languages: List[str] = None,
                          compact_mode: bool = True,
                          execution_ready: bool = False) -> TestCase:
        """
        Build test case from session data.
        
        Args:
            session_data: Dictionary from TestSession.to_dict()
            test_case_id: Optional custom test case ID (default: TC + timestamp)
            tags: Optional tags for categorization
            priority: Test priority (low, medium, high, critical)
            languages: Optional list of languages to generate (default: all)
            compact_mode: If True, generates compact code (70% smaller, default: True)
            execution_ready: If True, generates code without pytest fixtures for direct exec() (semantic tests)
            
        Returns:
            TestCase object
        """
        if test_case_id is None:
            # Generate ID: TC001, TC002, etc.
            existing_ids = [tc.test_case_id for tc in self.test_cases.values() 
                           if tc.test_case_id.startswith('TC')]
            if existing_ids:
                numbers = [int(re.findall(r'\d+', tid)[0]) for tid in existing_ids if re.findall(r'\d+', tid)]
                next_num = max(numbers) + 1 if numbers else 1
            else:
                next_num = 1
            test_case_id = f"TC{next_num:03d}"
        
        # Create test case
        test_case = TestCase(
            test_case_id=test_case_id,
            name=session_data['name'],
            description=session_data.get('description', ''),
            url=session_data.get('url', '')
        )
        
        test_case.tags = tags or []
        test_case.priority = priority
        test_case.steps = session_data['prompts']
        
        # Log step order for debugging
        step_order = [f"{s['step']}: {s['prompt'][:30]}..." for s in test_case.steps]
        logger.info(f"[TEST BUILDER] Building test with steps in order: {step_order}")
        
        # If no languages specified, generate all
        if languages is None:
            languages = ['python', 'java', 'javascript', 'cypress']
        
        # Generate code only for requested languages
        if 'python' in languages:
            try:
                if execution_ready:
                    # Generate execution-ready code (no pytest) for semantic tests
                    test_case.generated_code['python'] = self._generate_python_code_execution_ready(test_case)
                else:
                    # Generate pytest-style code for exported tests
                    test_case.generated_code['python'] = self._generate_python_code(test_case, compact_mode=compact_mode)
            except Exception as e:
                logger.error(f"[TEST BUILDER] Error generating Python code: {e}")
                test_case.generated_code['python'] = f"# Error generating Python code: {str(e)}"
        
        if 'java' in languages:
            try:
                test_case.generated_code['java'] = self._generate_java_code(test_case)
            except Exception as e:
                logger.error(f"[TEST BUILDER] Error generating Java code: {e}")
                test_case.generated_code['java'] = f"// Error generating Java code: {str(e)}"
        
        if 'javascript' in languages:
            try:
                test_case.generated_code['javascript'] = self._generate_javascript_code(test_case)
            except Exception as e:
                logger.error(f"[TEST BUILDER] Error generating JavaScript code: {e}")
                test_case.generated_code['javascript'] = f"// Error generating JavaScript code: {str(e)}"
        
        if 'cypress' in languages:
            try:
                test_case.generated_code['cypress'] = self._generate_cypress_code(test_case)
            except Exception as e:
                logger.error(f"[TEST BUILDER] Error generating Cypress code: {e}")
                test_case.generated_code['cypress'] = f"// Error generating Cypress code: {str(e)}"
        
        # Add to cache
        self.test_cases[test_case_id] = test_case
        
        logger.info(f"[TEST BUILDER] Built test case: {test_case_id} - {test_case.name}")
        return test_case
    
    def _generate_python_code_compact(self, test_case: TestCase) -> str:
        """Generate COMPACT Python/pytest test file (70% smaller)."""
        safe_name = self._safe_name(test_case.name)
        lines = []
        
        # Minimal header
        lines.append(f'"""')
        lines.append(f'Test Case: {test_case.name}')
        lines.append(f'Test ID: {test_case.test_case_id}')
        lines.append(f'Priority: {test_case.priority}')
        lines.append(f'Generated: {datetime.now().isoformat()}')
        lines.append(f'"""')
        lines.append('')
        
        # Minimal imports
        lines.append('import pytest')
        lines.append('import time')  # Required for time.sleep() in generated code
        lines.append('from selenium import webdriver')
        lines.append('from selenium.webdriver.common.by import By')
        lines.append('from selenium.webdriver.support.ui import WebDriverWait')
        lines.append('from selenium.webdriver.support import expected_conditions as EC')
        lines.append('')
        
        # Compact fixture
        lines.append('@pytest.fixture')
        lines.append('def driver(request):')  
        lines.append('    browser = request.config.getoption("--browser", default="chrome")')
        lines.append('    if browser.lower() == "firefox":')
        lines.append('        driver = webdriver.Firefox()')
        lines.append('    elif browser.lower() == "edge":')
        lines.append('        driver = webdriver.Edge()')
        lines.append('    else:')
        lines.append('        driver = webdriver.Chrome()')
        lines.append('    driver.maximize_window()')
        lines.append('    yield driver')
        lines.append('    driver.quit()')
        lines.append('')
        
        # Test function with tags
        lines.append(f'@pytest.mark.{test_case.priority}')
        for tag in test_case.tags[:2]:  # Limit tags to avoid bloat
            safe_tag = re.sub(r'[^a-zA-Z0-9_]', '_', tag.lower())
            lines.append(f'@pytest.mark.{safe_tag}')
        lines.append(f'def test_{safe_name}(driver):')
        lines.append(f'    """{test_case.description or test_case.name}"""')
        
        # Navigate to first URL if exists
        first_url = test_case.steps[0].get('url') if test_case.steps else None
        if first_url:
            lines.append(f'    driver.get("{first_url}")')
        
        # Add each step's compact code
        for step in test_case.steps:
            step_code = step.get('generated_code', '').strip()
            step_value = step.get('value')
            
            if step_code:
                # Replace {VALUE} placeholders with actual data values from UI
                if step_value:
                    placeholders = ['{VALUE}', '{TEXT}', '{SEARCH_TEXT}', '{OPTION}', '{DATA}']
                    for placeholder in placeholders:
                        # Replace quoted: "{VALUE}" -> "actual_value"
                        quoted = f'"{placeholder}"'
                        if quoted in step_code:
                            step_code = step_code.replace(quoted, f'"{step_value}"')
                        # Replace unquoted: {VALUE} -> "actual_value"
                        elif placeholder in step_code:
                            step_code = step_code.replace(placeholder, f'"{step_value}"')
                
                # Add code with proper indentation (split on actual newline, not backslash-n)
                for line in step_code.split('\n'):
                    if line.strip():
                        lines.append(f'    {line}')
            else:
                # Fallback placeholder
                lines.append(f'    # {step.get("prompt", "Step")}')
                lines.append('    pass')
        
        return '\n'.join(lines)
    
    def _generate_python_code_execution_ready(self, test_case: TestCase) -> str:
        """
        Generate EXECUTION-READY Python code (no pytest fixtures).
        This code can be directly executed with exec() for semantic tests.
        The driver object will be provided by the exec_context.
        """
        lines = []
        
        # Add comment header (not docstring - those cause issues)
        lines.append(f'# Execution-ready code (no pytest fixtures)')
        lines.append(f'# Test: {test_case.name}')
        lines.append(f'# Test ID: {test_case.test_case_id}')
        if test_case.url:
            lines.append(f'# URL: {test_case.url}')
        lines.append('')
        
        # Navigate to first URL if exists (driver is provided by exec_context)
        # For semantic tests, check prompts field first, then steps
        execution_steps = test_case.prompts if test_case.prompts else test_case.steps
        
        # Try to get URL from first step, then fall back to test case URL
        first_url = None
        if execution_steps and isinstance(execution_steps[0], dict):
            first_url = execution_steps[0].get('url')
            logger.info(f"[URL-CHECK] Checked first step/prompt URL: {first_url}")
        # If no URL in first step, use test case URL (important for semantic variants)
        if not first_url:
            first_url = test_case.url
            logger.info(f"[URL-CHECK] Using test_case.url: {first_url}")
        
        # If still no URL and this is a semantic variant, look up parent test's URL
        if not first_url and hasattr(test_case, 'parent_test_case_id') and test_case.parent_test_case_id:
            logger.info(f"[URL-FALLBACK] No URL found, looking up parent test: {test_case.parent_test_case_id}")
            try:
                parent_test = self.load_test_case(test_case.parent_test_case_id)
                if parent_test:
                    # Try parent's first step URL
                    if parent_test.steps and isinstance(parent_test.steps[0], dict):
                        first_url = parent_test.steps[0].get('url')
                        logger.info(f"[URL-FALLBACK] Found URL in parent's first step: {first_url}")
                    # Fall back to parent's test case URL
                    if not first_url:
                        first_url = parent_test.url
                        logger.info(f"[URL-FALLBACK] Using parent's test_case.url: {first_url}")
                    if first_url:
                        logger.info(f"[URL-FALLBACK] ✓ Retrieved URL from parent test {test_case.parent_test_case_id}: {first_url}")
                else:
                    logger.warning(f"[URL-FALLBACK] Could not load parent test {test_case.parent_test_case_id} - returned None")
            except Exception as e:
                logger.warning(f"[URL-FALLBACK] Error loading parent test {test_case.parent_test_case_id}: {e}")
        else:
            if not first_url:
                logger.warning(f"[URL-CHECK] No URL found and no parent_test_case_id to fall back to")
            
            
        if first_url:
            lines.append(f'driver.get("{first_url}")')
            lines.append('time.sleep(2)  # Wait for page load')
            lines.append('')
        
        # Add each step's code
        # Use prompts field for semantic tests, steps for normal tests
        for step in execution_steps:
            # Skip string steps (documentation for semantic tests)
            if isinstance(step, str):
                logger.info(f"[EXEC-READY] Skipping documentation string: {step[:50]}")
                continue
                
            step_code = step.get('generated_code', '').strip()
            step_value = step.get('value')
            step_prompt = step.get('prompt', '')
            
            logger.info(f"[EXEC-READY] Processing step: prompt='{step_prompt}', has_code={bool(step_code)}, value='{step_value}'")
            
            # If no generated_code, try to generate it from prompt (for semantic variants)
            if not step_code and step_prompt:
                logger.info(f"[EXEC-READY] No code found, generating from prompt: '{step_prompt}'")
                try:
                    from ml_models.inference_engine import InferenceEngine
                    engine = InferenceEngine()
                    generated = engine.generate_code(step_prompt, test_case.url or '')
                    step_code = generated.get('code', '').strip() if generated else ''
                    logger.info(f"[EXEC-READY] Generated code length: {len(step_code)} chars")
                except Exception as e:
                    logger.error(f"[EXEC-READY] Could not generate code from prompt: {e}")
            else:
                logger.info(f"[EXEC-READY] Using existing code (length: {len(step_code)} chars)")
            
            if step_code:
                logger.info(f"[EXEC-READY] Step has code, processing placeholders...")
                # Replace {VALUE} placeholders with actual data values
                if step_value:
                    placeholders = ['{VALUE}', '{TEXT}', '{SEARCH_TEXT}', '{OPTION}', '{DATA}']
                    for placeholder in placeholders:
                        if f'"{placeholder}"' in step_code or f"'{placeholder}'" in step_code:
                            step_code = step_code.replace(f'"{placeholder}"', f'"{step_value}"')
                            step_code = step_code.replace(f"'{placeholder}'", f"'{step_value}'")
                        elif placeholder in step_code:
                            step_code = step_code.replace(placeholder, f'"{step_value}"')
                
                # CRITICAL: Verify no syntax errors after replacement (check for double parentheses)
                if '))'  in step_code:
                    # Check if it's a valid nested structure or an error
                    import re
                    # Pattern: send_keys("something"))
                    if re.search(r'\.(send_keys|click|clear|submit)\([^)]+\)\)(?!\s*[;\n])', step_code):
                        logger.error(f"[EXEC-READY] ⚠️ Found potential syntax error: double closing parenthesis")
                        # Remove extra trailing parenthesis after method calls
                        step_code = re.sub(r'\.(send_keys|click|clear|submit)\(([^)]+)\)\)', r'.\1(\2)', step_code)
                        logger.info(f"[EXEC-READY] ✓ Fixed double parenthesis in step code")
                
                # ✅ CRITICAL FIX: Strip headers and URL navigation from step code
                # These were copied from parent test but should only appear once at test level
                cleaned_lines = []
                for line in step_code.split('\n'):
                    stripped = line.strip()
                    # Skip header comments and URL navigation
                    if (stripped.startswith('# Execution-ready code') or
                        stripped.startswith('# Test:') or
                        stripped.startswith('# Test ID:') or
                        stripped.startswith('# URL:') or
                        stripped.startswith('driver.get(') or
                        stripped == 'time.sleep(2)  # Wait for page load' or
                        (not stripped and not cleaned_lines)):  # Skip leading blank lines
                        continue
                    cleaned_lines.append(line)
                
                step_code = '\n'.join(cleaned_lines)
                logger.info(f"[EXEC-READY] Cleaned step code from {len(step_code.split(chr(10)))} to {len(cleaned_lines)} lines")
                
                # Add code without test function indentation (direct execution)
                for line in step_code.split('\n'):
                    if line.strip():
                        lines.append(line)
                lines.append('')  # Blank line between steps
            else:
                # Fallback comment if still no code
                logger.warning(f"[EXEC-READY] No code available for step '{step_prompt}', using pass")
                lines.append(f'# {step_prompt or "Step"}')
                lines.append('pass')
                lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_python_code(self, test_case: TestCase, compact_mode: bool = False) -> str:
        """Generate complete executable Python/pytest test file.
        
        Args:
            test_case: TestCase object with steps
            compact_mode: If True, generates minimal boilerplate (70% smaller code)
        """
        if compact_mode:
            logger.info(f"[TEST BUILDER] Generating COMPACT Python code for {test_case.test_case_id}")
            return self._generate_python_code_compact(test_case)
        
        # Standard verbose template
        lines = []
        
        # Header with metadata
        lines.append(f'"""')
        lines.append(f'Test Case: {test_case.name}')
        lines.append(f'Test ID: {test_case.test_case_id}')
        lines.append(f'Description: {test_case.description}')
        lines.append(f'Priority: {test_case.priority}')
        lines.append(f'Tags: {", ".join(test_case.tags)}')
        lines.append(f'Generated: {datetime.now().isoformat()}')
        lines.append(f'')
        lines.append(f'This is a complete executable test file.')
        lines.append(f'Run with: pytest {self._safe_filename(test_case.test_case_id)}.py')
        lines.append(f'"""')
        lines.append('')
        
        # Imports
        lines.append('import pytest')
        lines.append('import os')
        lines.append('import sys')
        lines.append('import time')
        lines.append('from selenium import webdriver')
        lines.append('from selenium.webdriver.common.by import By')
        lines.append('from selenium.webdriver.support.ui import WebDriverWait')
        lines.append('from selenium.webdriver.support import expected_conditions as EC')
        lines.append('from selenium.webdriver.support.ui import Select')
        lines.append('from selenium.common.exceptions import TimeoutException, NoSuchElementException')
        lines.append('')
        lines.append('# Add self-healing locator support')
        lines.append("script_dir = os.path.dirname(os.path.abspath(__file__))")
        lines.append('if script_dir not in sys.path:')
        lines.append('    sys.path.insert(0, script_dir)')
        lines.append('try:')
        lines.append('    from self_healing_locator import SelfHealingLocator')
        lines.append('except ImportError:')
        lines.append('    # Fallback if self-healing not available')
        lines.append('    SelfHealingLocator = None')
        lines.append('')
        
        # Test fixture for driver setup/teardown
        lines.append('@pytest.fixture')
        lines.append('def driver(request):')
        lines.append('    """Setup and teardown for WebDriver (supports chrome/firefox/edge)."""')
        lines.append('    browser = request.config.getoption("--browser", default="chrome")')
        lines.append('    if browser.lower() == "firefox":')
        lines.append('        driver = webdriver.Firefox()')
        lines.append('    elif browser.lower() == "edge":')
        lines.append('        driver = webdriver.Edge()')
        lines.append('    else:')
        lines.append('        driver = webdriver.Chrome()')
        lines.append('    driver.maximize_window()')
        lines.append('    driver.implicitly_wait(15)  # Implicit wait for elements - increased for slow-loading pages')
        lines.append('')
        lines.append('    # Initialize self-healing locator if available')
        lines.append('    driver.healer = SelfHealingLocator() if SelfHealingLocator else None')
        lines.append('')
        lines.append('    # Close sticky popup - simple direct approach')
        lines.append('    try:')
        lines.append("        close_btn = driver.find_element(By.ID, 'sticky-close')")
        lines.append("        driver.execute_script('arguments[0].click();', close_btn)")
        lines.append('        time.sleep(1)')
        lines.append('    except:')
        lines.append('        pass')
        lines.append('')
        lines.append('    yield driver')
        lines.append('    driver.quit()')
        lines.append('')
        
        # Test function
        safe_name = self._safe_name(test_case.name)
        lines.append(f'@pytest.mark.{test_case.priority}')
        for tag in test_case.tags:
            safe_tag = re.sub(r'[^a-zA-Z0-9_]', '_', tag.lower())
            lines.append(f'@pytest.mark.{safe_tag}')
        lines.append(f'def test_{safe_name}(driver):')
        lines.append(f'    """')
        lines.append(f'    {test_case.description or "No description provided"}')
        lines.append(f'    """')
        lines.append('    wait = WebDriverWait(driver, 20)')
        lines.append('')
        lines.append('    # Helper method to find elements with self-healing and better waits')
        lines.append('    def find_element_safe(locator_str):')
        lines.append('        if driver.healer:')
        lines.append('            element = driver.healer.find_element(driver, locator_str)')
        lines.append('            if element:')
        lines.append('                return element')
        lines.append('        # Fallback to traditional method if healer fails or not available')
        lines.append("        by_parts = locator_str.replace('By.', '').split('(')")
        lines.append('        if len(by_parts) == 2:')
        lines.append('            by_type = by_parts[0].strip()')
        lines.append("            value = by_parts[1].strip(')\"\\'')")  
        lines.append("            by_map = {'ID': By.ID, 'NAME': By.NAME, 'XPATH': By.XPATH, 'CSS_SELECTOR': By.CSS_SELECTOR,")
        lines.append("                      'CLASS_NAME': By.CLASS_NAME, 'TAG_NAME': By.TAG_NAME, 'LINK_TEXT': By.LINK_TEXT}")
        lines.append('            locator = (by_map.get(by_type, By.XPATH), value)')
        lines.append('            # First wait for presence, then wait for visibility')
        lines.append('            element = wait.until(EC.presence_of_element_located(locator))')
        lines.append('            wait.until(EC.visibility_of(element))')
        lines.append('            return element')
        lines.append('        raise Exception(f"Could not find element: {locator_str}")')
        lines.append('    ')
        
        # Navigate to first URL if exists
        first_url = test_case.steps[0].get('url') if test_case.steps else None
        if first_url:
            lines.append(f'    # Navigate to application')
            lines.append(f'    driver.get("{first_url}")')
            lines.append('    time.sleep(2)')
            lines.append('    ')
        
        # Add each step with proper indentation
        current_url = first_url
        first_action_done = False
        for step in test_case.steps:
            step_num = step.get('step', 0)
            prompt = step.get('prompt', '')
            step_url = step.get('url')
            step_value = step.get('value')
            
            # Close popup before first action to avoid interference
            if not first_action_done:
                lines.append('    # Close any sticky popups that might interfere with actions')
                lines.append('    try:')
                lines.append("        close_btn = driver.find_element(By.ID, 'sticky-close')")
                lines.append("        driver.execute_script('arguments[0].click();', close_btn)")
                lines.append('        time.sleep(0.5)')
                lines.append('    except:')
                lines.append('        pass  # Popup might not exist')
                lines.append('    ')
                first_action_done = True
            
            lines.append(f'    # Step {step_num}: {prompt}')
            
            # Navigate if URL changed
            if step_url and step_url != current_url:
                lines.append(f'    driver.get("{step_url}")')
                lines.append('    time.sleep(2)')
                current_url = step_url
            
            # Use already-generated code from step (should be Python now)
            step_code = step.get('generated_code', '')
            
            # DEBUG: Log what code we have for this step
            print(f"[TEST BUILDER] Step {step_num} generated_code: {step_code[:100] if step_code else 'EMPTY'}...", flush=True)
            
            # Check if we have valid generated code (not just a TODO placeholder)
            is_placeholder = (not step_code or 
                            not step_code.strip() or 
                            step_code.strip().startswith('# TODO:') or
                            step_code.strip() == 'pass')
            
            if step_code and not is_placeholder:
                # Legacy support: Convert to Python syntax if it's Java (old test cases)
                if 'WebDriverWait wait = new WebDriverWait' in step_code or 'WebElement element' in step_code:
                    logger.warning(f"[TEST BUILDER] Step {step_num}: Converting Java to Python (legacy support)")
                    step_code = self._convert_java_to_python_code(step_code)
                
                # Replace any remaining placeholders with actual value
                if step_value:
                    # Need to handle both quoted and unquoted placeholders
                    placeholders = ['{VALUE}', '{TEXT}', '{SEARCH_TEXT}', '{OPTION}', '{DATA}']
                    for placeholder in placeholders:
                        # Replace quoted placeholder: "{VALUE}" -> "actual_value"
                        quoted_placeholder = f'"{placeholder}"'
                        if quoted_placeholder in step_code:
                            step_code = step_code.replace(quoted_placeholder, f'"{step_value}"')
                        # Replace unquoted placeholder: {VALUE} -> "actual_value"  
                        elif placeholder in step_code:
                            step_code = step_code.replace(placeholder, f'"{step_value}"')
                else:
                    # No value provided - ensure placeholders remain as clear TODO markers
                    # Replace any bare "value" variable (error) with "{VALUE}" placeholder
                    # Match .send_keys(value) or similar patterns where value is undefined variable
                    step_code = re.sub(r'\.send_keys\(value\)', r'.send_keys("{VALUE}")', step_code)
                    step_code = re.sub(r'\.send_keys\s*\(\s*value\s*\)', r'.send_keys("{VALUE}")', step_code)
                    # Also handle sendKeys (Java style)
                    step_code = re.sub(r'\.sendKeys\("value"\)', r'.sendKeys("{VALUE}")', step_code)
                    step_code = re.sub(r'\.sendKeys\(value\)', r'.sendKeys("{VALUE}")', step_code)
                
                # Add indented code lines
                for line in step_code.strip().split('\n'):
                    if line.strip():
                        lines.append(f'    {line}')
            else:
                # No generated code - add placeholder
                lines.append(f'    # TODO: Implement step - {prompt}')
                lines.append('    pass')
            
            lines.append('    ')
        
        # Add assertion example
        lines.append('    # Add assertions as needed')
        lines.append('    # assert "expected text" in driver.page_source')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _convert_java_to_python_code(self, java_code: str) -> str:
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
        
        return python_code
    
    def _safe_name(self, name: str) -> str:
        """Convert name to safe identifier."""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    
    def _safe_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        return re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    
    def _generate_java_code(self, test_case: TestCase) -> str:
        """Generate complete executable Java/JUnit test class."""
        lines = []
        
        # Package and imports
        lines.append('package com.test.automation;')
        lines.append('')
        lines.append('/**')
        lines.append(f' * Test Case: {test_case.name}')
        lines.append(f' * Test ID: {test_case.test_case_id}')
        lines.append(f' * Description: {test_case.description}')
        lines.append(f' * Priority: {test_case.priority}')
        lines.append(f' * Generated: {datetime.now().isoformat()}')
        lines.append(' */')
        lines.append('import org.junit.jupiter.api.*;')
        lines.append('import org.junit.jupiter.api.extension.ExtendWith;')
        lines.append('import org.openqa.selenium.*;')
        lines.append('import org.openqa.selenium.chrome.ChromeDriver;')
        lines.append('import org.openqa.selenium.firefox.FirefoxDriver;')
        lines.append('import org.openqa.selenium.edge.EdgeDriver;')
        lines.append('import org.openqa.selenium.chrome.ChromeOptions;')
        lines.append('import org.openqa.selenium.support.ui.*;')
        lines.append('import org.openqa.selenium.support.ui.WebDriverWait;')
        lines.append('import java.time.Duration;')
        lines.append('import static org.junit.jupiter.api.Assertions.*;')
        lines.append('')
        
        # Class with tags
        safe_name = ''.join(word.capitalize() for word in re.findall(r'\w+', test_case.name))
        if test_case.tags:
            for tag in test_case.tags:
                lines.append(f'@Tag("{tag}")')
        lines.append(f'@DisplayName("{test_case.name}")')
        lines.append(f'public class {safe_name}Test {{')
        lines.append('    private WebDriver driver;')
        lines.append('    private WebDriverWait wait;')
        lines.append('')
        
        # Setup
        lines.append('    @BeforeEach')
        lines.append('    public void setUp() {')
        lines.append('        // Browser-agnostic setup - supports chrome, firefox, edge')
        lines.append('        String browser = System.getProperty("browser", "chrome");')
        lines.append('        ChromeOptions options = new ChromeOptions();')
        lines.append('        options.addArguments("--start-maximized");')
        lines.append('        options.addArguments("--disable-notifications");')
        lines.append('        if (browser.equalsIgnoreCase("firefox")) {')
        lines.append('            driver = new FirefoxDriver();')
        lines.append('        } else if (browser.equalsIgnoreCase("edge")) {')
        lines.append('            driver = new EdgeDriver();')
        lines.append('        } else {')
        lines.append('            driver = new ChromeDriver(options);')
        lines.append('        }')
        lines.append('        wait = new WebDriverWait(driver, Duration.ofSeconds(10));')
        lines.append('        ')
        lines.append('        // Close sticky popup - simple direct approach')
        lines.append('        try {')
        lines.append('            WebElement closeBtn = driver.findElement(By.id("sticky-close"));')
        lines.append('            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", closeBtn);')
        lines.append('            Thread.sleep(1000);')
        lines.append('        } catch (Exception e) {')
        lines.append('            // Popup might not exist')
        lines.append('        }')
        lines.append('    }')
        lines.append('')
        
        # Teardown
        lines.append('    @AfterEach')
        lines.append('    public void tearDown() {')
        lines.append('        if (driver != null) {')
        lines.append('            driver.quit();')
        lines.append('        }')
        lines.append('    }')
        lines.append('')
        
        # Test method
        lines.append('    @Test')
        lines.append(f'    @DisplayName("{test_case.description or test_case.name}")')
        lines.append(f'    public void test{safe_name}() throws InterruptedException {{')
        
        # Navigate to first URL
        first_url = test_case.steps[0].get('url') if test_case.steps else None
        if first_url:
            lines.append(f'        // Navigate to application')
            lines.append(f'        driver.get("{first_url}");')
            lines.append('        Thread.sleep(2000);')
            lines.append('')
        
        # Add each step with generated code
        current_url = first_url
        first_action_done = False
        for step in test_case.steps:
            step_num = step.get('step', 0)
            prompt = step.get('prompt', '')
            step_url = step.get('url')
            
            # Close popup before first action to avoid interference
            if not first_action_done:
                lines.append('        // Close any sticky popups that might interfere with actions')
                lines.append('        try {')
                lines.append('            WebElement closeBtn = driver.findElement(By.id("sticky-close"));')
                lines.append('            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", closeBtn);')
                lines.append('            Thread.sleep(500);')
                lines.append('        } catch (Exception e) {')
                lines.append('            // Popup might not exist')
                lines.append('        }')
                lines.append('')
                first_action_done = True
            
            lines.append(f'        // Step {step_num}: {prompt}')
            
            # Navigate if URL changed
            if step_url and step_url != current_url:
                lines.append(f'        driver.get("{step_url}");')
                lines.append('        Thread.sleep(2000);')
                current_url = step_url
            
            # Regenerate Java code from prompt using inference engine
            if prompt:
                try:
                    result = self.inference_engine.infer(prompt, language='java')
                    java_code = result.get('code', '').strip()
                    
                    if java_code:
                        code_lines = java_code.split('\n')
                        for line in code_lines:
                            if line.strip() and not line.strip().startswith('//'):
                                # Remove duplicate driver declarations
                                if 'WebDriver driver' not in line and 'new ChromeDriver' not in line:
                                    lines.append(f'        {line}')
                    else:
                        lines.append(f'        // TODO: Implement step - {prompt}')
                except Exception as e:
                    logger.warning(f"[TEST BUILDER] Failed to generate Java code for: {prompt} - {e}")
                    lines.append(f'        // TODO: Implement step - {prompt}')
            
            lines.append('')
        
        # Add assertion example
        lines.append('        // Add assertions as needed')
        lines.append('        // assertTrue(driver.getPageSource().contains("expected text"));')
        lines.append('    }')
        lines.append('}')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_javascript_code(self, test_case: TestCase) -> str:
        """Generate JavaScript/Playwright test code."""
        lines = []
        
        # Imports
        lines.append("const { test, expect } = require('@playwright/test');")
        lines.append('')
        
        # Test
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', test_case.name)
        lines.append(f"test('{test_case.name}', async ({{ page }}) => {{")
        
        # Navigate to first URL and close popup
        first_url = test_case.steps[0].get('url') if test_case.steps else None
        if first_url:
            lines.append(f"    // Navigate to application")
            lines.append(f"    await page.goto('{first_url}');")
            lines.append('    await page.waitForTimeout(2000);')
            lines.append('')
            lines.append('    // Close sticky popup - simple direct approach')
            lines.append('    try {')
            lines.append('        const closeBtn = await page.locator(\"#sticky-close\");')
            lines.append('        if (await closeBtn.isVisible()) {')
            lines.append('            await closeBtn.evaluate(el => el.click());')
            lines.append('            await page.waitForTimeout(1000);')
            lines.append('        }')
            lines.append('    } catch (e) {')
            lines.append('        // Popup might not exist')
            lines.append('    }')
            lines.append('')
        
        # Add each step with regenerated code
        first_action_done = False
        for step in test_case.steps:
            prompt = step.get('prompt', '')
            step_url = step.get('url')
            
            # Close popup before first action to avoid interference
            if not first_action_done:
                lines.append('    // Close any sticky popups that might interfere with actions')
                lines.append('    try {')
                lines.append('        const closeBtn = await page.locator(\"#sticky-close\");')
                lines.append('        if (await closeBtn.isVisible()) {')
                lines.append('            await closeBtn.evaluate(el => el.click());')
                lines.append('            await page.waitForTimeout(500);')
                lines.append('        }')
                lines.append('    } catch (e) {')
                lines.append('        // Popup might not exist')
                lines.append('    }')
                lines.append('')
                first_action_done = True
            
            lines.append(f"    // Step {step['step']}: {prompt}")
            
            # Navigate if URL changed
            if step_url and step_url != first_url:
                lines.append(f"    await page.goto('{step_url}');")
                lines.append('    await page.waitForTimeout(2000);')
            
            # Regenerate JavaScript code from prompt (note: inference engine generates Selenium, will need conversion)
            # For now, regenerate and adapt basic patterns
            if prompt:
                try:
                    result = self.inference_engine.infer(prompt, language='java')
                    code = result.get('code', '').strip()
                    
                    if code:
                        # Simple Java→JavaScript conversion for Playwright
                        js_code = code
                        js_code = js_code.replace('driver.findElement(By.', 'await page.locator(')
                        js_code = js_code.replace('.click();', ').click();')
                        js_code = js_code.replace('.sendKeys(', ').fill(')
                        js_code = js_code.replace('By.xpath("', 'xpath=')
                        js_code = js_code.replace('By.id("', '#')
                        js_code = js_code.replace('By.name("', '[name="')
                        js_code = js_code.replace('By.cssSelector("', '')
                        js_code = js_code.replace('")', '')
                        
                        lines.append(f"    {js_code}")
                    else:
                        lines.append(f"    // TODO: Implement step - {prompt}")
                except Exception as e:
                    logger.warning(f"[TEST BUILDER] Failed to generate JavaScript code for: {prompt} - {e}")
                    lines.append(f"    // TODO: Implement step - {prompt}")
            
            lines.append('')
        
        lines.append('});')
        lines.append('')
        
        return '\n'.join(lines)
    
    def _generate_cypress_code(self, test_case: TestCase) -> str:
        """Generate Cypress test code."""
        lines = []
        
        # Test
        lines.append(f"describe('{test_case.name}', () => {{")
        
        safe_name = re.sub(r'[^a-zA-Z0-9_]', ' ', test_case.name)
        lines.append(f"    it('{safe_name}', () => {{")
        
        # Navigate to first URL and close popup
        first_url = test_case.steps[0].get('url') if test_case.steps else None
        if first_url:
            lines.append(f"        // Navigate to application")
            lines.append(f"        cy.visit('{first_url}');")
            lines.append('        cy.wait(2000);')
            lines.append('')
            lines.append('        // Close sticky popup - simple direct approach')
            lines.append('        cy.get(\"#sticky-close\").then(($btn) => {')
            lines.append('            if ($btn.is(\":visible\")) {')
            lines.append('                cy.wrap($btn).click({ force: true });')
            lines.append('                cy.wait(1000);')
            lines.append('            }')
            lines.append('        }).catch(() => {')
            lines.append('            // Popup might not exist')
            lines.append('        });')
            lines.append('')
        
        # Add each step with regenerated code
        first_action_done = False
        for step in test_case.steps:
            prompt = step.get('prompt', '')
            step_url = step.get('url')
            
            # Close popup before first action to avoid interference
            if not first_action_done:
                lines.append('        // Close any sticky popups that might interfere with actions')
                lines.append('        cy.get(\"#sticky-close\").then(($btn) => {')
                lines.append('            if ($btn.is(\":visible\")) {')
                lines.append('                cy.wrap($btn).click({ force: true });')
                lines.append('                cy.wait(500);')
                lines.append('            }')
                lines.append('        }).catch(() => {')
                lines.append('            // Popup might not exist')
                lines.append('        });')
                lines.append('')
                first_action_done = True
            
            lines.append(f"        // Step {step['step']}: {prompt}")
            
            # Navigate if URL changed
            if step_url and step_url != first_url:
                lines.append(f"        cy.visit('{step_url}');")
                lines.append('        cy.wait(2000);')
            
            # Regenerate Cypress code from prompt
            if prompt:
                try:
                    result = self.inference_engine.infer(prompt, language='java')
                    code = result.get('code', '').strip()
                    
                    if code:
                        # Simple Java→Cypress conversion
                        cy_code = code
                        cy_code = cy_code.replace('driver.findElement(By.xpath("', 'cy.xpath(\'')
                        cy_code = cy_code.replace('driver.findElement(By.id("', 'cy.get(\'#')
                        cy_code = cy_code.replace('driver.findElement(By.name("', 'cy.get(\'[name="')
                        cy_code = cy_code.replace('driver.findElement(By.cssSelector("', 'cy.get(\'')
                        cy_code = cy_code.replace('")', '\').click()')
                        cy_code = cy_code.replace('.click();', '.click();')
                        cy_code = cy_code.replace('.sendKeys("', '.type(\'')
                        cy_code = cy_code.replace('");', '\');')
                        
                        lines.append(f"        {cy_code}")
                    else:
                        lines.append(f"        // TODO: Implement step - {prompt}")
                except Exception as e:
                    logger.warning(f"[TEST BUILDER] Failed to generate Cypress code for: {prompt} - {e}")
                    lines.append(f"        // TODO: Implement step - {prompt}")
            
            lines.append('')
        
        lines.append('    });')
        lines.append('});')
        lines.append('')
        
        return '\n'.join(lines)
    
    def save_test_case(self, test_case: TestCase, test_type: str = "general", filename: str = None) -> str:
        """
        Save test case to test_suites/ directory (single source of truth).
        
        NEW: Organized by test type for better classification
        
        Args:
            test_case: TestCase to save
            test_type: Test type (regression, smoke, integration, performance, security, exploratory, general)
            filename: Optional custom filename
            
        Returns:
            Path to saved JSON file
            
        Structure: test_suites/{test_type}/builder/{filename}.json
        Example: test_suites/regression/builder/test_001_login.json
        """
        # Create directory: test_suites/{test_type}/builder/
        suite_dir = self.project_root / "test_suites" / test_type / "builder"
        suite_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                               for c in test_case.name)
            filename = f"{test_case.test_case_id}_{safe_name}.json"
        
        filepath = suite_dir / filename
        
        # Add FULL metadata (same as recorder)
        test_case_dict = test_case.to_dict()
        test_case_dict['test_type'] = test_type  # NEW: regression, smoke, integration, etc.
        test_case_dict['source'] = 'builder'     # Source: builder
        test_case_dict['saved_to_suite_at'] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_case_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[TEST BUILDER] ✓ Saved to test_suites/{test_type}/builder/{filename}")
        logger.info(f"[TEST BUILDER] 🎯 Test Type: {test_type}")
        logger.info(f"[TEST BUILDER] 📁 Structure: test_suites/{test_type}/builder/")
        
        # Export as executable test files
        try:
            self.export_test_files(test_case)
        except Exception as e:
            logger.warning(f"[TEST BUILDER] Could not export test files: {str(e)}")
        
        return str(filepath)
    
    def export_test_files(self, test_case: TestCase, test_type: str = 'general') -> Dict[str, str]:
        """
        Export test case as executable test files in multiple languages.
        NOW ORGANIZED BY LANGUAGE: test_suites/{test_type}/exports/{language}/
        
        Args:
            test_case: TestCase to export
            test_type: Test type (regression, smoke, integration, etc.)
            
        Returns:
            Dictionary of language -> file path
        """
        exported_files = {}
        
        # NEW: Use test_suites/{test_type}/exports/{language}/ structure
        # Determine test_type from test case tags or use default
        if hasattr(test_case, 'tags') and test_case.tags:
            test_type = test_case.tags[0] if test_case.tags else test_type
        
        # Base exports directory: test_suites/{test_type}/exports/
        suite_exports_dir = self.project_root / "test_suites" / test_type / "exports"
        suite_exports_dir.mkdir(parents=True, exist_ok=True)
        
        safe_id = self._safe_filename(test_case.test_case_id)
        
        # Export Python test file → exports/python/
        if test_case.generated_code.get('python'):
            python_dir = suite_exports_dir / "python"
            python_dir.mkdir(exist_ok=True)
            python_filename = f"{safe_id}_test.py"
            python_path = python_dir / python_filename
            with open(python_path, 'w', encoding='utf-8') as f:
                f.write(test_case.generated_code['python'])
            exported_files['python'] = str(python_path)
            logger.info(f"[TEST EXPORT] ✓ Python: test_suites/{test_type}/exports/python/{python_filename}")
        
        # Export Java test file → exports/java/
        if test_case.generated_code.get('java'):
            java_dir = suite_exports_dir / "java"
            java_dir.mkdir(exist_ok=True)
            java_class_name = ''.join(word.capitalize() for word in re.findall(r'\w+', test_case.name))
            java_filename = f"{java_class_name}Test.java"
            java_path = java_dir / java_filename
            with open(java_path, 'w', encoding='utf-8') as f:
                f.write(test_case.generated_code['java'])
            exported_files['java'] = str(java_path)
            logger.info(f"[TEST EXPORT] ✓ Java: test_suites/{test_type}/exports/java/{java_filename}")
        
        # Export Playwright/JavaScript test file → exports/playwright/
        if test_case.generated_code.get('javascript'):
            playwright_dir = suite_exports_dir / "playwright"
            playwright_dir.mkdir(exist_ok=True)
            js_filename = f"{safe_id}.spec.js"
            js_path = playwright_dir / js_filename
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(test_case.generated_code['javascript'])
            exported_files['javascript'] = str(js_path)
            logger.info(f"[TEST EXPORT] ✓ Playwright: test_suites/{test_type}/exports/playwright/{js_filename}")
        
        # Export Cypress test file → exports/cypress/
        if test_case.generated_code.get('cypress'):
            cypress_dir = suite_exports_dir / "cypress"
            cypress_dir.mkdir(exist_ok=True)
            cy_filename = f"{safe_id}.cy.js"
            cy_path = cypress_dir / cy_filename
            with open(cy_path, 'w', encoding='utf-8') as f:
                f.write(test_case.generated_code['cypress'])
            exported_files['cypress'] = str(cy_path)
            logger.info(f"[TEST EXPORT] ✓ Cypress: test_suites/{test_type}/exports/cypress/{cy_filename}")
        
        return exported_files
    
    def load_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """
        Load test case from file by ID.
        Searches across all test types (regression, smoke, integration, etc.).
        
        Args:
            test_case_id: Test case ID (e.g., TC001)
            
        Returns:
            TestCase object or None if not found
        """
        # Check cache first
        if test_case_id in self.test_cases:
            return self.test_cases[test_case_id]
        
        # Search in default directory first (for backward compatibility)
        for filename in os.listdir(self.test_cases_dir):
            if filename.startswith(test_case_id) and filename.endswith('.json'):
                filepath = os.path.join(self.test_cases_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                test_case = TestCase.from_dict(data)
                self.test_cases[test_case_id] = test_case
                
                logger.info(f"[TEST BUILDER] Loaded test case: {test_case_id}")
                return test_case
        
        # Search across all test types (for semantic and categorized tests)
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general']
        for test_type in test_types:
            builder_dir = self.project_root / "test_suites" / test_type / "builder"
            if builder_dir.exists():
                for filename in os.listdir(builder_dir):
                    if filename.startswith(test_case_id) and filename.endswith('.json'):
                        filepath = builder_dir / filename
                        
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        test_case = TestCase.from_dict(data)
                        self.test_cases[test_case_id] = test_case
                        
                        logger.info(f"[TEST BUILDER] Loaded test case from {test_type}: {test_case_id}")
                        return test_case
        
        # INFO level since recorder tests are expected to not be in builder
        logger.info(f"[TEST BUILDER] Test case not found in builder (may be recorder test): {test_case_id}")
        return None
    
    def list_test_cases(self, tags: List[str] = None, 
                       priority: str = None,
                       status: str = "active",
                       exclude_preview: bool = True) -> List[Dict]:
        """
        List all test cases (optionally filtered).
        Scans test_suites/{test_type}/builder/ directories for all test types.
        
        Args:
            tags: Filter by tags (test must have all tags)
            priority: Filter by priority
            status: Filter by status (default: active only)
            exclude_preview: If True, exclude preview test cases (default: True)
            
        Returns:
            List of test case summaries
        """
        # CRITICAL FIX: Clear cache before loading to ensure fresh data from disk
        # This prevents stale cache from showing deleted tests or hiding new ones
        logger.info(f"[TEST BUILDER] Clearing cache before loading ({len(self.test_cases)} cached tests)")
        self.test_cases.clear()
        
        # Test types to scan
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general']
        
        # Load all test cases from test_suites structure
        loaded_count = 0
        for test_type in test_types:
            builder_dir = self.project_root / "test_suites" / test_type / "builder"
            if builder_dir.exists():
                for filename in os.listdir(builder_dir):
                    if filename.endswith('.json'):
                        filepath = builder_dir / filename
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                test_data = json.load(f)
                                test_case_id = test_data.get('test_case_id')
                                
                                if not test_case_id:
                                    logger.warning(f"[TEST BUILDER] Skipping {filename} - no test_case_id in JSON")
                                    continue
                                
                                test_case = TestCase.from_dict(test_data)
                                self.test_cases[test_case_id] = test_case
                                loaded_count += 1
                                
                        except Exception as e:
                            logger.error(f"[TEST BUILDER] Error loading test case {filepath}: {e}")
                            continue
        
        logger.info(f"[TEST BUILDER] Loaded {loaded_count} test cases from disk")
        
        # Filter test cases
        results = []
        for tc in self.test_cases.values():
            # EXCLUDE preview test cases (from Test Builder code preview)
            if exclude_preview and ('preview' in tc.tags or tc.test_case_id.startswith('Preview:')):
                continue
                
            # Status filter
            if status and tc.status != status:
                continue
            
            # Priority filter
            if priority and tc.priority != priority:
                continue
            
            # Tags filter
            if tags and not all(tag in tc.tags for tag in tags):
                continue
            
            # Convert steps to prompts format for frontend compatibility
            prompts = []
            if tc.steps:
                for step in tc.steps:
                    if isinstance(step, dict):
                        prompts.append({
                            'prompt': step.get('prompt', step.get('description', '')),
                            'type': step.get('type', 'action'),
                            'value': step.get('value', '')
                        })
                    else:
                        prompts.append({
                            'prompt': str(step),
                            'type': 'action',
                            'value': ''
                        })
            
            results.append({
                'test_case_id': tc.test_case_id,
                'name': tc.name,
                'description': tc.description,
                'tags': tc.tags,
                'priority': tc.priority,
                'status': tc.status,
                'created_at': tc.created_at,
                'timestamp': tc.created_at,  # For UI compatibility
                'step_count': len(tc.steps),
                'prompt_count': len(tc.steps),  # For UI compatibility
                'prompts': prompts,  # ✓ ADDED: Include prompts for semantic analysis
                'steps': tc.steps,   # ✓ ADDED: Include raw steps for compatibility
                'url': tc.url or '',              # Return empty string instead of 'undefined'
                'module': tc.tags[0] if tc.tags else 'Test Builder'
            })
        
        # Sort by timestamp descending (newest first)
        return sorted(results, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    def delete_test_case(self, test_case_id: str) -> bool:
        """
        Delete a test case.
        Searches across all test types (regression, smoke, integration, etc.)
        """
        # Remove from cache
        if test_case_id in self.test_cases:
            del self.test_cases[test_case_id]
        
        # Search and delete from all test type directories
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general']
        
        for test_type in test_types:
            builder_dir = self.project_root / "test_suites" / test_type / "builder"
            if builder_dir.exists():
                for filename in os.listdir(builder_dir):
                    if filename.startswith(test_case_id) and filename.endswith('.json'):
                        filepath = builder_dir / filename
                        try:
                            os.remove(filepath)
                            logger.info(f"[TEST BUILDER] ✓ Deleted test case: {test_case_id} from {test_type}/builder/")
                            return True
                        except Exception as e:
                            logger.error(f"[TEST BUILDER] ✗ Failed to delete {filepath}: {e}")
                            return False
        
        logger.warning(f"[TEST BUILDER] Test case {test_case_id} not found in any directory")
        return False


# Global test case builder instance
_test_case_builder = None

def get_test_case_builder() -> TestCaseBuilder:
    """Get or create global test case builder instance."""
    global _test_case_builder
    if _test_case_builder is None:
        _test_case_builder = TestCaseBuilder()
    return _test_case_builder


# Example usage
if __name__ == "__main__":
    # Test the builder
    builder = TestCaseBuilder()
    
    # Sample session data
    session_data = {
        'name': 'User Login Test',
        'description': 'Complete login flow test',
        'prompts': [
            {'step': 1, 'prompt': 'Navigate to login page', 'url': 'https://example.com/login'},
            {'step': 2, 'prompt': 'Enter username'},
            {'step': 3, 'prompt': 'Enter password'},
            {'step': 4, 'prompt': 'Click login button'},
            {'step': 5, 'prompt': 'Verify welcome message'}
        ]
    }
    
    # Build test case
    test_case = builder.build_from_session(
        session_data,
        tags=['login', 'smoke', 'authentication'],
        priority='high'
    )
    
    print("\n" + "="*80)
    print(f"GENERATED TEST CASE: {test_case.test_case_id}")
    print("="*80)
    print("\nPYTHON CODE:")
    print("-"*80)
    print(test_case.generated_code['python'])
    
    # Save test case
    filepath = builder.save_test_case(test_case)
    print(f"\nSaved to: {filepath}")
    
    # List test cases
    print("\nALL TEST CASES:")
    for tc_summary in builder.list_test_cases():
        print(f"  - {tc_summary['test_case_id']}: {tc_summary['name']} ({tc_summary['step_count']} steps)")
