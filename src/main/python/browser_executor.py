"""
Browser executor module to run generated Selenium code in real browser.
"""

import re
import time
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BrowserExecutor:
    """Executes generated Selenium code in a real browser."""
    
    def __init__(self):
        self.driver = None
        self.driver_type = "chrome"  # Default browser
        self.recording_mode = False
        
    def initialize_driver(self, browser: str = "chrome", headless: bool = False):
        """
        Initialize WebDriver instance.
        
        Args:
            browser: Browser type (chrome, firefox, edge)
            headless: Run browser in headless mode
        """
        try:
            if browser.lower() == "chrome":
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options
                from webdriver_manager.chrome import ChromeDriverManager
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif browser.lower() == "firefox":
                from selenium import webdriver
                from selenium.webdriver.firefox.service import Service
                from selenium.webdriver.firefox.options import Options
                from webdriver_manager.firefox import GeckoDriverManager
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                
            elif browser.lower() == "edge":
                from selenium import webdriver
                from selenium.webdriver.edge.service import Service
                from selenium.webdriver.edge.options import Options
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                
                service = Service(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
            
            self.driver.maximize_window()
            logger.info(f"[OK] {browser.capitalize()} browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize {browser} browser: {str(e)}")
            return False
    
    def execute_code(self, generated_code: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute generated Selenium code.
        
        Args:
            generated_code: Java-style Selenium code to execute
            url: Optional URL to navigate to before executing code
            
        Returns:
            Dict with execution status and results
        """
        if not self.driver:
            if not self.initialize_driver():
                return {
                    'success': False,
                    'error': 'Failed to initialize browser driver'
                }
        
        try:
            # Log what we received
            logger.info(f"[EXECUTOR] execute_code called with url='{url}'")
            
            # Check if browser is still alive, reinitialize if crashed/invalid
            try:
                test_url = self.driver.current_url
                logger.info(f"[BROWSER] Session OK - current URL: {test_url[:100]}")
            except Exception as e:
                logger.warning(f"[BROWSER] Session invalid ({str(e)}), reinitializing...")
                try:
                    self.driver.quit()
                except:
                    pass
                self.initialize_driver()
                logger.info(f"[BROWSER] New session initialized")
            
            # Navigate to URL if provided AND different from current URL
            # This prevents re-navigation and preserves session (e.g., login state)
            if url:
                try:
                    current_url = self.driver.current_url
                    logger.info(f"[EXECUTOR] Current URL: '{current_url}'")
                    logger.info(f"[EXECUTOR] Target URL: '{url}'")
                    
                    # Only navigate if URL is different (ignore trailing slashes and fragments)
                    current_base = current_url.split('#')[0].rstrip('/')
                    target_base = url.split('#')[0].rstrip('/')
                    
                    logger.info(f"[EXECUTOR] Comparing: '{current_base}' vs '{target_base}'")
                    
                    if current_base != target_base and not current_base.startswith(target_base):
                        logger.info(f"[NAVIGATE] URL changed - navigating from '{current_url}' to '{url}'")
                        self.driver.get(url)
                        time.sleep(2)  # Wait for page load
                        
                        # Close sticky popup by clicking the sticky-close div
                        try:
                            popup_closed = self.driver.execute_script("""
                                var stickyClose = document.getElementById('sticky-close');
                                if (stickyClose) {
                                    stickyClose.click();
                                    return 'Popup closed';
                                }
                                return 'No popup found';
                            """)
                            logger.info(f"[NAVIGATE] Popup handling: {popup_closed}")
                            time.sleep(0.5)
                        except:
                            pass
                        
                        logger.info("[NAVIGATE] Page loaded successfully")
                    else:
                        logger.info(f"[NAVIGATE] ✓ Already on target URL - SKIPPING navigation to preserve session")
                except Exception as e:
                    # If can't get current URL (e.g., no page loaded yet), navigate
                    logger.info(f"[NAVIGATE] Cannot determine current URL ({str(e)}), navigating to: {url}")
                    self.driver.get(url)
                    time.sleep(2)
                    
                    # Close sticky popup by clicking the sticky-close div
                    try:
                        popup_closed = self.driver.execute_script("""
                            var stickyClose = document.getElementById('sticky-close');
                            if (stickyClose) {
                                stickyClose.click();
                                return 'Popup closed';
                            }
                            return 'No popup found';
                        """)
                        logger.info(f"[NAVIGATE] Popup handling: {popup_closed}")
                        time.sleep(0.5)
                    except:
                        pass
                    
                    logger.info("[NAVIGATE] Page loaded successfully")
            else:
                logger.info("[EXECUTOR] No URL provided - staying on current page")
            
            # Use the generated Python code directly (no conversion needed)
            python_code = generated_code
            logger.info(f"[EXECUTOR] Generated Python code:\n{python_code}")
            
            # Store current URL before execution
            url_before = self.driver.current_url
            logger.info(f"[NAVIGATE] Starting URL: {url_before[:100]}")
            
            # Execute the Python code
            result = self._execute_python_code(python_code)
            
            # Always check for redirects after execution (important for login flows)
            # Wait for redirects to complete - check every second for up to 30 seconds
            max_wait = 30
            stable_count = 0
            previous_url = url_before
            url_changed = False
            
            logger.info(f"[NAVIGATE] Monitoring for redirects (up to {max_wait}s)...")
            
            for i in range(max_wait):
                time.sleep(1)
                current_url = self.driver.current_url
                
                # Check if we're on an auth/token page
                is_auth = 'authenticate' in current_url or '/auth' in current_url or 'token=' in current_url
                
                if is_auth:
                    logger.info(f"[NAVIGATE] On auth page ({i+1}s): {current_url[:100]}...")
                    previous_url = current_url
                    stable_count = 0
                    url_changed = True
                    continue
                
                # Check if URL changed from previous check
                if current_url != previous_url:
                    logger.info(f"[NAVIGATE] URL changed to: {current_url[:100]}")
                    previous_url = current_url
                    stable_count = 0
                    url_changed = True
                    continue
                
                # URL is stable
                stable_count += 1
                
                # If URL never changed and we've waited 3 seconds, we're done
                if not url_changed and stable_count >= 3:
                    logger.info(f"[NAVIGATE] No redirect detected after 3s, staying at: {current_url[:100]}")
                    break
                
                # If URL changed and is now stable for 3 seconds, we're done
                if url_changed and stable_count >= 3:
                    logger.info(f"[NAVIGATE] URL stable for 3s at: {current_url[:100]}")
                    break
            
            final_url = self.driver.current_url
            if url_before != final_url:
                logger.info(f"[NAVIGATE] Final destination (changed): {final_url[:100]}")
            else:
                logger.info(f"[NAVIGATE] Final destination (unchanged): {final_url[:100]}")
            
            return {
                'success': True,
                'executed_code': python_code,
                'result': result,
                'current_url': self.driver.current_url,
                'page_title': self.driver.title
            }
            
        except Exception as e:
            # Check if it's an invalid session error - try to recover once
            error_msg = str(e)
            if 'invalid session id' in error_msg.lower() or 'session' in error_msg.lower():
                logger.warning(f"[BROWSER] Session error detected, attempting recovery...")
                try:
                    self.initialize_driver()
                    logger.info(f"[BROWSER] Browser reinitialized, retrying execution...")
                    
                    # Retry the execution once with new session
                    if url:
                        self.driver.get(url)
                        time.sleep(3)
                    
                    # Use the generated code directly (already Python)
                    python_code = generated_code
                    result = self._execute_python_code(python_code)
                    
                    return {
                        'success': True,
                        'executed_code': python_code,
                        'result': result,
                        'current_url': self.driver.current_url,
                        'page_title': self.driver.title,
                        'recovered': True
                    }
                except Exception as retry_error:
                    logger.error(f"[ERROR] Recovery failed: {str(retry_error)}")
                    return {
                        'success': False,
                        'error': f"Recovery failed: {str(retry_error)}",
                        'executed_code': python_code if 'python_code' in locals() else None
                    }
            
            logger.error(f"[ERROR] Execution error: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'executed_code': python_code if 'python_code' in locals() else None
            }
    
    def _convert_java_to_python(self, java_code: str) -> str:
        """Convert Java Selenium code to Python Selenium code."""
        
        logger.info(f"[CONVERT] Input Java code:\n{java_code}")
        
        # Split by step comments to handle compound commands
        step_pattern = r'// Step \d+:.*?\n'
        steps = re.split(step_pattern, java_code)
        
        all_conversions = []
        
        # Process each step separately
        for step_code in steps:
            if not step_code.strip():
                continue
                
            # Remove remaining Java comments and clean up
            step_code = re.sub(r'//.*$', '', step_code, flags=re.MULTILINE)
            step_code = step_code.strip()
            
            if not step_code:
                continue
            
            # Log original code
            logger.info(f"Converting step:\n{step_code}")
            
            conversions = self._convert_single_action(step_code)
            if conversions:
                all_conversions.extend(conversions)
                all_conversions.append('')  # Add blank line between steps
        
        # If no steps found, try converting as single block
        if not all_conversions:
            # Remove Java comments and clean up
            java_code = re.sub(r'//.*$', '', java_code, flags=re.MULTILINE)
            java_code = java_code.strip()
            logger.info(f"Original Java code to convert:\n{java_code}")
            all_conversions = self._convert_single_action(java_code)
        
        python_code = '\n'.join(all_conversions)
        logger.info(f"Final converted Python code:\n{python_code}")
        return python_code
    
    def _convert_single_action(self, java_code: str) -> list:
        """Convert a single action from Java to Python."""
        conversions = []
        
        # Handle Java try-catch with multiple fallback strategies
        # Look for our specific fallback pattern with linkText -> button -> any element
        if 'try {' in java_code and 'By.linkText' in java_code and ('//button[contains(text()' in java_code or '//button[contains(normalize-space' in java_code):
            # Extract the text value from linkText
            linktext_match = re.search(r'By\.linkText\("([^"]+)"\)', java_code)
            if linktext_match:
                text_value = linktext_match.group(1)
                # Generate Python code with fallback strategies
                conversions.append('# Try multiple locator strategies')
                conversions.append('element_found = False')
                conversions.append('wait = WebDriverWait(driver, 5)')
                conversions.append('')
                conversions.append('# Strategy 1: Try as link')
                conversions.append('try:')
                conversions.append(f'    element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "{text_value}")))')
                conversions.append('    element.click()')
                conversions.append('    element_found = True')
                conversions.append('except:')
                conversions.append('    pass')
                conversions.append('')
                conversions.append('# Strategy 2: Try as button')
                conversions.append('if not element_found:')
                conversions.append('    try:')
                conversions.append(f'        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), \'{text_value}\')]")))')
                conversions.append('        element.click()')
                conversions.append('        element_found = True')
                conversions.append('    except:')
                conversions.append('        pass')
                conversions.append('')
                conversions.append('# Strategy 3: Try any element with text')
                conversions.append('if not element_found:')
                conversions.append(f'    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(normalize-space(.), \'{text_value}\')]")))')
                conversions.append('    element.click()')
                return conversions
        
        # Convert driver.get() - navigation (improved pattern matching)
        get_matches = re.findall(r'driver\.get\s*\(\s*"([^"]+)"\s*\)', java_code)
        if get_matches:
            for url in get_matches:
                conversions.append(f'driver.get("{url}")')
                conversions.append('time.sleep(1)  # Wait for page load')
            return conversions  # Return early after handling navigation
        
        # Convert findElement + click pattern
        if 'findElement' in java_code and 'click()' in java_code:
            # Try different By locator types
            id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
            if id_match:
                element_id = id_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.ID, "{element_id}")))')
                conversions.append('element.click()')
                return conversions
            
            xpath_match = re.search(r'By\.xpath\s*\(\s*"([^"\\]*(?:\\.[^"\\]*)*)"\s*\)', java_code)
            if xpath_match:
                xpath = xpath_match.group(1)
                # Unescape the quotes in xpath
                xpath = xpath.replace('\\"', '"')
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.XPATH, r"""{xpath}""")))')
                conversions.append('element.click()')
                return conversions
            
            css_match = re.search(r'By\.cssSelector\s*\(\s*"([^"]+)"\s*\)', java_code)
            if css_match:
                css = css_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "{css}")))')
                conversions.append('element.click()')
                return conversions
            
            name_match = re.search(r'By\.name\s*\(\s*"([^"]+)"\s*\)', java_code)
            if name_match:
                name = name_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.NAME, "{name}")))')
                conversions.append('element.click()')
                return conversions
            
            linktext_match = re.search(r'By\.linkText\s*\(\s*"([^"]+)"\s*\)', java_code)
            if linktext_match:
                link_text = linktext_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "{link_text}")))')
                conversions.append('element.click()')
                return conversions
            
            xpath_match = re.search(r'By\.xpath\s*\(\s*"([^"]+)"\s*\)', java_code)
            if xpath_match:
                xpath = xpath_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.XPATH, "{xpath}")))')
                conversions.append('element.click()')
                return conversions
        
        # Convert sendKeys pattern
        if 'findElement' in java_code and 'sendKeys' in java_code:
            id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
            text_match = re.search(r'sendKeys\s*\(\s*"([^"]+)"\s*\)', java_code)
            
            if id_match and text_match:
                element_id = id_match.group(1)
                text = text_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.visibility_of_element_located((By.ID, "{element_id}")))')
                conversions.append(f'element.send_keys("{text}")')
                return conversions
        
        # Convert Select dropdown
        if 'Select(' in java_code and 'selectByVisibleText' in java_code:
            id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
            text_match = re.search(r'selectByVisibleText\s*\(\s*"([^"]+)"\s*\)', java_code)
            
            if id_match and text_match:
                element_id = id_match.group(1)
                option_text = text_match.group(1)
                conversions.append(f'wait = WebDriverWait(driver, 10)')
                conversions.append(f'element = wait.until(EC.visibility_of_element_located((By.ID, "{element_id}")))')
                conversions.append('select = Select(element)')
                conversions.append(f'select.select_by_visible_text("{option_text}")')
                return conversions
        
        # Convert WebDriverWait
        if 'WebDriverWait' in java_code:
            timeout_match = re.search(r'Duration\.ofSeconds\s*\(\s*(\d+)\s*\)', java_code)
            timeout = timeout_match.group(1) if timeout_match else '10'
            
            if 'visibilityOfElementLocated' in java_code:
                id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
                if id_match:
                    element_id = id_match.group(1)
                    conversions.append(f'wait = WebDriverWait(driver, {timeout})')
                    conversions.append(f'element = wait.until(EC.visibility_of_element_located((By.ID, "{element_id}")))')
                    return conversions
            
            if 'elementToBeClickable' in java_code:
                id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
                if id_match:
                    element_id = id_match.group(1)
                    conversions.append(f'wait = WebDriverWait(driver, {timeout})')
                    conversions.append(f'element = wait.until(EC.element_to_be_clickable((By.ID, "{element_id}")))')
                    return conversions
        
        # Convert assertions
        if 'Assert.assertTrue' in java_code:
            if 'isDisplayed()' in java_code:
                id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
                if id_match:
                    element_id = id_match.group(1)
                    conversions.append(f'element = driver.find_element(By.ID, "{element_id}")')
                    conversions.append('assert element.is_displayed(), "Element is not displayed"')
                    return conversions
            
            if 'contains(' in java_code:
                text_match = re.search(r'contains\s*\(\s*"([^"]+)"\s*\)', java_code)
                if text_match:
                    expected_text = text_match.group(1)
                    id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
                    if id_match:
                        element_id = id_match.group(1)
                        conversions.append(f'element = driver.find_element(By.ID, "{element_id}")')
                        conversions.append(f'assert "{expected_text}" in element.text, "Text not found"')
                        return conversions
        
        if 'Assert.assertEquals' in java_code:
            # Extract expected and actual values
            expected_match = re.search(r'Assert\.assertEquals\s*\(\s*"([^"]+)"', java_code)
            if expected_match:
                expected_value = expected_match.group(1)
                
                if 'getTitle()' in java_code:
                    conversions.append(f'assert driver.title == "{expected_value}", "Title mismatch"')
                    return conversions
                
                if 'getText()' in java_code:
                    id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
                    if id_match:
                        element_id = id_match.group(1)
                        conversions.append(f'element = driver.find_element(By.ID, "{element_id}")')
                        conversions.append(f'assert element.text == "{expected_value}", "Text mismatch"')
                        return conversions
        
        # Convert Actions (hover, drag-and-drop)
        if 'Actions(' in java_code and 'moveToElement' in java_code:
            id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', java_code)
            if id_match:
                element_id = id_match.group(1)
                conversions.append(f'element = driver.find_element(By.ID, "{element_id}")')
                conversions.append('actions = ActionChains(driver)')
                conversions.append('actions.move_to_element(element).perform()')
                return conversions
        
        # Convert Alert handling
        if 'switchTo().alert()' in java_code or 'driver.switchTo().alert' in java_code:
            if 'accept()' in java_code:
                conversions.append('alert = driver.switch_to.alert')
                conversions.append('alert.accept()')
                return conversions
            if 'dismiss()' in java_code:
                conversions.append('alert = driver.switch_to.alert')
                conversions.append('alert.dismiss()')
                return conversions
        
        # Convert window switching
        if 'switchTo().window' in java_code or 'getWindowHandles()' in java_code:
            conversions.append('# Switch to new window')
            conversions.append('windows = driver.window_handles')
            conversions.append('driver.switch_to.window(windows[-1])')
            return conversions
        
        # Fallback - return original as comment
        if not conversions:
            conversions.append(f'# TODO: Convert manually - {java_code[:100]}')
        
        return conversions
    
    def _execute_python_code(self, python_code: str) -> Any:
        """Execute Python Selenium code with driver context."""
        
        # Import required modules
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.common.keys import Keys
        
        # Create execution context with all necessary objects
        exec_globals = {
            'driver': self.driver,
            'By': By,
            'WebDriverWait': WebDriverWait,
            'EC': EC,
            'Select': Select,
            'Keys': Keys,
            'time': time,
            'logger': logger
        }
        
        try:
            # Execute the Python code
            exec(python_code, exec_globals)
            
            return {
                'executed': True,
                'message': 'Code executed successfully'
            }
        except Exception as e:
            from selenium.common.exceptions import NoSuchElementException, TimeoutException
            
            if isinstance(e, NoSuchElementException):
                logger.error(f"[ERROR] Element not found. The page might not have loaded completely or the locator is incorrect.")
                logger.error(f"Details: {str(e)}")
            elif isinstance(e, TimeoutException):
                logger.error(f"[ERROR] Timeout waiting for element. The element may not exist or takes longer to load.")
                logger.error(f"Details: {str(e)}")
            else:
                logger.error(f"Python execution error: {str(e)}")
            
            logger.error(f"Code that failed:\n{python_code}")
            raise
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self.driver:
            return {'error': 'Browser not initialized'}
        
        try:
            return {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_source_length': len(self.driver.page_source)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def take_screenshot(self, filename: str = 'screenshot.png') -> Dict[str, Any]:
        """Take screenshot of current page."""
        if not self.driver:
            return {'error': 'Browser not initialized'}
        
        try:
            filepath = self.driver.save_screenshot(filename)
            return {
                'success': True,
                'filepath': filename,
                'message': f'Screenshot saved to {filename}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def inject_recorder_script(self):
        """Inject the recorder JavaScript into the current page."""
        if not self.driver:
            return {'error': 'Browser not initialized'}
        
        try:
            # Get the path to the recorder script
            script_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'resources', 'web', 'recorder-inject.js'
            )
            
            if os.path.exists(script_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                # Inject the script
                self.driver.execute_script(script_content)
                logger.info("[OK] Recorder script injected successfully")
                return {'success': True, 'message': 'Recorder script injected'}
            else:
                logger.warning(f"[WARNING] Recorder script not found at {script_path}")
                return {'error': 'Recorder script file not found'}
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to inject recorder script: {str(e)}")
            return {'error': str(e)}
    
    def start_recording(self):
        """Start recording user actions."""
        if not self.driver:
            return {'error': 'Browser not initialized'}
        
        try:
            # Inject recorder if not already done
            self.inject_recorder_script()
            
            # Start the recorder
            self.driver.execute_script("window.startRecorderCapture();")
            self.recording_mode = True
            
            logger.info("[OK] Recording started")
            return {'success': True, 'message': 'Recording started'}
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start recording: {str(e)}")
            return {'error': str(e)}
    
    def stop_recording(self):
        """Stop recording user actions."""
        if not self.driver:
            return {'error': 'Browser not initialized'}
        
        try:
            self.driver.execute_script("window.stopRecorderCapture();")
            self.recording_mode = False
            
            logger.info("[OK] Recording stopped")
            return {'success': True, 'message': 'Recording stopped'}
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to stop recording: {str(e)}")
            return {'error': str(e)}
    
    def close(self):
        """Close browser and cleanup."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("[OK] Browser closed successfully")
            except Exception as e:
                logger.error(f"[ERROR] Error closing browser: {str(e)}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close()
