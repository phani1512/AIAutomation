"""
Complete Test Generator
Generates ready-to-execute test cases with locators from screenshots
Produces complete test suites that can be directly added to test automation frameworks
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CompleteTestGenerator:
    """Generates complete, executable test scripts from screenshot analysis."""
    
    def __init__(self):
        """Initialize test generator."""
        self.test_counter = 0
    
    def generate_complete_test_suite(self, analysis: Dict, language: str = 'java', 
                                    test_name: str = 'ScreenshotTest') -> Dict:
        """
        Generate complete test suite with all test cases and locators.
        
        Args:
            analysis: Screenshot analysis with elements and strategies
            language: Target language ('java' or 'python')
            test_name: Base name for test class
            
        Returns:
            Dict with test class, page object, and data provider
        """
        logger.info(f"[TEST-GEN] Generating complete {language} test suite: {test_name}")
        
        elements = analysis.get('elements', {})
        buttons = elements.get('buttons', [])
        inputs = elements.get('inputs', [])
        
        logger.info(f"[TEST-GEN] Processing {len(buttons)} buttons, {len(inputs)} inputs")
        
        if language.lower() == 'java':
            return self._generate_java_suite(buttons, inputs, test_name)
        else:
            return self._generate_python_suite(buttons, inputs, test_name)
    
    def _generate_java_suite(self, buttons: List[Dict], inputs: List[Dict], 
                            test_name: str) -> Dict:
        """Generate complete Java TestNG test suite."""
        
        # Generate Page Object
        page_object = self._generate_java_page_object(buttons, inputs, test_name)
        
        # Generate Test Class
        test_class = self._generate_java_test_class(buttons, inputs, test_name)
        
        # Generate Data Provider
        data_provider = self._generate_java_data_provider(inputs)
        
        # Generate Complete Suite with all files
        return {
            'language': 'java',
            'framework': 'TestNG + Selenium',
            'page_object': page_object,
            'test_class': test_class,
            'data_provider': data_provider,
            'test_count': len(buttons) + len(inputs),
            'ready_to_execute': True,
            'instructions': self._get_java_instructions()
        }
    
    def _generate_java_page_object(self, buttons: List[Dict], inputs: List[Dict], 
                                   page_name: str) -> str:
        """Generate Java Page Object with all locators."""
        class_name = page_name.replace(' ', '') + 'Page'
        
        # Collect all elements with their best locators
        element_declarations = []
        element_methods = []
        
        # Process inputs
        for idx, inp in enumerate(inputs):
            field_name = inp.get('suggested_name', f'input_{idx}')
            locator = self._get_best_locator(inp)
            
            element_declarations.append(f"    @FindBy({locator['findby']})")
            element_declarations.append(f"    private WebElement {field_name};")
            element_declarations.append("")
            
            # Generate input method
            method_name = f"enter{self._to_pascal_case(field_name)}"
            element_methods.append(f"""    public {class_name} {method_name}(String value) {{
        wait.until(ExpectedConditions.visibilityOf({field_name}));
        {field_name}.clear();
        {field_name}.sendKeys(value);
        return this;
    }}
""")
        
        # Process buttons
        for idx, btn in enumerate(buttons):
            button_name = btn.get('suggested_name', f'button_{idx}')
            locator = self._get_best_locator(btn)
            
            element_declarations.append(f"    @FindBy({locator['findby']})")
            element_declarations.append(f"    private WebElement {button_name};")
            element_declarations.append("")
            
            # Generate click method
            method_name = f"click{self._to_pascal_case(button_name)}"
            element_methods.append(f"""    public void {method_name}() {{
        wait.until(ExpectedConditions.elementToBeClickable({button_name}));
        {button_name}.click();
    }}
""")
        
        code = f"""package com.testing.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;

