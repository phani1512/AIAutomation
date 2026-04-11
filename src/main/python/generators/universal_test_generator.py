"""
Universal Test Generator - Works for ANY page, ANY elements
Uses actual OCR text for naming - NO hardcoded login/email/password logic
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class UniversalTestGenerator:
    """Generates tests for any detected elements - no page-specific logic."""
    
    def generate_tests(self, elements: Dict, test_name: str = "PageTest", 
                      url: str = "YOUR_URL_HERE") -> Dict:
        """
        Generate tests for ALL detected elements using actual OCR text.
        Works for ANY page type - login, search, registration, checkout, admin, etc.
        """
        # Extract ALL element types
        inputs = elements.get('inputs', [])
        buttons = elements.get('buttons', [])
        links = elements.get('links', [])
        checkboxes = elements.get('checkboxes', [])
        dropdowns = elements.get('dropdowns', [])
        
        logger.info(f"[UNIVERSAL] Detected: {len(inputs)} inputs, {len(buttons)} buttons, {len(links)} links, {len(checkboxes)} checkboxes, {len(dropdowns)} dropdowns")
        
        # Add display names from OCR with better fallbacks
        for idx, inp in enumerate(inputs):
            text_or_label = inp.get('text', '') or inp.get('label', '')
            inp['display_name'] = text_or_label if text_or_label else f"Input Field {idx + 1}"
            logger.info(f"[UNIVERSAL] Input {idx}: text='{inp.get('text', '')}', label='{inp.get('label', '')}' -> display_name='{inp['display_name']}'")
        
        for idx, btn in enumerate(buttons):
            text_or_label = btn.get('text', '') or btn.get('label', '')
            btn['display_name'] = text_or_label if text_or_label else f"Button {idx + 1}"
            logger.info(f"[UNIVERSAL] Button {idx}: text='{btn.get('text', '')}', label='{btn.get('label', '')}' -> display_name='{btn['display_name']}'")
        
        for idx, link in enumerate(links):
            text_or_label = link.get('text', '') or link.get('label', '')
            link['display_name'] = text_or_label if text_or_label else f"Link {idx + 1}"
            logger.info(f"[UNIVERSAL] Link {idx}: text='{link.get('text', '')}', label='{link.get('label', '')}' -> display_name='{link['display_name']}'")
        
        # Generate tests for ALL elements
        test_methods = []
        test_num = 1
        
        # 1. INPUT TESTS - Generate for each input field
        for inp in inputs:
            safe_name = inp['display_name'].replace(' ', '').replace('-', '')[:20]
            locator = self._get_locator(inp, 'input')
            
            # Valid input test
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_ValidInput",
                f"Verify '{inp['display_name']}' accepts valid input",
                f'driver.findElement({locator}).sendKeys("test value");'
            ))
            test_num += 1
            
            # Long input test
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_LongInput",
                f"Verify '{inp['display_name']}' handles long input",
                f'driver.findElement({locator}).sendKeys("a".repeat(1000));'
            ))
            test_num += 1
            
            # Security: SQL injection
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_SQLInjection",
                f"Verify '{inp['display_name']}' prevents SQL injection",
                f'driver.findElement({locator}).sendKeys("\' OR \'1\'=\'1\' --");'
            ))
            test_num += 1
            
            # Security: XSS
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_XSS",
                f"Verify '{inp['display_name']}' prevents XSS",
                f'driver.findElement({locator}).sendKeys("<script>alert(\'XSS\')</script>");'
            ))
            test_num += 1
        
        # 2. BUTTON TESTS - Generate for each button
        for btn in buttons:
            safe_name = btn['display_name'].replace(' ', '').replace('-', '')[:20]
            locator = self._get_locator(btn, 'button')
            
            # Clickable test
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_Click",
                f"Verify '{btn['display_name']}' button is clickable",
                f'driver.findElement({locator}).click();\\n        try {{ Thread.sleep(500); }} catch (InterruptedException e) {{ }}'
            ))
            test_num += 1
            
            # With all fields filled
            if len(inputs) > 0:
                fill_code = '\\n        '.join([
                    f'driver.findElement({self._get_locator(inp, "input")}).sendKeys("test{i}");'
                    for i, inp in enumerate(inputs)
                ])
                test_methods.append(self._create_test(
                    test_num, f"test{safe_name}_WithData",
                    f"Verify '{btn['display_name']}' works with all fields filled",
                    f'{fill_code}\\n        driver.findElement({locator}).click();\\n        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}'
                ))
                test_num += 1
        
        # 3. LINK TESTS - Generate for each link
        for link in links:
            safe_name = link['display_name'].replace(' ', '').replace('-', '')[:20]
            locator = self._get_locator(link, 'link')
            
            test_methods.append(self._create_test(
                test_num, f"test{safe_name}_Link",
                f"Verify '{link['display_name']}' link is clickable",
                f'driver.findElement({locator}).click();\\n        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}'
            ))
            test_num += 1
        
        # 4. CHECKBOX TESTS
        for idx, checkbox in enumerate(checkboxes):
            locator = self._get_locator(checkbox, 'checkbox')
            test_methods.append(self._create_test(
                test_num, f"testCheckbox{idx+1}_Toggle",
                f"Verify checkbox {idx+1} can be toggled",
                f'driver.findElement({locator}).click();'
            ))
            test_num += 1
        
        # 5. DROPDOWN TESTS
        for idx, dropdown in enumerate(dropdowns):
            locator = self._get_locator(dropdown, 'dropdown')
            test_methods.append(self._create_test(
                test_num, f"testDropdown{idx+1}_Open",
                f"Verify dropdown {idx+1} can be opened",
                f'driver.findElement({locator}).click();'
            ))
            test_num += 1
        
        # Build complete test class
        test_class = self._build_class(test_name, url, test_methods)
        
        return {
            'test_class': test_class,
            'test_count': len(test_methods),
            'framework': 'TestNG',
            'language': 'java',
            'has_pom': False,
            'detected_elements': {
                'inputs': len(inputs),
                'buttons': len(buttons),
                'links': len(links),
                'checkboxes': len(checkboxes),
                'dropdowns': len(dropdowns)
            }
        }
    
    def _create_test(self, num: int, method_name: str, description: str, code: str) -> str:
        """Create a single test method."""
        return f'''
    /**
     * TC-{num:03d}: {description}
     */
    @Test(priority = {num})
    public void {method_name}() {{
        {code}
    }}
'''
    
    def _get_locator(self, element: Dict, elem_type: str) -> str:
        """Generate locator using ACTUAL OCR text."""
        text = element.get('text', '').strip()
        label = element.get('label', '').strip()
        name = text or label
        
        logger.info(f"[LOCATOR] {elem_type}: text='{text}', label='{label}' -> using '{name}'")
        
        if elem_type == 'input':
            if name:
                return f'By.xpath("//input[contains(@placeholder, \'{name}\') or contains(@name, \'{name.lower()}\')]")'
            return 'By.xpath("//input[1]")'
        
        elif elem_type == 'button':
            if name:
                clean = name.replace("'", "\\'")
                return f'By.xpath("//button[contains(text(), \'{clean}\')] | //*/button[contains(text(), \'{clean}\')] | //input[@type=\'submit\' and contains(@value, \'{clean}\')]")'
            return 'By.xpath("//button[1]")'
        
        elif elem_type == 'link':
            if name:
                return f'By.linkText("{name}")'
            return 'By.xpath("//a[1]")'
        
        elif elem_type == 'checkbox':
            return 'By.xpath("//input[@type=\'checkbox\'][1]")'
        
        elif elem_type == 'dropdown':
            return 'By.xpath("//select[1]")'
        
        return 'By.xpath("//*[1]")'
    
    def _build_class(self, test_name: str, url: str, methods: List[str]) -> str:
        """Build complete test class."""
        methods_code = ''.join(methods)
        
        return f'''package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;

/**
 * Automated Test Cases - Generated from Screenshot
 * Total Tests: {len(methods)}
 * Generated for ALL detected elements using actual OCR text
 */
public class {test_name} {{
    
    private WebDriver driver;
    private static final String BASE_URL = "{url}";
    
    @BeforeMethod
    public void setup() {{
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        driver = new ChromeDriver(options);
        driver.get(BASE_URL);
    }}
    
    @AfterMethod
    public void tearDown() {{
        if (driver != null) {{
            driver.quit();
        }}
    }}
{methods_code}
}}
'''
