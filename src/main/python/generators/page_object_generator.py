"""
Page Object Model Generator
Automatically generates POM classes from screenshot analysis
Supports both Java and Python implementations
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PageObjectGenerator:
    """Generates Page Object Model classes from detected elements."""
    
    def __init__(self):
        """Initialize POM generator."""
        self.class_name_counter = {}
        
    def generate_pom(self, elements: Dict, page_name: str, language: str = 'java') -> str:
        """
        Generate Page Object Model class.
        
        Args:
            elements: Detected elements with locators
            page_name: Name of the page (e.g., 'Login', 'Registration')
            language: Target language ('java' or 'python')
            
        Returns:
            Generated POM class code
        """
        if language.lower() == 'java':
            return self._generate_java_pom(elements, page_name)
        elif language.lower() == 'python':
            return self._generate_python_pom(elements, page_name)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _generate_java_pom(self, elements: Dict, page_name: str) -> str:
        """Generate Java POM class."""
        class_name = self._to_class_name(page_name) + "Page"
        
        logger.info(f"[POM] Generating Java POM for {page_name}")
        logger.info(f"[POM] Elements received - Buttons: {len(elements.get('buttons', []))}, Inputs: {len(elements.get('inputs', []))}")
        
        # Collect all elements
        all_elements = []
        all_elements.extend(elements.get('buttons', []))
        all_elements.extend(elements.get('inputs', []))
        all_elements.extend(elements.get('text_regions', []))
        
        logger.info(f"[POM] Total elements to process: {len(all_elements)}")
        
        # Check if we have any elements
        if not all_elements:
            logger.warning("[POM] No elements to generate POM from")
            return f"""// No elements detected in the screenshot.
// Please ensure:
// 1. Screenshot contains visible UI elements
// 2. OCR is enabled for better detection
// 3. Image quality is good (clear buttons/inputs)

// Detected elements: {len(elements.get('buttons', []))} buttons, {len(elements.get('inputs', []))} inputs
"""
        
        # Generate element declarations
        element_declarations = []
        element_methods = []
        
        for idx, elem in enumerate(all_elements):
            element_name = self._generate_element_name(elem, idx)
            
            # Get locator from primary_locator or locator_strategies
            locator_type = 'id'
            locator_value = f'element-{idx}'
            
            if elem.get('primary_locator'):
                primary = elem['primary_locator']
                locator_type = primary.get('type', 'id')
                locator_value = primary.get('value', f'element-{idx}')
            elif elem.get('locator_strategies') and len(elem['locator_strategies']) > 0:
                first_strategy = elem['locator_strategies'][0]
                locator_type = first_strategy.get('type', 'id')
                locator_value = first_strategy.get('value', f'element-{idx}')
            elif elem.get('locator_info'):
                locator_info = elem['locator_info']
                locator_type = locator_info.get('type', 'id')
                locator_value = locator_info.get('value', f'element-{idx}')
            
            find_by = self._get_java_findby(locator_type, locator_value)
            
            element_declarations.append(f"    {find_by}")
            element_declarations.append(f"    private WebElement {element_name};")
            element_declarations.append("")
            
            # Generate interaction methods
            elem_type = elem.get('type', 'unknown')
            if elem_type in ['input', 'text_field', 'textarea']:
                element_methods.append(self._java_input_method(element_name, elem))
            elif elem_type == 'button':
                element_methods.append(self._java_click_method(element_name, elem))
        
        # Build complete class
        code = f"""package com.testing.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;

/**
 * Page Object Model for {page_name}
 * Auto-generated from screenshot analysis
 */
public class {class_name} {{
    
    private WebDriver driver;
    private WebDriverWait wait;
    
    // Page Elements
{chr(10).join(element_declarations)}
    
    // Constructor
    public {class_name}(WebDriver driver) {{
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        PageFactory.initElements(driver, this);
    }}
    
    // Page Methods
{chr(10).join(element_methods)}
    
    // Utility Methods
    public boolean isPageLoaded() {{
        try {{
            // Wait for first element to be visible
            return true;
        }} catch (Exception e) {{
            return false;
        }}
    }}
    
    public String getPageTitle() {{
        return driver.getTitle();
    }}
}}
"""
        logger.info(f"[POM] Java POM generated successfully - {len(code)} characters")
        return code
    
    def _generate_python_pom(self, elements: Dict, page_name: str) -> str:
        """Generate Python POM class."""
        class_name = self._to_class_name(page_name) + "Page"
        
        # Collect all elements
        all_elements = []
        all_elements.extend(elements.get('buttons', []))
        all_elements.extend(elements.get('inputs', []))
        all_elements.extend(elements.get('text_regions', []))
        
        # Check if we have any elements
        if not all_elements:
            return f"""# No elements detected in the screenshot.