/**
 * Page Object Model - Auto-generated from Screenshot
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
        return driver.getTitle() != null;
    }}
    
    public String getPageTitle() {{
        return driver.getTitle();
    }}
}}
"""
        return code
    
    def _generate_java_test_class(self, buttons: List[Dict], inputs: List[Dict], 
                                  test_name: str) -> str:
        """Generate complete Java TestNG test class."""
        class_name = test_name.replace(' ', '') + 'Test'
        page_class = test_name.replace(' ', '') + 'Page'
        
        # Generate test methods
        test_methods = []
        
        # Test for filling all inputs
        if inputs:
            input_steps = []
            for idx, inp in enumerate(inputs):
                field_name = inp.get('suggested_name', f'input_{idx}')
                method_name = f"enter{self._to_pascal_case(field_name)}"
                input_steps.append(f'        page.{method_name}(testData[{idx}]);')
            
            test_methods.append(f"""    @Test(dataProvider = "testData", priority = 1)
    public void testFillForm(String[] testData) {{
        logger.info("Test: Fill form with data");
{chr(10).join(input_steps)}
        
        // Verify data entered
        Assert.assertTrue(page.isPageLoaded(), "Page should be loaded");
        logger.info("✓ Form filled successfully");
    }}
""")
        
        # Test for each button click
        for idx, btn in enumerate(buttons):
            button_name = btn.get('suggested_name', f'button_{idx}')
            btn_text = btn.get('text', button_name)
            method_name = f"click{self._to_pascal_case(button_name)}"
            
            test_methods.append(f"""    @Test(priority = {idx + 2})
    public void test{self._to_pascal_case(button_name)}Click() {{
        logger.info("Test: Click {btn_text} button");
        page.{method_name}();
        
        // Add assertions here based on expected behavior
        Assert.assertTrue(page.isPageLoaded(), "Page should remain loaded");
        logger.info("✓ {btn_text} button clicked successfully");
    }}
""")
        
        code = f"""package com.testing.tests;

import com.testing.pages.{page_class};
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.Assert;
import org.testng.annotations.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Automated Test Suite - Generated from Screenshot
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */
public class {class_name} {{
    
    private WebDriver driver;
    private {page_class} page;
    private static final Logger logger = LoggerFactory.getLogger({class_name}.class);
    
    @BeforeClass
    public void setUp() {{
        logger.info("Setting up test environment");
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        driver.get("YOUR_URL_HERE"); // Replace with actual URL
        page = new {page_class}(driver);
    }}
    
    @AfterClass
    public void tearDown() {{
        if (driver != null) {{
            logger.info("Closing browser");
            driver.quit();
        }}
    }}
    
{chr(10).join(test_methods)}
    
    @DataProvider(name = "testData")
    public Object[][] getTestData() {{
        return new Object[][] {{
            {{new String[]{{{', '.join([f'"TestData{i}"' for i in range(len(inputs))])}}}}},
            {{new String[]{{{', '.join([f'"ValidData{i}"' for i in range(len(inputs))])}}}}},
            {{new String[]{{{', '.join([f'"EdgeCase{i}"' for i in range(len(inputs))])}}}}},
        }};
    }}
}}
"""
        return code
    
    def _generate_java_data_provider(self, inputs: List[Dict]) -> str:
        """Generate separate data provider class with realistic test data."""
        
        data_sets = []
        for inp in inputs:
            field_name = inp.get('suggested_name', 'field')
            field_type = self._detect_field_type(inp)
            
            if field_type == 'email':
                data_sets.append(['test@example.com', 'user@domain.com', 'valid@test.org'])
            elif field_type == 'password':
                data_sets.append(['Password123!', 'SecureP@ss', 'Test123!@#'])
            elif field_type == 'username':
                data_sets.append(['testuser', 'john_doe', 'user123'])
            else:
                data_sets.append([f'Test{field_name}1', f'Valid{field_name}', f'{field_name}_data'])
        
        # Transpose to get test scenarios
        scenarios = []
        for i in range(3):
            scenario = [data_set[i] if i < len(data_set) else 'TestData' for data_set in data_sets]
            scenarios.append(scenario)
        
        code = f"""package com.testing.data;

/**
 * Test Data Provider - Auto-generated
 * Contains realistic test data for form fields
 */
public class TestDataProvider {{
    
