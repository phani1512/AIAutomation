"""
Self-Healing Element Locator with Dynamic Detection
Provides fallback strategies and automatic element detection when primary locators fail.
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logger = logging.getLogger(__name__)

class SelfHealingLocator:
    """Provides dynamic element detection with self-healing capabilities."""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize self-healing locator.
        
        Args:
            dataset_path: Path to dataset JSON file. If None, loads from default location.
        """
        self.fallback_cache = {}
        self.success_cache = {}  # Cache successful locators for faster future lookups
        
        if dataset_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
            # Use combined dataset with generic patterns for better self-healing
            dataset_path = os.path.join(project_root, 'resources', 'ml_data', 'datasets', 'combined-training-dataset-final.json')
        
        self._load_fallback_strategies(dataset_path)
    
    def _load_fallback_strategies(self, dataset_path: str):
        """Load fallback locator strategies from dataset."""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for entry in data:
                for step in entry.get('steps', []):
                    locator = step.get('locator', '')
                    fallbacks = step.get('fallback_locators', [])
                    
                    if locator and fallbacks:
                        self.fallback_cache[locator] = fallbacks
            
            logger.info(f"[SELF-HEAL] Loaded {len(self.fallback_cache)} fallback strategies")
        except Exception as e:
            logger.warning(f"[SELF-HEAL] Could not load fallback strategies: {e}")
    
    def _parse_locator(self, locator_string: str) -> tuple:
        """
        Parse locator string to (By type, value) tuple.
        
        Examples:
            'By.id("email")' -> (By.ID, 'email')
            'By.cssSelector(".btn-primary")' -> (By.CSS_SELECTOR, '.btn-primary')
            'By.xpath("//button[contains(., \"Login\")]")' -> (By.XPATH, '//button[contains(., "Login")]')
        """
        import re
        
        # First, remove outer quotes if the entire string is wrapped
        locator_string = locator_string.strip()
        if (locator_string.startswith('"') and locator_string.endswith('"')) or \
           (locator_string.startswith("'") and locator_string.endswith("'")):
            locator_string = locator_string[1:-1]
        
        # Match pattern: By.METHOD("value") or By.METHOD('value')
        # Use a more robust pattern that handles escaped quotes
        # This matches everything between the opening quote and the last closing quote before the final )
        match = re.search(r'By\.(\w+)\((["\'])(.+?)\2\)\s*$', locator_string)
        
        if match:
            method = match.group(1)
            value = match.group(3)
            # Unescape any escaped quotes
            value = value.replace('\\"', '"').replace("\\'", "'")
        else:
            # Fallback: Try to extract method and value manually
            if 'By.' not in locator_string:
                return None, None
            
            try:
                # Extract method name
                method_match = re.search(r'By\.(\w+)', locator_string)
                if not method_match:
                    return None, None
                method = method_match.group(1)
                
                # Extract value - everything between first ( and last )
                paren_start = locator_string.index('(')
                paren_end = locator_string.rindex(')')
                value_with_quotes = locator_string[paren_start+1:paren_end].strip()
                
                # Remove surrounding quotes
                if (value_with_quotes.startswith('"') and value_with_quotes.endswith('"')) or \
                   (value_with_quotes.startswith("'") and value_with_quotes.endswith("'")):
                    value = value_with_quotes[1:-1]
                else:
                    value = value_with_quotes
                
                # Unescape quotes
                value = value.replace('\\"', '"').replace("\\'", "'")
            except (ValueError, IndexError):
                return None, None
        
        # Map method names to By constants
        by_map = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'cssSelector': By.CSS_SELECTOR,
            'className': By.CLASS_NAME,
            'tagName': By.TAG_NAME,
            'linkText': By.LINK_TEXT,
            'partialLinkText': By.PARTIAL_LINK_TEXT
        }
        
        by_type = by_map.get(method)
        return by_type, value
    
    def find_element(self, driver: WebDriver, locator: str, context: Optional[str] = None) -> Optional[WebElement]:
        """
        Find element with self-healing capability.
        
        Args:
            driver: Selenium WebDriver instance
            locator: Primary locator string (e.g., 'By.id("email")')
            context: Optional context for logging
            
        Returns:
            WebElement if found, None otherwise
        """
        # Check success cache first
        if locator in self.success_cache:
            try:
                by_type, value = self._parse_locator(self.success_cache[locator])
                element = driver.find_element(by_type, value)
                logger.debug(f"[SELF-HEAL] ✓ Found using cached successful locator")
                return element
            except NoSuchElementException:
                # Cached locator failed, remove from cache
                del self.success_cache[locator]
        
        # Try primary locator
        by_type, value = self._parse_locator(locator)
        if by_type and value:
            try:
                element = driver.find_element(by_type, value)
                logger.debug(f"[SELF-HEAL] ✓ Found using primary locator: {locator}")
                self.success_cache[locator] = locator  # Cache success
                return element
            except NoSuchElementException:
                logger.warning(f"[SELF-HEAL] ✗ Primary locator failed: {locator}")
        
        # Try fallback locators
        fallbacks = self.fallback_cache.get(locator, [])
        for i, fallback in enumerate(fallbacks, 1):
            by_type, value = self._parse_locator(fallback)
            if by_type and value:
                try:
                    element = driver.find_element(by_type, value)
                    logger.info(f"[SELF-HEAL] ✓ Found using fallback #{i}: {fallback}")
                    self.success_cache[locator] = fallback  # Cache successful fallback
                    return element
                except NoSuchElementException:
                    logger.debug(f"[SELF-HEAL] ✗ Fallback #{i} failed: {fallback}")
                    continue
        
        # All strategies failed
        logger.error(f"[SELF-HEAL] ✗ All strategies failed for: {locator}")
        return None
    
    def find_elements(self, driver: WebDriver, locator: str) -> List[WebElement]:
        """
        Find multiple elements with self-healing capability.
        
        Args:
            driver: Selenium WebDriver instance
            locator: Primary locator string
            
        Returns:
            List of WebElements (may be empty if none found)
        """
        # Try primary locator
        by_type, value = self._parse_locator(locator)
        if by_type and value:
            try:
                elements = driver.find_elements(by_type, value)
                if elements:
                    logger.debug(f"[SELF-HEAL] ✓ Found {len(elements)} elements using primary locator")
                    return elements
            except Exception as e:
                logger.warning(f"[SELF-HEAL] Primary locator failed: {e}")
        
        # Try fallback locators
        fallbacks = self.fallback_cache.get(locator, [])
        for i, fallback in enumerate(fallbacks, 1):
            by_type, value = self._parse_locator(fallback)
            if by_type and value:
                try:
                    elements = driver.find_elements(by_type, value)
                    if elements:
                        logger.info(f"[SELF-HEAL] ✓ Found {len(elements)} elements using fallback #{i}")
                        return elements
                except Exception:
                    continue
        
        logger.warning(f"[SELF-HEAL] No elements found for: {locator}")
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about self-healing performance."""
        return {
            'total_fallback_strategies': len(self.fallback_cache),
            'cached_successful_locators': len(self.success_cache),
            'success_rate': len(self.success_cache) / max(len(self.fallback_cache), 1) * 100
        }


# Convenience functions for easy usage
_global_healer = None

def get_healer() -> SelfHealingLocator:
    """Get global self-healing locator instance."""
    global _global_healer
    if _global_healer is None:
        _global_healer = SelfHealingLocator()
    return _global_healer

def find_element_with_healing(driver: WebDriver, locator: str) -> Optional[WebElement]:
    """Convenience function to find element with self-healing."""
    return get_healer().find_element(driver, locator)

def find_elements_with_healing(driver: WebDriver, locator: str) -> List[WebElement]:
    """Convenience function to find elements with self-healing."""
    return get_healer().find_elements(driver, locator)