# Please ensure:
# 1. Screenshot contains visible UI elements
# 2. OCR is enabled for better detection
# 3. Image quality is good (clear buttons/inputs)

# Detected elements: {len(elements.get('buttons', []))} buttons, {len(elements.get('inputs', []))} inputs
"""
        
        # Generate locator constants
        locator_constants = []
        element_properties = []
        element_methods = []
        
        for idx, elem in enumerate(all_elements):
            element_name = self._generate_element_name(elem, idx)
            
            # Get locator from primary_locator or locator_strategies
            locator_type = 'ID'
            locator_value = f'element-{idx}'
            
            if elem.get('primary_locator'):
                primary = elem['primary_locator']
                locator_type = primary.get('type', 'id').upper()
                locator_value = primary.get('value', f'element-{idx}')
            elif elem.get('locator_strategies') and len(elem['locator_strategies']) > 0:
                first_strategy = elem['locator_strategies'][0]
                locator_type = first_strategy.get('type', 'id').upper()
                locator_value = first_strategy.get('value', f'element-{idx}')
            elif elem.get('locator_info'):
                locator_info = elem['locator_info']
                locator_type = locator_info.get('type', 'ID').upper()
                locator_value = locator_info.get('value', f'element-{idx}')
            
            # Locator tuple
            const_name = element_name.upper() + "_LOCATOR"
            locator_constants.append(f'    {const_name} = (By.{locator_type}, "{locator_value}")')
            
            # Property for element
            element_properties.append(f"""    @property
    def {element_name}(self):
        \"\"\"Get {elem.get('text', element_name)} element\"\"\"
        return self.wait.until(EC.visibility_of_element_located(self.{const_name}))""")
            
            # Interaction methods
            elem_type = elem.get('type', 'unknown')
            if elem_type in ['input', 'text_field', 'textarea']:
                element_methods.append(self._python_input_method(element_name, elem))
            elif elem_type == 'button':
                element_methods.append(self._python_click_method(element_name, elem))
        
        # Build complete class
        code = f"""from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class {class_name}:
    \"\"\"
    Page Object Model for {page_name}
    Auto-generated from screenshot analysis
    \"\"\"
    
    # Locators
{chr(10).join(locator_constants)}
    
    def __init__(self, driver):
        \"\"\"Initialize page object with WebDriver instance\"\"\"
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    # Element Properties
{chr(10).join(element_properties)}
    
    # Page Actions
{chr(10).join(element_methods)}
    
    def is_page_loaded(self):
        \"\"\"Check if page is fully loaded\"\"\"
        try:
            self.{self._generate_element_name(all_elements[0], 0) if all_elements else 'page_element'}
            return True
        except TimeoutException:
            return False
    
    def get_page_title(self):
        \"\"\"Get current page title\"\"\"
        return self.driver.title
"""
        return code
    
    def _get_java_findby(self, locator_type: str, value: str) -> str:
        """Generate Java @FindBy annotation."""
        type_map = {
            'id': 'id',
            'name': 'name',
            'css': 'css',
            'xpath': 'xpath',
            'class': 'className',
            'tag': 'tagName'
        }
        
        find_type = type_map.get(locator_type.lower(), 'id')
        return f'@FindBy({find_type} = "{value}")'
    
    def _java_input_method(self, element_name: str, elem: Dict) -> str:
        """Generate Java input method."""
        method_name = "enter" + self._to_class_name(element_name)
        text_hint = elem.get('text', element_name.replace('_', ' '))
        
        return f"""    public {self._to_class_name(elem.get('text', 'element'))}Page {method_name}(String value) {{
        wait.until(ExpectedConditions.visibilityOf({element_name}));
        {element_name}.clear();
        {element_name}.sendKeys(value);
        return this;
    }}
"""
    
    def _java_click_method(self, element_name: str, elem: Dict) -> str:
        """Generate Java click method."""
        method_name = "click" + self._to_class_name(element_name)
        
        return f"""    public void {method_name}() {{
        wait.until(ExpectedConditions.elementToBeClickable({element_name}));
        {element_name}.click();
    }}