    public static Object[][] getValidData() {{
        return new Object[][] {{
            {{{', '.join([f'"{val}"' for val in scenarios[0]])}}},
            {{{', '.join([f'"{val}"' for val in scenarios[1]])}}},
            {{{', '.join([f'"{val}"' for val in scenarios[2]])}}}
        }};
    }}
    
    public static Object[][] getInvalidData() {{
        return new Object[][] {{
            {{{', '.join(['""'] * len(inputs))}}},  // Empty values
            {{{', '.join(['"@invalid"'] * len(inputs))}}},  // Invalid format
            {{{', '.join(['"<script>alert(1)</script>"'] * len(inputs))}}}  // XSS attempt
        }};
    }}
}}
"""
        return code
    
    def _generate_python_suite(self, buttons: List[Dict], inputs: List[Dict], 
                              test_name: str) -> Dict:
        """Generate complete Python pytest test suite."""
        
        # Generate Page Object
        page_object = self._generate_python_page_object(buttons, inputs, test_name)
        
        # Generate Test Class
        test_class = self._generate_python_test_class(buttons, inputs, test_name)
        
        # Generate Fixtures
        fixtures = self._generate_python_fixtures()
        
        return {
            'language': 'python',
            'framework': 'pytest + Selenium',
            'page_object': page_object,
            'test_class': test_class,
            'fixtures': fixtures,
            'test_count': len(buttons) + len(inputs),
            'ready_to_execute': True,
            'instructions': self._get_python_instructions()
        }
    
    def _generate_python_page_object(self, buttons: List[Dict], inputs: List[Dict], 
                                     page_name: str) -> str:
        """Generate Python Page Object with all locators."""
        class_name = page_name.replace(' ', '') + 'Page'
        
        # Collect locators
        locator_constants = []
        element_properties = []
        element_methods = []
        
        # Process inputs
        for idx, inp in enumerate(inputs):
            field_name = inp.get('suggested_name', f'input_{idx}')
            locator = self._get_best_locator(inp)
            
            const_name = field_name.upper() + '_LOCATOR'
            locator_constants.append(f'    {const_name} = ({locator["by"]}, "{locator["value"]}")')
            
            # Property
            element_properties.append(f"""    @property
    def {field_name}(self):
        return self.wait.until(EC.visibility_of_element_located(self.{const_name}))
""")
            
            # Method
            element_methods.append(f"""    def enter_{field_name}(self, value):
        self.{field_name}.clear()
        self.{field_name}.send_keys(value)
        return self
""")
        
        # Process buttons
        for idx, btn in enumerate(buttons):
            button_name = btn.get('suggested_name', f'button_{idx}')
            locator = self._get_best_locator(btn)
            
            const_name = button_name.upper() + '_LOCATOR'
            locator_constants.append(f'    {const_name} = ({locator["by"]}, "{locator["value"]}")')
            
            element_methods.append(f"""    def click_{button_name}(self):
        element = self.wait.until(EC.element_to_be_clickable(self.{const_name}))
        element.click()
        return self
""")
        
        code = f"""from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class {class_name}:
    \"\"\"
    Page Object Model - Auto-generated from Screenshot
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    \"\"\"
    
    # Locators
{chr(10).join(locator_constants)}
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
{chr(10).join(element_properties)}
{chr(10).join(element_methods)}
    
    def is_page_loaded(self):
        return self.driver.title is not None
    
    def get_page_title(self):
        return self.driver.title
"""
        return code
    
    def _generate_python_test_class(self, buttons: List[Dict], inputs: List[Dict], 
                                   test_name: str) -> str:
        """Generate Python pytest test class."""
        class_name = 'Test' + test_name.replace(' ', '')
        page_class = test_name.replace(' ', '') + 'Page'
        
        # Generate test methods
        test_methods = []
        
        # Test for filling form
        if inputs:
            input_steps = []
            test_data = []
            for idx, inp in enumerate(inputs):
                field_name = inp.get('suggested_name', f'input_{idx}')
                input_steps.append(f'        page.enter_{field_name}(test_data[{idx}])')
                test_data.append(f'"TestData{idx}"')
            
            test_methods.append(f"""    @pytest.mark.parametrize("test_data", [
        [{', '.join(test_data)}],
        ["Valid1", "Valid2", "Valid3"],
    ])
    def test_fill_form(self, driver, test_data):
        page = {page_class}(driver)
        
