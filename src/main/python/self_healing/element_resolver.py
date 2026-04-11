"""
Element Resolver - Maps natural language element names to actual locators

This module enables users to say things like:
- "click loginButton" 
- "enter text in usernameField"
- "verify errorMessage is displayed"

And the system automatically finds the element on the page and clicks it.

How it works:
1. User mentions an element name in their prompt
2. System scans the current page to find matching elements
3. Generates appropriate locator (id, name, text, xpath, css)
4. Executes the action with the discovered locator
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class ElementResolver:
    """
    Resolves natural language element names to actual Selenium locators.
    """
    
    def __init__(self, driver: webdriver.Chrome = None):
        self.driver = driver
        self.element_cache = {}  # Cache discovered elements
        
    def extract_element_name(self, prompt: str) -> Optional[str]:
        """
        Extract element name from prompt.
        
        Examples:
        - "click loginButton" -> "loginButton"
        - "enter text in usernameField" -> "usernameField"
        - "verify errorMsg is displayed" -> "errorMsg"
        """
        patterns = [
            r'click\s+(\w+)',
            r'in\s+(\w+)(?:\s+field)?',
            r'from\s+(\w+)',
            r'verify\s+(\w+)',
            r'get\s+text\s+from\s+(\w+)',
            r'select\s+.+?\s+from\s+(\w+)',
            r'wait\s+for\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                element_name = match.group(1)
                logger.info(f"[RESOLVER] Extracted element name: {element_name}")
                return element_name
        
        return None
    
    def find_element_by_name(self, element_name: str) -> Optional[Tuple[str, str]]:
        """
        Find element on page by multiple strategies.
        Returns: (locator_type, locator_value) or None
        
        Priority:
        1. ID matches element name
        2. Name attribute matches
        3. Class contains element name (camelCase/kebab-case)
        4. Text content contains element name
        5. Aria-label matches
        6. Data-testid matches
        """
        if not self.driver:
            logger.error("[RESOLVER] No WebDriver instance available")
            return None
        
        # Check cache first
        if element_name in self.element_cache:
            logger.info(f"[RESOLVER] Using cached locator for: {element_name}")
            return self.element_cache[element_name]
        
        try:
            # Strategy 1: ID (exact match)
            try:
                elem = self.driver.find_element(By.ID, element_name)
                locator = (By.ID, element_name)
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by ID: {element_name}")
                return locator
            except:
                pass
            
            # Strategy 2: ID (camelCase -> kebab-case)
            kebab_name = self._camel_to_kebab(element_name)
            try:
                elem = self.driver.find_element(By.ID, kebab_name)
                locator = (By.ID, kebab_name)
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by ID (kebab): {kebab_name}")
                return locator
            except:
                pass
            
            # Strategy 3: Name attribute
            try:
                elem = self.driver.find_element(By.NAME, element_name)
                locator = (By.NAME, element_name)
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by NAME: {element_name}")
                return locator
            except:
                pass
            
            # Strategy 4: Data-testid
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, f'[data-testid="{element_name}"]')
                locator = (By.CSS_SELECTOR, f'[data-testid="{element_name}"]')
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by data-testid: {element_name}")
                return locator
            except:
                pass
            
            # Strategy 5: Aria-label
            try:
                # Convert camelCase to space-separated for aria-label
                label = self._camel_to_words(element_name)
                elem = self.driver.find_element(By.CSS_SELECTOR, f'[aria-label*="{label}"]')
                locator = (By.CSS_SELECTOR, f'[aria-label*="{label}"]')
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by aria-label: {label}")
                return locator
            except:
                pass
            
            # Strategy 6: Class name contains element name
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, f'[class*="{kebab_name}"]')
                locator = (By.CSS_SELECTOR, f'[class*="{kebab_name}"]')
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by class: {kebab_name}")
                return locator
            except:
                pass
            
            # Strategy 7: Text content (for buttons, links)
            text = self._camel_to_words(element_name)
            xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
            try:
                elem = self.driver.find_element(By.XPATH, xpath)
                locator = (By.XPATH, xpath)
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by text: {text}")
                return locator
            except:
                pass
            
            # Strategy 8: Fuzzy match - scan all interactive elements
            locator = self._fuzzy_find_element(element_name)
            if locator:
                self.element_cache[element_name] = locator
                logger.info(f"[RESOLVER] Found by fuzzy match: {element_name}")
                return locator
            
            logger.warning(f"[RESOLVER] Could not find element: {element_name}")
            return None
            
        except Exception as e:
            logger.error(f"[RESOLVER] Error finding element {element_name}: {e}")
            return None
    
    def _fuzzy_find_element(self, element_name: str) -> Optional[Tuple[str, str]]:
        """
        Scan all interactive elements and find best match.
        """
        try:
            # Get all interactive elements
            selectors = [
                'button', 'input', 'select', 'textarea', 'a', 
                '[role="button"]', '[role="link"]', '[role="textbox"]'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements:
                    # Check all attributes
                    elem_id = elem.get_attribute('id') or ''
                    elem_name = elem.get_attribute('name') or ''
                    elem_class = elem.get_attribute('class') or ''
                    elem_text = elem.text or ''
                    elem_placeholder = elem.get_attribute('placeholder') or ''
                    elem_label = elem.get_attribute('aria-label') or ''
                    
                    # Combine all searchable text
                    searchable = f"{elem_id} {elem_name} {elem_class} {elem_text} {elem_placeholder} {elem_label}".lower()
                    
                    # Check if element_name appears in any attribute
                    if element_name.lower() in searchable or self._camel_to_kebab(element_name) in searchable:
                        # Generate best locator for this element
                        if elem_id:
                            return (By.ID, elem_id)
                        elif elem_name:
                            return (By.NAME, elem_name)
                        else:
                            # Use XPath with multiple attributes
                            xpath = self._generate_xpath(elem)
                            return (By.XPATH, xpath)
            
            return None
            
        except Exception as e:
            logger.error(f"[RESOLVER] Fuzzy search error: {e}")
            return None
    
    def _generate_xpath(self, element: WebElement) -> str:
        """Generate XPath for element using its attributes."""
        tag = element.tag_name
        elem_id = element.get_attribute('id')
        elem_class = element.get_attribute('class')
        elem_text = element.text
        
        if elem_id:
            return f"//{tag}[@id='{elem_id}']"
        elif elem_class:
            return f"//{tag}[contains(@class, '{elem_class.split()[0]}')]"
        elif elem_text:
            return f"//{tag}[contains(text(), '{elem_text[:20]}')]"
        else:
            return f"({tag})[1]"
    
    def _camel_to_kebab(self, text: str) -> str:
        """Convert camelCase to kebab-case: loginButton -> login-button"""
        return re.sub(r'([a-z])([A-Z])', r'\1-\2', text).lower()
    
    def _camel_to_words(self, text: str) -> str:
        """Convert camelCase to words: loginButton -> login button"""
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', text).lower()
    
    def resolve_prompt_with_element(self, prompt: str) -> Dict:
        """
        Main method: Extract element name and find its locator.
        
        Returns:
        {
            'original_prompt': 'click loginButton',
            'element_name': 'loginButton',
            'locator_type': 'By.ID',
            'locator_value': 'loginButton',
            'generic_prompt': 'click <element>',
            'success': True
        }
        """
        result = {
            'original_prompt': prompt,
            'element_name': None,
            'locator_type': None,
            'locator_value': None,
            'generic_prompt': prompt,
            'success': False
        }
        
        # Extract element name from prompt
        element_name = self.extract_element_name(prompt)
        if not element_name:
            logger.warning(f"[RESOLVER] No element name found in prompt: {prompt}")
            return result
        
        result['element_name'] = element_name
        
        # Find element on page
        locator = self.find_element_by_name(element_name)
        if not locator:
            logger.error(f"[RESOLVER] Element not found on page: {element_name}")
            return result
        
        locator_type, locator_value = locator
        result['locator_type'] = locator_type
        result['locator_value'] = locator_value
        result['success'] = True
        
        # Create generic prompt for dataset matching
        result['generic_prompt'] = prompt.replace(element_name, '<element>')
        
        logger.info(f"[RESOLVER] Successfully resolved: {element_name} -> {locator_type}('{locator_value}')")
        return result
    
    def clear_cache(self):
        """Clear the element cache (use when page changes)."""
        self.element_cache.clear()
        logger.info("[RESOLVER] Element cache cleared")


def test_element_resolver():
    """Test the element resolver with sample page."""
    from selenium.webdriver.chrome.options import Options
    
    # Setup Chrome
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to a test page
        driver.get('https://www.saucedemo.com/')
        
        # Initialize resolver
        resolver = ElementResolver(driver)
        
        # Test different prompts
        test_prompts = [
            "click loginButton",
            "enter text in username",
            "enter password in password",
            "click login-button",
            "verify error message",
        ]
        
        print("\n" + "=" * 80)
        print("ELEMENT RESOLVER TEST")
        print("=" * 80)
        
        for prompt in test_prompts:
            print(f"\n📝 Prompt: '{prompt}'")
            result = resolver.resolve_prompt_with_element(prompt)
            
            if result['success']:
                print(f"   ✅ Element: {result['element_name']}")
                print(f"   📍 Locator: {result['locator_type']}('{result['locator_value']}')")
                print(f"   🔄 Generic: {result['generic_prompt']}")
            else:
                print(f"   ❌ Failed to resolve element")
        
        print("\n" + "=" * 80)
        
    finally:
        driver.quit()


if __name__ == "__main__":
    # Run test
    test_element_resolver()