"""
    
    def _python_input_method(self, element_name: str, elem: Dict) -> str:
        """Generate Python input method."""
        method_name = f"enter_{element_name}"
        
        return f"""    def {method_name}(self, value):
        \"\"\"Enter text into {elem.get('text', element_name)}\"\"\"
        element = self.{element_name}
        element.clear()
        element.send_keys(value)
        return self
"""
    
    def _python_click_method(self, element_name: str, elem: Dict) -> str:
        """Generate Python click method."""
        method_name = f"click_{element_name}"
        
        return f"""    def {method_name}(self):
        \"\"\"Click {elem.get('text', element_name)}\"\"\"
        element = self.wait.until(EC.element_to_be_clickable(self.{element_name.upper()}_LOCATOR))
        element.click()
        return self
"""
    
    def _generate_element_name(self, elem: Dict, index: int) -> str:
        """Generate variable name for element."""
        # Priority 1: Use suggested_name (from smart locator generation)
        if elem.get('suggested_name'):
            name = elem['suggested_name']
            # Clean up the name
            name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            name = re.sub(r'_+', '_', name).strip('_')
            if name and not name[0].isdigit():
                return name
        
        # Priority 2: Use text from OCR
        text = elem.get('text', '').strip()
        if text:
            name = re.sub(r'[^a-zA-Z0-9]', '_', text.lower())
            name = re.sub(r'_+', '_', name).strip('_')
            if name:
                if name[0].isdigit():
                    name = 'elem_' + name
                return name
        
        # Priority 3: Use label for inputs
        label = elem.get('label', '').strip()
        if label:
            name = re.sub(r'[^a-zA-Z0-9]', '_', label.lower())
            name = re.sub(r'_+', '_', name).strip('_')
            if name and not name[0].isdigit():
                return name + '_field'
        
        # Fallback to type-based naming
        elem_type = elem.get('type', 'element')
        return f"{elem_type}_{index}"
    
    def _to_class_name(self, text: str) -> str:
        """Convert text to PascalCase class name."""
        # Remove special characters
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Split by spaces and capitalize
        words = clean.split()
        return ''.join(word.capitalize() for word in words if word)
    
    def generate_test_class(self, pom_class_name: str, test_scenario: str, 
                          language: str = 'java') -> str:
        """
        Generate test class using the POM.
        
        Args:
            pom_class_name: Name of POM class
            test_scenario: Test scenario description
            language: Target language
            
        Returns:
            Generated test class
        """
        if language.lower() == 'java':
            return self._generate_java_test(pom_class_name, test_scenario)
        else:
            return self._generate_python_test(pom_class_name, test_scenario)
    
    def _generate_java_test(self, pom_class: str, scenario: str) -> str:
        """Generate Java test class."""
        test_class = pom_class.replace('Page', 'Test')
        
        return f"""package com.testing.tests;

import com.testing.pages.{pom_class};
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.*;
import org.testng.Assert;

public class {test_class} {{
    
    private WebDriver driver;
    private {pom_class} page;
    
    @BeforeMethod
    public void setUp() {{
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        page = new {pom_class}(driver);
    }}
    
    @Test
    public void test{scenario.replace(' ', '')}() {{
        // Navigate to page
        driver.get("YOUR_PAGE_URL_HERE");
        
        // Verify page loaded
        Assert.assertTrue(page.isPageLoaded(), "Page should be loaded");
        
        // TODO: Add test steps based on scenario: {scenario}
    }}
    
    @AfterMethod
    public void tearDown() {{
        if (driver != null) {{
            driver.quit();
        }}
    }}
}}
"""
    
    def _generate_python_test(self, pom_class: str, scenario: str) -> str:
        """Generate Python test class."""
        test_class = pom_class.replace('Page', 'Test')
        module_name = self._to_snake_case(pom_class)
        
        return f"""import pytest
from selenium import webdriver
from pages.{module_name} import {pom_class}

class {test_class}:
    \"\"\"Test cases for {pom_class}\"\"\"
    
    @pytest.fixture(autouse=True)
    def setup(self):
        \"\"\"Setup before each test\"\"\"
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.page = {pom_class}(self.driver)
        yield
        self.driver.quit()
    
    def test_{self._to_snake_case(scenario)}(self):
        \"\"\"Test: {scenario}\"\"\"
        # Navigate to page
        self.driver.get("YOUR_PAGE_URL_HERE")
        
        # Verify page loaded
        assert self.page.is_page_loaded(), "Page should be loaded"
        
        # TODO: Add test steps based on scenario: {scenario}
"""
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        # Insert underscore before capital letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # Insert underscore before capital letters preceded by lowercase
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()