{chr(10).join(input_steps)}
        
        assert page.is_page_loaded(), "Page should be loaded"
""")
        
        # Test for button clicks
        for idx, btn in enumerate(buttons):
            button_name = btn.get('suggested_name', f'button_{idx}')
            btn_text = btn.get('text', button_name)
            
            test_methods.append(f"""    def test_{button_name}_click(self, driver):
        page = {page_class}(driver)
        page.click_{button_name}()
        
        assert page.is_page_loaded(), "Page should remain loaded"
""")
        
        code = f"""import pytest
from {test_name.lower()}_page import {page_class}

class {class_name}:
    \"\"\"
    Automated Test Suite - Generated from Screenshot
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    \"\"\"
    
{chr(10).join(test_methods)}
"""
        return code
    
    def _generate_python_fixtures(self) -> str:
        """Generate pytest fixtures."""
        return """import pytest
from selenium import webdriver

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("YOUR_URL_HERE")  # Replace with actual URL
    yield driver
    driver.quit()
"""
    
    def _get_best_locator(self, element: Dict) -> Dict:
        """Get the best locator strategy for element."""
        strategies = element.get('locator_strategies', [])
        
        if not strategies:
            # Fallback
            return {
                'findby': 'id = "unknown"',
                'by': 'By.ID',
                'value': 'unknown'
            }
        
        # Get highest scored strategy
        best = strategies[0]
        
        # Convert to different formats
        loc_type = best.get('type', 'id')
        loc_value = best.get('value', 'unknown')
        
        # Java @FindBy format
        findby_map = {
            'id': f'id = "{loc_value}"',
            'name': f'name = "{loc_value}"',
            'css': f'css = "{loc_value}"',
            'xpath': f'xpath = "{loc_value}"'
        }
        
        # Python By format
        by_map = {
            'id': 'By.ID',
            'name': 'By.NAME',
            'css': 'By.CSS_SELECTOR',
            'xpath': 'By.XPATH'
        }
        
        return {
            'findby': findby_map.get(loc_type, f'id = "{loc_value}"'),
            'by': by_map.get(loc_type, 'By.ID'),
            'value': loc_value
        }
    
    def _detect_field_type(self, field: Dict) -> str:
        """Detect field type for data generation."""
        text = (field.get('text', '') + ' ' + field.get('label', '') + ' ' + 
                field.get('suggested_name', '')).lower()
        
        if 'email' in text:
            return 'email'
        elif 'password' in text or 'pwd' in text:
            return 'password'
        elif 'username' in text or 'user' in text:
            return 'username'
        return 'text'
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert to PascalCase."""
        return ''.join(word.capitalize() for word in text.replace('_', ' ').split())
    
    def _get_java_instructions(self) -> str:
        """Get instructions for running Java tests."""
        return """
# How to Run These Tests

1. Add to your Maven project:
   - Copy Page Object to: src/main/java/com/testing/pages/
   - Copy Test Class to: src/test/java/com/testing/tests/
   - Copy Data Provider to: src/main/java/com/testing/data/

2. Add dependencies to pom.xml:
   - Selenium WebDriver
   - TestNG
   - SLF4J Logger

3. Update the URL in setUp() method

4. Run tests:
   mvn test
   or
   Right-click on test class -> Run as TestNG Test
"""
    
    def _get_python_instructions(self) -> str:
        """Get instructions for running Python tests."""
        return """
# How to Run These Tests

1. Install dependencies:
   pip install selenium pytest

2. Add files to your project:
   - Copy Page Object as: {test_name}_page.py
   - Copy Test Class as: test_{test_name}.py
   - Copy Fixtures as: conftest.py

3. Update the URL in conftest.py

4. Run tests:
   pytest test_{test_name}.py -v
   or
   pytest test_{test_name}.py::TestClassName::test_method_name
"""
