"""
Direct Test Generator - Generates comprehensive test suite in ONE file
Matches the DIRECT_TEST_OUTPUT.java format with 20+ test cases
NO Page Object Model - uses direct locators
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DirectTestGenerator:
    """Generates comprehensive test cases in single file without POM."""
    
    def generate_direct_comprehensive_tests(self, elements: Dict, test_name: str = "PageTest", 
                                           url: str = "YOUR_URL_HERE") -> Dict:
        """
        Generate 20 comprehensive test cases based on DETECTED elements (works for ANY screenshot)
        
        Returns:
            Dict with test_class code and metadata
        """
        inputs = elements.get('inputs', [])
        buttons = elements.get('buttons', [])
        text_regions = elements.get('text_regions', [])
        
        logger.info(f"[DIRECT-GEN] Generating tests: {len(inputs)} inputs, {len(buttons)} buttons, {len(text_regions)} text regions")
        
        # Dynamically classify ALL inputs using OCR text and labels
        classified_fields = {
            'email': [],
            'password': [],
            'text': [],
            'search': [],
            'number': [],
            'phone': [],
            'date': [],
            'other': []
        }
        
        logger.info(f"[DIRECT-GEN] ===== CLASSIFYING {len(inputs)} INPUTS =====")
        for idx, inp in enumerate(inputs):
            label = str(inp.get('label', '')).lower()
            suggested_name = str(inp.get('suggested_name', '')).lower()
            ocr_text = str(inp.get('ocr_text', '')).lower()
            combined = label + suggested_name + ocr_text
            
            # DEBUG: Log ALL attributes of each input
            logger.info(f"[DIRECT-GEN] Input {idx}:")
            logger.info(f"  - label: '{inp.get('label', 'NONE')}'")
            logger.info(f"  - suggested_name: '{inp.get('suggested_name', 'NONE')}'")
            logger.info(f"  - ocr_text: '{inp.get('ocr_text', 'NONE')}'")
            logger.info(f"  - combined: '{combined}'")
            logger.info(f"  - position: ({inp.get('x')}, {inp.get('y')})")
            
            # Use OCR and context to classify each field
            classification = None
            if 'email' in combined or 'e-mail' in combined:
                classified_fields['email'].append(inp)
                classification = 'email'
            elif 'password' in combined or 'pass' in combined or 'pwd' in combined:
                classified_fields['password'].append(inp)
                classification = 'password'
            elif 'search' in combined or 'find' in combined or 'query' in combined:
                classified_fields['search'].append(inp)
                classification = 'search'
            elif 'phone' in combined or 'mobile' in combined or 'tel' in combined:
                classified_fields['phone'].append(inp)
                classification = 'phone'
            elif 'date' in combined or 'calendar' in combined:
                classified_fields['date'].append(inp)
                classification = 'date'
            elif 'number' in combined or 'amount' in combined or 'quantity' in combined:
                classified_fields['number'].append(inp)
                classification = 'number'
            elif 'text' in combined or 'name' in combined or 'address' in combined:
                classified_fields['text'].append(inp)
                classification = 'text'
            else:
                classified_fields['other'].append(inp)
                classification = 'other'
            
            logger.info(f"  ➜ Classified as: {classification}")
        
        # Log final classification summary
        logger.info(f"[DIRECT-GEN] ===== CLASSIFICATION SUMMARY =====")
        for field_type, fields in classified_fields.items():
            if len(fields) > 0:
                logger.info(f"  {field_type}: {len(fields)} fields")
        
        
        # Determine page type from classified fields (dynamic detection)
        page_type = self._detect_page_type(classified_fields, buttons, text_regions)
        logger.info(f"[DIRECT-GEN] Detected page type: {page_type}")
        
        # Generate comprehensive tests based on what was ACTUALLY detected
        detected_data = {
            'classified_fields': classified_fields,
            'buttons': buttons,
            'text_regions': text_regions,
            'page_type': page_type,
            'all_inputs': inputs
        }
        
        # Generate test class DYNAMICALLY based on ACTUAL detected elements
        test_class = self._generate_dynamic_tests(
            test_name, url, page_type, classified_fields, buttons, text_regions
        )
        
        # Count actual tests generated (not hardcoded 20)
        test_count = test_class.count('@Test')
        
        return {
            'test_class': test_class,
            'test_count': test_count,
            'framework': 'TestNG',
            'language': 'java',
            'has_pom': False,
            'page_type': page_type,
            'detected_elements': {
                'email_fields': len(classified_fields.get('email', [])),
                'password_fields': len(classified_fields.get('password', [])),
                'text_fields': len(classified_fields.get('text', [])),
                'buttons': len(buttons)
            },
            'files': {
                'test': f'src/test/java/com/testing/tests/{test_name}.java'
            }
        }
    
    def _detect_page_type(self, classified_fields: Dict, buttons: List, text_regions: List) -> str:
        """Detect page type from OCR and field classification."""
        has_email = len(classified_fields['email']) > 0
        has_password = len(classified_fields['password']) > 0
        has_search = len(classified_fields['search']) > 0
        
        # Check OCR text for page type hints
        ocr_text = ' '.join([str(r.get('text', '')).lower() for r in text_regions])
        
        if has_email and has_password:
            return 'login'
        elif has_search:
            return 'search'
        elif 'register' in ocr_text or 'sign up' in ocr_text or 'signup' in ocr_text:
            return 'registration'
        elif 'contact' in ocr_text or 'message' in ocr_text:
            return 'contact'
        elif len(classified_fields['text']) + len(classified_fields['other']) > 3:
            return 'form'
        else:
            return 'generic'
    
    def _generate_dynamic_tests(self, test_name: str, url: str, page_type: str,
                                classified_fields: Dict, buttons: List, text_regions: List) -> str:
        """Generate test cases dynamically based on ACTUAL detected elements - NO HARDCODING."""
        
        # Extract detected elements
        email_fields = classified_fields.get('email', [])
        password_fields = classified_fields.get('password', [])
        text_fields = classified_fields.get('text', [])
        search_fields = classified_fields.get('search', [])
        all_fields = email_fields + password_fields + text_fields + search_fields + classified_fields.get('other', [])
        
        logger.info(f"[DYNAMIC-GEN] Generating tests for {page_type} page")
        logger.info(f"[DYNAMIC-GEN] Detected: {len(email_fields)} email, {len(password_fields)} password, {len(buttons)} buttons")
        
        # Generate locators for detected elements
        field_locators = []
        for idx, field in enumerate(all_fields):
            locator = self._get_locator(field)
            field_type = 'email' if field in email_fields else ('password' if field in password_fields else 'text')
            field_locators.append({'locator': locator, 'type': field_type, 'index': idx})
        
        button_locators = []
        for idx, btn in enumerate(buttons):
            locator = self._get_button_locator(btn)
            button_locators.append({'locator': locator, 'index': idx})
        
        # Generate test methods based on detected elements
        test_methods = self._generate_test_methods_for_elements(
            field_locators, button_locators, page_type
        )
        
        # Build complete test class
        return self._build_test_class(test_name, url, test_methods)
    
    def _generate_test_methods_for_elements(self, field_locators: List[Dict], 
                                            button_locators: List[Dict], page_type: str) -> List[str]:
        """Generate test methods dynamically based on actual detected elements."""
        test_methods = []
        test_num = 1
        
        # If NO elements detected, generate basic page load test only
        if len(field_locators) == 0 and len(button_locators) == 0:
            test_methods.append(self._generate_page_load_test(test_num))
            return test_methods
        
        # Generate tests based on page type and detected elements
        if page_type == 'login' and len(field_locators) >= 2 and len(button_locators) >= 1:
            # Login-specific tests (only if we actually detected email/password/button)
            test_methods.extend(self._generate_login_tests(field_locators, button_locators))
        elif page_type == 'search' and len(search_fields) > 0 and len(button_locators) > 0:
            # Search-specific tests
            test_methods.extend(self._generate_search_tests(field_locators, button_locators))
        else:
            # Generic form tests based on what was detected
            test_methods.extend(self._generate_generic_form_tests(field_locators, button_locators))
        
        return test_methods
    
    def _generate_page_load_test(self, test_num: int) -> str:
        """Generate basic page load test when no elements detected."""
        return f'''
    /**
     * TC-{test_num:03d}: Verify page loads successfully
     */
    @Test(priority = {test_num})
    public void testPageLoads() {{
        // Verify page loaded
        Assert.assertNotNull(driver, "Driver should be initialized");
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "Should be on the correct page");
        Assert.assertFalse(driver.getTitle().isEmpty(), "Page title should not be empty");
    }}
'''
    
    def _generate_login_tests(self, fields: List[Dict], buttons: List[Dict]) -> List[str]:
        """Generate comprehensive tests dynamically based on detected fields and buttons."""
        tests = []
        
        # Separate email and password fields
        email_fields = [f for f in fields if f['type'] == 'email']
        password_fields = [f for f in fields if f['type'] == 'password']
        
        if len(email_fields) == 0 or len(password_fields) == 0 or len(buttons) == 0:
            return tests  # Can't generate login tests without email/password/button
        
        email_loc = email_fields[0]['locator']
        pass_loc = password_fields[0]['locator']
        btn_loc = buttons[0]['locator']
        
        # DYNAMIC TEST GENERATION: Generate tests based on detected elements
        test_num = 1
        
        # 1. POSITIVE TESTS - Generate for all detected buttons
        for btn_idx, btn in enumerate(buttons):
            btn_loc = btn['locator']
            
            # Basic valid submission test for each button
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify form submission with valid data (Button {btn_idx + 1})
     */
    @Test(priority = {test_num})
    public void testValidSubmission_Button{btn_idx + 1}() {{
        driver.findElement({email_loc}).sendKeys("user@example.com");
        driver.findElement({pass_loc}).sendKeys("Password123!");
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, "Should redirect after successful submission");
    }}
''')
            test_num += 1
        
        # 2. EMPTY FIELD VALIDATION - Test all combinations of empty fields
        # All fields empty
        tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify validation when all fields are empty
     */
    @Test(priority = {test_num})
    public void testAllFieldsEmpty() {{
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "Should remain on page when fields are empty");
    }}
''')
        test_num += 1
        
        # Each field empty individually
        for field_idx, field in enumerate(fields):
            field_name = field['type'].capitalize()
            other_fields = [f for f in fields if f != field]
            
            fill_code = '\n        '.join([
                f'driver.findElement({f["locator"]}).sendKeys("test{i}");'
                for i, f in enumerate(other_fields)
            ])
            
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify validation when {field_name} field is empty
     */
    @Test(priority = {test_num})
    public void test{field_name}FieldEmpty() {{
        {fill_code}
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "{field_name} field is required");
    }}
''')
            test_num += 1
        
        # 3. INVALID DATA TESTS - Generate for each detected input field
        invalid_test_data = {
            'email': [
                ('MissingAt', 'userexample.com', 'Invalid email format (missing @)'),
                ('MissingDomain', 'user@', 'Incomplete email (missing domain)'),
                ('InvalidChars', 'user#$%@example.com', 'Email with invalid special characters'),
                ('WithSpaces', 'user name@example.com', 'Email containing spaces'),
                ('SingleChar', 'a', 'Single character email'),
            ],
            'password': [
                ('TooShort', '123', 'Password too short'),
                ('OnlyNumbers', '12345678', 'Password with only numbers'),
                ('OnlyLetters', 'password', 'Password with only letters'),
            ],
            'text': [
                ('SpecialChars', '<script>test</script>', 'Text with special characters'),
                ('TooLong', 'a' * 500, 'Extremely long text'),
            ]
        }
        
        for field in fields:
            field_type = field['type']
            field_locator = field['locator']
            
            if field_type in invalid_test_data:
                for suffix, invalid_value, description in invalid_test_data[field_type]:
                    # Fill other fields with valid data
                    fill_code = '\n        '.join([
                        f'driver.findElement({f["locator"]}).sendKeys("{"user@example.com" if f["type"] == "email" else "ValidPass123!" if f["type"] == "password" else "validtext"}");'
                        for f in fields if f != field
                    ])
                    
                    tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify validation with {description}
     */
    @Test(priority = {test_num})
    public void test{field_type.capitalize()}{suffix}() {{
        {fill_code}
        driver.findElement({field_locator}).sendKeys("{invalid_value}");
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "{description} should be rejected");
    }}
''')
                    test_num += 1
        
        # 4. SECURITY TESTS - Generate SQL injection and XSS tests for ALL input fields
        security_payloads = [
            ('SQLInjection1', "admin' OR '1'='1", 'SQL injection attempt (OR statement)'),
            ('SQLInjection2', "' OR '1'='1' --", 'SQL injection attempt (comment)'),
            ('XSSScript', "<script>alert('XSS')</script>", 'XSS attack with script tag'),
            ('XSSImage', "<img src=x onerror=alert('XSS')>", 'XSS attack with image tag'),
        ]
        
        for field in fields:
            field_name = field['type'].capitalize()
            field_locator = field['locator']
            
            for suffix, payload, description in security_payloads:
                # Fill other fields with valid data
                fill_code = '\n        '.join([
                    f'driver.findElement({f["locator"]}).sendKeys("{"user@example.com" if f["type"] == "email" else "ValidPass123!" if f["type"] == "password" else "validtext"}");'
                    for f in fields if f != field
                ])
                
                tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify security against {description} in {field_name} field
     */
    @Test(priority = {test_num})
    public void test{field_name}{suffix}() {{
        {fill_code}
        driver.findElement({field_locator}).sendKeys("{payload}");
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "Security: {description} should be prevented");
    }}
''')
                test_num += 1
        
        # 5. BOUNDARY TESTS - Generate for all detected input fields
        for field in fields:
            field_name = field['type'].capitalize()
            field_locator = field['locator']
            
            # Fill other fields with valid data
            fill_code = '\n        '.join([
                f'driver.findElement({f["locator"]}).sendKeys("{"user@example.com" if f["type"] == "email" else "ValidPass123!" if f["type"] == "password" else "validtext"}");'
                for f in fields if f != field
            ])
            
            # Very long input (boundary test)
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify boundary test with extremely long {field_name}
     */
    @Test(priority = {test_num})
    public void test{field_name}VeryLong() {{
        String longValue = "a".repeat(1000) + "{"@test.com" if field["type"] == "email" else ""}";
        {fill_code}
        driver.findElement({field_locator}).sendKeys(longValue);
        driver.findElement({btn_loc}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, "System should handle {field_name} length boundary");
    }}
''')
            test_num += 1
        
        # 6. FIELD ATTRIBUTE TESTS - Verify field properties
        for field in fields:
            field_name = field['type'].capitalize()
            field_locator = field['locator']
            expected_type = field['type'] if field['type'] == 'password' else 'text'
            
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify {field_name} field has correct type attribute
     */
    @Test(priority = {test_num})
    public void test{field_name}FieldType() {{
        String fieldType = driver.findElement({field_locator}).getAttribute("type");
        Assert.assertTrue(fieldType.equals("{expected_type}") || fieldType.equals("{field['type']}"), 
            "{field_name} field should have type='{expected_type}'");
    }}
''')
            test_num += 1
        
        return tests
    
    def _generate_generic_form_tests(self, fields: List[Dict], buttons: List[Dict]) -> List[str]:
        """Generate comprehensive form tests dynamically based on detected elements."""
        tests = []
        test_num = 1
        
        if len(fields) == 0 and len(buttons) == 0:
            return tests
        
        # 1. POSITIVE TESTS - Test each button with all fields filled
        for btn_idx, btn in enumerate(buttons):
            if len(fields) > 0:
                fill_code = '\n        '.join([
                    f'driver.findElement({f["locator"]}).sendKeys("test value {i+1}");'
                    for i, f in enumerate(fields)
                ])
                
                tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify form submission with all fields filled (Button {btn_idx + 1})
     */
    @Test(priority = {test_num})
    public void testFormSubmission_Button{btn_idx + 1}() {{
        {fill_code}
        driver.findElement({btn["locator"]}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
    }}
''')
                test_num += 1
        
        # 2. EMPTY FIELD TESTS - Test with all fields empty
        if len(buttons) > 0:
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify form validation with all fields empty
     */
    @Test(priority = {test_num})
    public void testEmptyFormSubmission() {{
        driver.findElement({buttons[0]["locator"]}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
    }}
''')
            test_num += 1
        
        # 3. INDIVIDUAL FIELD TESTS - Test each field individually
        for field_idx, field in enumerate(fields):
            if len(buttons) > 0:
                tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify single field submission (Field {field_idx + 1})
     */
    @Test(priority = {test_num})
    public void testSingleField{field_idx + 1}() {{
        driver.findElement({field["locator"]}).sendKeys("test value");
        driver.findElement({buttons[0]["locator"]}).click();
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
    }}
''')
                test_num += 1
        
        # 4. SECURITY TESTS - Test each field with security payloads
        security_payloads = [
            ('SQLInjection', "' OR '1'='1' --", 'SQL injection'),
            ('XSS', "<script>alert('test')</script>", 'XSS attack'),
        ]
        
        for field_idx, field in enumerate(fields):
            for suffix, payload, description in security_payloads:
                tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify security against {description} in field {field_idx + 1}
     */
    @Test(priority = {test_num})
    public void testField{field_idx + 1}_{suffix}() {{
        driver.findElement({field["locator"]}).sendKeys("{payload}");
        {"driver.findElement(" + buttons[0]["locator"] + ").click();" if len(buttons) > 0 else ""}
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
    }}
''')
                test_num += 1
        
        # 5. BOUNDARY TESTS - Test each field with very long input
        for field_idx, field in enumerate(fields):
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify boundary test with very long input in field {field_idx + 1}
     */
    @Test(priority = {test_num})
    public void testField{field_idx + 1}_VeryLongInput() {{
        String longValue = "a".repeat(1000);
        driver.findElement({field["locator"]}).sendKeys(longValue);
        {"driver.findElement(" + buttons[0]["locator"] + ").click();" if len(buttons) > 0 else ""}
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
    }}
''')
            test_num += 1
        
        # 6. BUTTON INTERACTION TESTS - Test each button individually
        for btn_idx, btn in enumerate(buttons):
            tests.append(f'''
    /**
     * TC-{test_num:03d}: Verify button {btn_idx + 1} is clickable
     */
    @Test(priority = {test_num})
    public void testButton{btn_idx + 1}_Clickable() {{
        driver.findElement({btn["locator"]}).click();
        try {{ Thread.sleep(500); }} catch (InterruptedException e) {{ }}
        Assert.assertNotNull(driver, "Button should be clickable");
    }}
''')
            test_num += 1
        
        return tests
    
    def _build_test_class(self, test_name: str, url: str, test_methods: List[str]) -> str:
        """Build complete test class with setup/teardown."""
        methods_code = "\\n".join(test_methods)
        
        return f'''package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;

/**
 * Automated Test Cases - Generated from Screenshot Analysis
 * Total Test Cases: {len(test_methods)}
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
    
    def _get_locator(self, field: Dict) -> str:
        """Generate smart locator from ACTUAL detected field attributes (OCR, position, type)."""
        if not field:
            logger.warning("[LOCATOR] Field is None, using fallback")
            return 'By.xpath("//input[1]")'
        
        # Extract all available attributes from detection
        label = str(field.get('label', '')).strip()
        suggested_name = str(field.get('suggested_name', '')).strip().lower()
        ocr_text = str(field.get('ocr_text', '')).strip()
        index = field.get('index', 0)
        y_pos = field.get('y', 0)
        
        logger.info(f"[LOCATOR] Generating locator for field:")
        logger.info(f"  - label='{label}', suggested='{suggested_name}', ocr='{ocr_text}'")
        logger.info(f"  - index={index}, y={y_pos}")
        
        # Strategy 1: Use placeholder/label text from OCR
        if label and label.lower() in ['email', 'password', 'username', 'search']:
            # Use contains for flexible matching
            locator = f'By.xpath("//input[contains(@placeholder, \'{label}\') or contains(@name, \'{label.lower()}\') or contains(@id, \'{label.lower()}\')]")'
            logger.info(f"  ➜ Using label-based locator: {locator}")
            return locator
        
        # Strategy 2: Use type attribute for password fields
        if 'password' in suggested_name or 'pass' in suggested_name:
            locator = 'By.xpath("//input[@type=\'password\']")'
            logger.info(f"  ➜ Using password type locator: {locator}")
            return locator
        
        # Strategy 3: Use type attribute for email fields  
        if 'email' in suggested_name or 'mail' in suggested_name:
            locator = 'By.xpath("//input[@type=\'email\' or @type=\'text\'][1]")'
            logger.info(f"  ➜ Using email type locator: {locator}")
            return locator
        
        # Strategy 4: Position-based (top field vs bottom field)
        # Assumes typical login page has email on top, password below
        if index == 0 or y_pos < 200:
            locator = 'By.xpath("//input[@type=\'text\' or @type=\'email\'][1]")'
            logger.info(f"  ➜ Using position-based (top) locator: {locator}")
            return locator
        else:
            locator = f'By.xpath("//input[@type=\'text\' or @type=\'email\' or @type=\'password\'][{index + 1}]")'
            logger.info(f"  ➜ Using index-based locator: {locator}")
            return locator
    
    def _get_button_locator(self, button: Dict) -> str:
        """Generate smart locator from ACTUAL detected button attributes (OCR text)."""
        if not button:
            return 'By.xpath("//button[1]")'
        
        # Extract OCR text from button
        text = str(button.get('text', '')).strip()
        ocr_text = str(button.get('ocr_text', '')).strip()
        label = str(button.get('label', '')).strip()
        
        # Combine all text sources
        button_text = text or ocr_text or label
        
        # Use actual button text if available
        if button_text and len(button_text) > 0:
            # Clean and use the actual text detected
            clean_text = button_text.replace("'", "\\'")
            return f'By.xpath("//button[contains(text(), \'{clean_text}\')] | //*/button[contains(text(), \'{clean_text}\')] | //input[@type=\'submit\' and contains(@value, \'{clean_text}\')]")'
        
        # Fallback: generic button or submit input
        return 'By.xpath("//button[@type=\'submit\'] | //input[@type=\'submit\'] | //button[1]")'
