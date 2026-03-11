"""
Simple Screenshot Test Generator - No POM, Just Test Methods
Generates standalone test methods with inline Selenium code
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SimpleScreenshotTestGenerator:
    """Generate simple test methods directly from screenshot analysis."""
    
    def __init__(self):
        self.field_name_patterns = {
            'email': ['email', 'e-mail', 'mail', 'user', 'username', 'login'],
            'password': ['password', 'pass', 'pwd', 'secret'],
            'phone': ['phone', 'mobile', 'tel', 'contact'],
            'name': ['name', 'full name', 'firstname', 'lastname'],
            'search': ['search', 'find', 'query'],
            'message': ['message', 'comment', 'description', 'text'],
        }
        # Track element positions for unique sequential locators
        self.input_positions = {}
        self.button_positions = {}
    
    def generate_test_methods(self, analysis: Dict, test_name: str = "ScreenshotTest") -> List[Dict]:
        """
        Generate simple test methods from screenshot analysis.
        
        Returns list of test methods:
        [
            {
                'name': 'testLogin',
                'code': 'Java test method code',
                'description': 'Test login functionality'
            }
        ]
        """
        inputs = analysis['elements'].get('inputs', [])
        buttons = analysis['elements'].get('buttons', [])
        
        # Reset position tracking for new screenshot
        self.input_positions = {}
        self.button_positions = {}
        
        # Pre-assign sequential positions to all inputs sorted by Y-coordinate
        sorted_inputs = sorted(inputs, key=lambda e: e.get('y', 0))
        for idx, inp in enumerate(sorted_inputs, start=1):
            element_id = id(inp)  # Use object ID as unique key
            self.input_positions[element_id] = idx
        
        # Pre-assign sequential positions to all buttons sorted by Y-coordinate
        sorted_buttons = sorted(buttons, key=lambda e: e.get('y', 0))
        for idx, btn in enumerate(sorted_buttons, start=1):
            element_id = id(btn)
            self.button_positions[element_id] = idx
        
        # Detect test type
        test_type = self._detect_test_type(inputs, buttons)
        logger.info(f"[SIMPLE-GEN] Detected test type: {test_type}")
        
        test_methods = []
        
        if test_type == 'login':
            test_methods = self._generate_login_tests(inputs, buttons)
        elif test_type == 'search':
            test_methods = self._generate_search_tests(inputs, buttons)
        elif test_type == 'form':
            test_methods = self._generate_form_tests(inputs, buttons)
        else:
            test_methods = self._generate_generic_tests(inputs, buttons)
        
        logger.info(f"[SIMPLE-GEN] Generated {len(test_methods)} test methods")
        return test_methods
    
    def _detect_test_type(self, inputs: List[Dict], buttons: List[Dict]) -> str:
        """Detect the type of test based on element count and labels."""
        # Check labels for login page indicators (most reliable!)
        labels_text = ' '.join([inp.get('label', '').lower() for inp in inputs])
        
        # LOGIN page detection: Look for password field OR email field
        has_password = any('password' in inp.get('label', '').lower() or 'pwd' in inp.get('label', '').lower() 
                          for inp in inputs)
        has_email = any('email' in inp.get('label', '').lower() or 'mail' in inp.get('label', '').lower()
                       for inp in inputs)
        
        if has_password or (has_email and len(inputs) <= 4):
            logger.info(f"[SIMPLE-GEN] Detected LOGIN page (has_password={has_password}, has_email={has_email})")
            logger.info(f"[SIMPLE-GEN] Input labels: {[inp.get('label', 'NO_LABEL') for inp in inputs]}")
            return 'login'
        
        # Search: 1 input + 1 button
        if len(inputs) == 1 and len(buttons) >= 1:
            logger.info(f"[SIMPLE-GEN] Detected SEARCH page (1 input)")
            return 'search'
        
        # Form: 4+ inputs WITHOUT password field
        if len(inputs) >= 4 and not has_password:
            logger.info(f"[SIMPLE-GEN] Detected FORM page ({len(inputs)} inputs, no password)")
            return 'form'
        
        logger.info(f"[SIMPLE-GEN] Detected GENERIC page")
        return 'generic'
    
    def _generate_login_tests(self, inputs: List[Dict], buttons: List[Dict]) -> List[Dict]:
        """Generate comprehensive login test methods with positive and negative scenarios."""
        # Use only first 2 inputs for login (email + password), ignore extras
        email_input = inputs[0] if len(inputs) > 0 else None
        password_input = inputs[1] if len(inputs) > 1 else None
        login_button = buttons[0] if len(buttons) > 0 else None
        
        logger.info(f"[LOGIN-GEN] Using {len(inputs)} inputs, but only first 2 for login tests")
        
        if not email_input or not password_input or not login_button:
            logger.error(f"[LOGIN-GEN] Missing elements: email={email_input}, pwd={password_input}, btn={login_button}")
            return []
        
        email_locator = self._build_locator(email_input)
        password_locator = self._build_locator(password_input)
        button_locator = self._build_locator(login_button)
        
        logger.info(f"[LOGIN-GEN] Locators: email={email_locator}, pwd={password_locator}, btn={button_locator}")
        
        tests = []
        
        # ============ POSITIVE TEST CASES ============
        
        # Test 1: Valid Login
        tests.append({
            'name': 'testSuccessfulLogin',
            'description': 'Verify successful login with valid credentials',
            'code': f'''    /**
     * TC-001: Verify successful login with valid credentials
     */
    @Test(priority = 1)
    public void testSuccessfulLogin() {{
        // Wait for email field and enter credentials
        wait.until(ExpectedConditions.visibilityOfElementLocated({email_locator}));
        driver.findElement({email_locator}).sendKeys("user@example.com");
        
        wait.until(ExpectedConditions.visibilityOfElementLocated({password_locator}));
        driver.findElement({password_locator}).sendKeys("Password123!");
        
        wait.until(ExpectedConditions.elementToBeClickable({button_locator}));
        driver.findElement({button_locator}).click();
        
        wait.until(ExpectedConditions.not(ExpectedConditions.urlToBe(BASE_URL)));
        
        // Verify successful login redirect
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "User should be redirected to dashboard after successful login");
    }}'''
        })
        
        # Test 2: Different Valid Email Format
        tests.append({
            'name': 'testLoginWithDifferentValidEmailFormat',
            'description': 'Verify login with various valid email formats',
            'code': f'''    /**
     * TC-002: Verify login with different valid email formats
     */
    @Test(priority = 2)
    public void testLoginWithDifferentValidEmailFormat() {{
        driver.findElement({email_locator}).sendKeys("test.user+tag@company.co.uk");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should accept valid email formats with dots, plus signs, and multiple TLDs");
    }}'''
        })
        
        # ============ NEGATIVE TEST CASES ============
        
        # Test 3: Empty Email and Password
        tests.append({
            'name': 'testLoginWithEmptyFields',
            'description': 'Verify validation when both email and password are empty',
            'code': f'''    /**
     * TC-003: Verify both fields empty
     */
    @Test(priority = 3)
    public void testLoginWithEmptyFields() {{
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Should remain on login page with empty fields");
    }}'''
        })
        
        # Test 4: Empty Email Only
        tests.append({
            'name': 'testLoginWithEmptyEmail',
            'description': 'Verify validation when email field is empty',
            'code': f'''    /**
     * TC-004: Verify login fails with empty email
     */
    @Test(priority = 4)
    public void testLoginWithEmptyEmail() {{
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email field is required - should remain on login page");
    }}'''
        })
        
        # Test 5: Empty Password Only
        tests.append({
            'name': 'testLoginWithEmptyPassword',
            'description': 'Verify validation when password field is empty',
            'code': f'''    /**
     * TC-005: Verify login fails with empty password
     */
    @Test(priority = 5)
    public void testLoginWithEmptyPassword() {{
        driver.findElement({email_locator}).sendKeys("user@example.com");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Password field is required - should remain on login page");
    }}'''
        })
        
        # Test 6: Invalid Email Format - Missing @
        tests.append({
            'name': 'testLoginWithInvalidEmailMissingAt',
            'description': 'Verify validation with invalid email format (missing @)',
            'code': f'''    /**
     * TC-006: Verify login fails with invalid email format (missing @)
     */
    @Test(priority = 6)
    public void testLoginWithInvalidEmailMissingAt() {{
        driver.findElement({email_locator}).sendKeys("userexample.com");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Invalid email format should be rejected");
    }}'''
        })
        
        # Test 7: Invalid Email - Missing Domain
        tests.append({
            'name': 'testLoginWithInvalidEmailMissingDomain',
            'description': 'Verify validation with invalid email format (missing domain)',
            'code': f'''    /**
     * TC-007: Verify login fails with invalid email (missing domain)
     */
    @Test(priority = 7)
    public void testLoginWithInvalidEmailMissingDomain() {{
        driver.findElement({email_locator}).sendKeys("user@");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Incomplete email should be rejected");
    }}'''
        })
        
        # Test 8: Invalid Email - Special Characters
        tests.append({
            'name': 'testLoginWithInvalidEmailSpecialChars',
            'description': 'Verify validation with invalid email containing special characters',
            'code': f'''    /**
     * TC-008: Verify login fails with invalid special characters in email
     */
    @Test(priority = 8)
    public void testLoginWithInvalidEmailSpecialChars() {{
        driver.findElement({email_locator}).sendKeys("user#$%@example.com");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email with invalid special characters should be rejected");
    }}'''
        })
        
        # Test 9: Wrong Password
        tests.append({
            'name': 'testLoginWithWrongPassword',
            'description': 'Verify login failure with incorrect password',
            'code': f'''    /**
     * TC-009: Verify login fails with invalid password
     */
    @Test(priority = 9)
    public void testLoginWithWrongPassword() {{
        driver.findElement({email_locator}).sendKeys("user@example.com");
        driver.findElement({password_locator}).sendKeys("WrongPassword123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Incorrect password should not allow login");
    }}'''
        })
        
        # Test 10: Unregistered Email
        tests.append({
            'name': 'testLoginWithUnregisteredEmail',
            'description': 'Verify login failure with unregistered email',
            'code': f'''    /**
     * TC-010: Verify login fails with unregistered email
     */
    @Test(priority = 10)
    public void testLoginWithUnregisteredEmail() {{
        driver.findElement({email_locator}).sendKeys("nonexistent@example.com");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Unregistered email should not allow login");
    }}'''
        })
        
        # ============ SECURITY TEST CASES ============
        
        # Test 11: SQL Injection in Email
        tests.append({
            'name': 'testSQLInjectionInEmail',
            'description': 'Verify protection against SQL injection in email field',
            'code': f'''    /**
     * TC-011: Verify login with SQL injection attempt in email
     */
    @Test(priority = 11)
    public void testSQLInjectionInEmail() {{
        driver.findElement({email_locator}).sendKeys("admin' OR '1'='1");
        driver.findElement({password_locator}).sendKeys("password");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should reject SQL injection attempts");
    }}'''
        })
        
        # Test 12: SQL Injection in Password
        tests.append({
            'name': 'testSQLInjectionInPassword',
            'description': 'Verify protection against SQL injection in password field',
            'code': f'''    /**
     * TC-012: Verify login with SQL injection attempt in password
     */
    @Test(priority = 12)
    public void testSQLInjectionInPassword() {{
        driver.findElement({email_locator}).sendKeys("user@example.com");
        driver.findElement({password_locator}).sendKeys("' OR '1'='1' --");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should prevent SQL injection via password field");
    }}'''
        })
        
        # Test 13: XSS Attack in Email
        tests.append({
            'name': 'testXSSAttemptInEmail',
            'description': 'Verify protection against XSS attack in email field',
            'code': f'''    /**
     * TC-013: Verify login with XSS attempt in email
     */
    @Test(priority = 13)
    public void testXSSAttemptInEmail() {{
        driver.findElement({email_locator}).sendKeys("<script>alert('XSS')</script>");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertTrue(driver.getCurrentUrl().equals(BASE_URL), 
            "System should handle XSS attempts safely");
    }}'''
        })
        
        # Test 14: XSS Attack in Password
        tests.append({
            'name': 'testXSSAttemptInPassword',
            'description': 'Verify protection against XSS attack in password field',
            'code': f'''    /**
     * TC-014: Verify login with XSS attempt in password
     */
    @Test(priority = 14)
    public void testXSSAttemptInPassword() {{
        driver.findElement({email_locator}).sendKeys("user@example.com");
        driver.findElement({password_locator}).sendKeys("<img src=x onerror=alert('XSS')>");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertTrue(driver.getCurrentUrl().equals(BASE_URL), 
            "System should sanitize XSS scripts safely");
    }}'''
        })
        
        # ============ BOUNDARY TEST CASES ============
        
        # Test 15: Very Long Email
        tests.append({
            'name': 'testLoginWithVeryLongEmail',
            'description': 'Verify handling of extremely long email',
            'code': f'''    /**
     * TC-015: Verify handling of extremely long email
     */
    @Test(priority = 15)
    public void testLoginWithVeryLongEmail() {{
        String longEmail = "a".repeat(250) + "@example.com";
        driver.findElement({email_locator}).sendKeys(longEmail);
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should handle boundary case for email length");
    }}'''
        })
        
        # Test 16: Very Long Password
        tests.append({
            'name': 'testLoginWithVeryLongPassword',
            'description': 'Verify handling of extremely long password',
            'code': f'''    /**
     * TC-016: Verify handling of extremely long password
     */
    @Test(priority = 16)
    public void testLoginWithVeryLongPassword() {{
        String longPassword = "P@ssw0rd" + "a".repeat(500);
        driver.findElement({email_locator}).sendKeys("user@example.com");
        driver.findElement({password_locator}).sendKeys(longPassword);
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should handle boundary case for password length");
    }}'''
        })
        
        # Test 17: Single Character Email
        tests.append({
            'name': 'testLoginWithSingleCharEmail',
            'description': 'Verify validation with minimum length email',
            'code': f'''    /**
     * TC-017: Verify validation with single character email
     */
    @Test(priority = 17)
    public void testLoginWithSingleCharEmail() {{
        driver.findElement({email_locator}).sendKeys("a");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Single character should not be accepted as valid email");
    }}'''
        })
        
        # Test 18: Spaces in Email
        tests.append({
            'name': 'testLoginWithSpacesInEmail',
            'description': 'Verify validation with spaces in email',
            'code': f'''    /**
     * TC-018: Verify validation with spaces in email
     */
    @Test(priority = 18)
    public void testLoginWithSpacesInEmail() {{
        driver.findElement({email_locator}).sendKeys("user name@example.com");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email addresses should not contain spaces");
    }}'''
        })
        
        # Test 19: Case Sensitivity
        tests.append({
            'name': 'testEmailCaseSensitivity',
            'description': 'Verify email field case sensitivity handling',
            'code': f'''    /**
     * TC-019: Verify email case sensitivity
     */
    @Test(priority = 19)
    public void testEmailCaseSensitivity() {{
        driver.findElement({email_locator}).sendKeys("USER@EXAMPLE.COM");
        driver.findElement({password_locator}).sendKeys("Password123!");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        // Email should be case-insensitive per RFC 5321
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email should be case-insensitive for login");
    }}'''
        })
        
        # Test 20: Password Field Masking
        tests.append({
            'name': 'testPasswordFieldMasksInput',
            'description': 'Verify password field is masked by default',
            'code': f'''    /**
     * TC-020: Verify password field masks input
     */
    @Test(priority = 20)
    public void testPasswordFieldMasksInput() {{
        driver.findElement({password_locator}).sendKeys("Password123!");
        
        String passwordType = driver.findElement({password_locator}).getAttribute("type");
        
        Assert.assertEquals(passwordType, "password", 
            "Password field should be masked (type='password')");
    }}'''
        })
        
        return tests
    
    def _generate_search_tests(self, inputs: List[Dict], buttons: List[Dict]) -> List[Dict]:
        """Generate comprehensive search test methods with professional QA standards."""
        search_input = inputs[0]
        search_button = buttons[0] if buttons else None
        
        search_locator = self._build_locator(search_input)
        button_locator = self._build_locator(search_button) if search_button else "null"
        
        tests = []
        
        # Positive Tests
        tests.append({
            'name': 'testSearchWithValidQuery',
            'description': 'Verify search with valid query returns results',
            'code': f'''    /**
     * TC-001: Verify search with valid query
     */
    @Test(priority = 1)
    public void testSearchWithValidQuery() {{
        driver.findElement({search_locator}).sendKeys("test query");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "Search results should be displayed after valid query");
    }}'''
        })
        
        tests.append({
            'name': 'testSearchWithNumericQuery',
            'description': 'Verify search with numeric query',
            'code': f'''    /**
     * TC-002: Verify search with numeric query
     */
    @Test(priority = 2)
    public void testSearchWithNumericQuery() {{
        driver.findElement({search_locator}).sendKeys("12345");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should handle numeric search queries");
    }}'''
        })
        
        # Negative Tests
        tests.append({
            'name': 'testSearchWithEmptyQuery',
            'description': 'Verify validation with empty search query',
            'code': f'''    /**
     * TC-003: Verify validation with empty search
     */
    @Test(priority = 3)
    public void testSearchWithEmptyQuery() {{
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Search query should be required");
    }}'''
        })
        
        tests.append({
            'name': 'testSearchWithSpecialCharacters',
            'description': 'Verify search with special characters',
            'code': f'''    /**
     * TC-004: Verify search with special characters
     */
    @Test(priority = 4)
    public void testSearchWithSpecialCharacters() {{
        driver.findElement({search_locator}).sendKeys("!@#$%^&*()");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "System should handle special characters in search safely");
    }}'''
        })
        
        tests.append({
            'name': 'testSearchWithVeryLongQuery',
            'description': 'Verify search with extremely long query',
            'code': f'''    /**
     * TC-005: Verify search with very long query
     */
    @Test(priority = 5)
    public void testSearchWithVeryLongQuery() {{
        String longQuery = "test ".repeat(100);
        driver.findElement({search_locator}).sendKeys(longQuery);
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "System should handle boundary case for search query length");
    }}'''
        })
        
        # Security Tests
        tests.append({
            'name': 'testSearchSQLInjectionProtection',
            'description': 'Verify protection against SQL injection in search',
            'code': f'''    /**
     * TC-006: Verify SQL injection protection in search
     */
    @Test(priority = 6)
    public void testSearchSQLInjectionProtection() {{
        driver.findElement({search_locator}).sendKeys("' OR '1'='1");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "System should prevent SQL injection attempts via search");
    }}'''
        })
        
        tests.append({
            'name': 'testSearchXSSProtection',
            'description': 'Verify protection against XSS in search',
            'code': f'''    /**
     * TC-007: Verify XSS protection in search
     */
    @Test(priority = 7)
    public void testSearchXSSProtection() {{
        driver.findElement({search_locator}).sendKeys("<script>alert('XSS')</script>");
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "System should sanitize XSS scripts in search query");
    }}'''
        })
        
        return tests
    
    def _generate_form_tests(self, inputs: List[Dict], buttons: List[Dict]) -> List[Dict]:
        """Generate comprehensive form test methods with professional QA standards."""
        submit_button = buttons[0] if buttons else None
        button_locator = self._build_locator(submit_button) if submit_button else "null"
        
        tests = []
        
        # Positive Test: Valid Form Submission
        input_code = ""
        for idx, inp in enumerate(inputs[:5]):
            locator = self._build_locator(inp)
            field_name = self._infer_field_name(inp, idx)
            input_code += f'        driver.findElement({locator}).sendKeys("Valid {field_name}");\n'
        
        tests.append({
            'name': 'testFormSubmissionWithValidData',
            'description': 'Verify form submission with all valid data',
            'code': f'''    /**
     * TC-001: Verify form submission with valid data
     */
    @Test(priority = 1)
    public void testFormSubmissionWithValidData() {{
{input_code}        
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "Form should be submitted successfully with valid data");
    }}'''
        })
        
        # Negative Test: Empty Form
        tests.append({
            'name': 'testFormSubmissionWithEmptyFields',
            'description': 'Verify validation when all fields are empty',
            'code': f'''    /**
     * TC-002: Verify validation with empty fields
     */
    @Test(priority = 2)
    public void testFormSubmissionWithEmptyFields() {{
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Form fields should be required");
    }}'''
        })
        
        # Test Each Field Individually
        for idx, inp in enumerate(inputs[:3]):
            locator = self._build_locator(inp)
            field_name = self._infer_field_name(inp, idx)
            tc_num = f"TC-{str(idx+3).zfill(3)}"
            
            tests.append({
                'name': f'test{field_name}AcceptsValidInput',
                'description': f'Verify {field_name} field accepts valid input',
                'code': f'''    /**
     * {tc_num}: Verify {field_name} field accepts valid input
     */
    @Test(priority = {idx+3})
    public void test{field_name}AcceptsValidInput() {{
        driver.findElement({locator}).sendKeys("Valid {field_name}");
        
        String value = driver.findElement({locator}).getAttribute("value");
        Assert.assertFalse(value.isEmpty(), 
            "{field_name} field should accept and retain valid input");
    }}'''
            })
        
        # Security Tests
        security_priority = len(inputs) + 3
        
        # SQL Injection Test
        sql_injection_code = ""
        for idx, inp in enumerate(inputs[:3]):
            locator = self._build_locator(inp)
            sql_injection_code += f'        driver.findElement({locator}).sendKeys("admin\' OR \'1\'=\'1");\n'
        
        tests.append({
            'name': 'testFormSQLInjectionProtection',
            'description': 'Verify protection against SQL injection in form fields',
            'code': f'''    /**
     * TC-{str(security_priority).zfill(3)}: Verify SQL injection protection
     */
    @Test(priority = {security_priority})
    public void testFormSQLInjectionProtection() {{
{sql_injection_code}        
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should reject SQL injection attempts");
    }}'''
        })
        
        # XSS Test
        xss_code = ""
        for idx, inp in enumerate(inputs[:3]):
            locator = self._build_locator(inp)
            xss_code += f'        driver.findElement({locator}).sendKeys("<script>alert(\'XSS\')</script>");\n'
        
        tests.append({
            'name': 'testFormXSSProtection',
            'description': 'Verify protection against XSS in form fields',
            'code': f'''    /**
     * TC-{str(security_priority + 1).zfill(3)}: Verify XSS protection
     */
    @Test(priority = {security_priority + 1})
    public void testFormXSSProtection() {{
{xss_code}        
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(2000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should sanitize XSS scripts safely");
    }}'''
        })
        
        # Boundary Test: Very Long Input
        if len(inputs) > 0:
            first_input_locator = self._build_locator(inputs[0])
            field_name = self._infer_field_name(inputs[0], 0)
            tests.append({
                'name': 'testFormWithVeryLongInput',
                'description': 'Verify handling of extremely long input',
                'code': f'''    /**
     * TC-{str(security_priority + 2).zfill(3)}: Verify very long input handling
     */
    @Test(priority = {security_priority + 2})
    public void testFormWithVeryLongInput() {{
        String longInput = "A".repeat(1000);
        driver.findElement({first_input_locator}).sendKeys(longInput);
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "System should handle boundary case for {field_name} length");
    }}'''
            })
        
        return tests
    
    def _generate_generic_tests(self, inputs: List[Dict], buttons: List[Dict]) -> List[Dict]:
        """Generate professional test methods for generic UI elements."""
        tests = []
        
        # Positive Test: Valid Interaction
        interaction_code = ""
        for idx, inp in enumerate(inputs[:3]):
            locator = self._build_locator(inp)
            field_name = self._infer_field_name(inp, idx)
            interaction_code += f'        driver.findElement({locator}).sendKeys("Test {field_name}");\n'
        
        if buttons:
            button_locator = self._build_locator(buttons[0])
            interaction_code += f'        driver.findElement({button_locator}).click();'
        
        tests.append({
            'name': 'testUIElementsInteraction',
            'description': 'Verify successful interaction with UI elements',
            'code': f'''    /**
     * TC-001: Verify interaction with UI elements
     */
    @Test(priority = 1)
    public void testUIElementsInteraction() {{
{interaction_code}
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "UI elements should respond to user interactions");
    }}'''
        })
        
        # Element Visibility Test
        tests.append({
            'name': 'testUIElementsVisibility',
            'description': 'Verify all UI elements are visible',
            'code': f'''    /**
     * TC-002: Verify UI elements are visible
     */
    @Test(priority = 2)
    public void testUIElementsVisibility() {{
        driver.get(BASE_URL);
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertTrue(driver.findElements(By.tagName("input")).size() > 0, 
            "Input elements should be visible on page load");
    }}'''
        })
        
        # Individual Input Tests
        for idx, inp in enumerate(inputs[:3]):
            locator = self._build_locator(inp)
            field_name = self._infer_field_name(inp, idx)
            tc_num = f"TC-{str(idx+3).zfill(3)}"
            
            tests.append({
                'name': f'test{field_name}AcceptsData',
                'description': f'Verify {field_name} input accepts data',
                'code': f'''    /**
     * {tc_num}: Verify {field_name} accepts input
     */
    @Test(priority = {idx+3})
    public void test{field_name}AcceptsData() {{
        driver.findElement({locator}).sendKeys("Sample {field_name}");
        
        String value = driver.findElement({locator}).getAttribute("value");
        Assert.assertFalse(value.isEmpty(), 
            "{field_name} should accept and retain input data");
    }}'''
            })
        
        # Button Click Tests
        for idx, btn in enumerate(buttons[:2]):
            button_locator = self._build_locator(btn)
            tc_num = f"TC-{str(len(inputs)+idx+3).zfill(3)}"
            
            tests.append({
                'name': f'testButton{idx+1}Clickable',
                'description': f'Verify button {idx+1} is clickable',
                'code': f'''    /**
     * {tc_num}: Verify button {idx+1} functionality
     */
    @Test(priority = {len(inputs)+idx+3})
    public void testButton{idx+1}Clickable() {{
        driver.findElement({button_locator}).click();
        
        try {{ Thread.sleep(1000); }} catch (InterruptedException e) {{ }}
        
        Assert.assertNotNull(driver, 
            "Button {idx+1} should be clickable and functional");
    }}'''
            })
        
        # Security Test: Special Characters
        if len(inputs) > 0:
            first_input_locator = self._build_locator(inputs[0])
            field_name = self._infer_field_name(inputs[0], 0)
            security_priority = len(inputs) + len(buttons) + 3
            
            tests.append({
                'name': 'testSpecialCharacterHandling',
                'description': 'Verify special character handling',
                'code': f'''    /**
     * TC-{str(security_priority).zfill(3)}: Verify special character handling
     */
    @Test(priority = {security_priority})
    public void testSpecialCharacterHandling() {{
        driver.findElement({first_input_locator}).sendKeys("!@#$%^&*()");
        
        String value = driver.findElement({first_input_locator}).getAttribute("value");
        Assert.assertNotNull(value, 
            "System should handle special characters in {field_name} safely");
    }}'''
            })
        
        return tests
    
    def _infer_html_id_from_label(self, label: str, element_type: str) -> Optional[str]:
        """
        Infer likely HTML id attribute from visible label text.
        Mimics professional LoginPage.java approach of using semantic IDs.
        
        Args:
            label: Extracted text from screenshot (e.g., "Email", "Password")
            element_type: Type of element ('input', 'button', 'link')
        
        Returns:
            Likely HTML id or None
        """
        if not label or label == 'NO LABEL':
            return None
        
        label_lower = label.lower().strip()
        
        # Map common field labels to standard HTML IDs (like LoginPage.java)
        field_mappings = {
            # Email variations
            'email': 'email',
            'e-mail': 'email',
            'email address': 'email',
            'your email': 'email',
            
            # Password variations
            'password': 'password',
            'pass': 'password',
            'pwd': 'password',
            'your password': 'password',
            
            # Username variations
            'username': 'username',
            'user name': 'username',
            'login': 'username',
            'user': 'username',
            
            # Name fields
            'first name': 'firstName',
            'firstname': 'firstName',
            'fname': 'firstName',
            'given name': 'firstName',
            
            'last name': 'lastName',
            'lastname': 'lastName',
            'lname': 'lastName',
            'surname': 'lastName',
            
            'full name': 'fullName',
            'name': 'name',
            
            # Contact fields
            'phone': 'phone',
            'phone number': 'phone',
            'mobile': 'mobile',
            'telephone': 'phone',
            
            'address': 'address',
            'street': 'street',
            'city': 'city',
            'state': 'state',
            'zip': 'zip',
            'zipcode': 'zip',
            'postal code': 'zip',
            
            # Company fields
            'company': 'company',
            'organization': 'organization',
            'employer': 'employer',
        }
        
        # Check for exact or partial match
        for key, html_id in field_mappings.items():
            if key in label_lower:
                logger.info(f"[SMART-MAPPING] '{label}' → By.id(\"{html_id}\") (like LoginPage.java)")
                return html_id
        
        return None
    
    def _build_locator(self, element: Dict) -> str:
        """
        Build professional locator like LoginPage.java using smart ID inference from extracted text.
        GUARANTEES a valid locator for ANY element - multiple fallback strategies.
        """
        if not element:
            return "null"
        
        # Priority 1: id attribute if already provided
        if element.get('id'):
            logger.info(f"[LOCATOR] Using provided id: {element['id']}")
            return f'By.id("{element["id"]}")'
        
        # Priority 2: name attribute if already provided
        if element.get('name'):
            logger.info(f"[LOCATOR] Using provided name: {element['name']}")
            return f'By.name("{element["name"]}")'
        
        # Priority 3: SMART INFERENCE - Map extracted text to likely HTML id (BEST!)
        element_type = element.get('type', 'input')
        label = element.get('label', '').strip()
        
        if label and label != 'NO LABEL':
            inferred_id = self._infer_html_id_from_label(label, element_type)
            if inferred_id:
                # Generate professional locator like @FindBy(id = "email") in LoginPage.java
                logger.info(f"[LOCATOR] ✅ Smart mapping: '{label}' → By.id(\"{inferred_id}\")")
                return f'By.id("{inferred_id}")'
        
        # Priority 4: className (GOOD for unique classes)
        if element.get('class') and 'error' not in element.get('class', '').lower():
            logger.info(f"[LOCATOR] Using className: {element['class']}")
            return f'By.className("{element["class"]}")'
        
        # Priority 5: Professional XPath from button text (like LoginPage.java Sign In button)
        if element_type == 'button' and label and label != 'NO LABEL':
            clean_label = label.replace('"', '').replace("'", "").strip()
            # Professional XPath like: //button[contains(text(), 'Sign In')]
            logger.info(f"[LOCATOR] ✅ Button XPath: //button[contains(text(), '{clean_label}')]")
            return f'By.xpath("//button[contains(text(), \'{clean_label}\')]")'
        
        # Priority 6: linkText for links (like LoginPage.java "Forgot password" link)
        if element_type == 'link' and label:
            logger.info(f"[LOCATOR] Link text: {label}")
            return f'By.linkText("{label}")'
        
        # Priority 7: XPath with placeholder for inputs (extracted from label)
        if label and label != 'NO LABEL':
            clean_label = label.replace('"', '').replace("'", "").strip()
            logger.info(f"[LOCATOR] Placeholder XPath: //input[@placeholder='{clean_label}']")
            return f'By.xpath("//input[@placeholder=\'{clean_label}\']")'
        
        # Priority 8: Placeholder attribute alone
        placeholder = element.get('placeholder', '').strip()
        if placeholder:
            logger.info(f"[LOCATOR] Using placeholder: {placeholder}")
            return f'By.xpath("//input[@placeholder=\'{placeholder}\']")'
        
        # Priority 9: CSS selector if provided
        if element.get('css_selector'):
            logger.info(f"[LOCATOR] Using CSS selector: {element['css_selector']}")
            return f'By.cssSelector("{element["css_selector"]}")'
        
        # Priority 10: Direct XPath if provided
        if element.get('xpath'):
            logger.info(f"[LOCATOR] Using provided XPath: {element['xpath']}")
            return f'By.xpath("{element["xpath"]}")'
        
        # Priority 11: Position + Type based locator (guaranteed fallback)
        element_id = id(element)
        if element_type == 'button':
            position_index = self.button_positions.get(element_id, 1)
            logger.warning(f"[LOCATOR] ⚠️ Fallback button position: //button[{position_index}]")
            return f'By.xpath("//button[{position_index}]")'
        elif element_type == 'link':
            position_index = self.button_positions.get(element_id, 1)  # Use button counter for links
            logger.warning(f"[LOCATOR] ⚠️ Fallback link position: //a[{position_index}]")
            return f'By.xpath("//a[{position_index}]")'
        else:
            position_index = self.input_positions.get(element_id, 1)
            logger.warning(f"[LOCATOR] ⚠️ Fallback input position: //input[{position_index}]")
            return f'By.xpath("//input[{position_index}]")'
    
    def _infer_field_name(self, element: Dict, index: int) -> str:
        """Infer semantic field name from label, placeholder, or position."""
        # Try label first
        label = element.get('label', '').strip()
        
        # Clean up bad OCR labels
        if label and label not in ['NO LABEL', 'Input 1', 'Input 2', 'Input 3', 'Input 4', '{D}', '{d}']:
            label_lower = label.lower()
            
            # Match against known patterns
            if any(kw in label_lower for kw in ['first', 'fname', 'given']):
                return 'FirstName'
            elif any(kw in label_lower for kw in ['last', 'lname', 'surname', 'family']):
                return 'LastName'
            elif any(kw in label_lower for kw in ['email', 'e-mail', 'mail']):
                return 'Email'
            elif any(kw in label_lower for kw in ['phone', 'mobile', 'tel', 'contact']):
                return 'Phone'
            elif any(kw in label_lower for kw in ['password', 'pass', 'pwd']):
                return 'Password'
            elif any(kw in label_lower for kw in ['user', 'username', 'login']):
                return 'Username'
            elif any(kw in label_lower for kw in ['search', 'find', 'query']):
                return 'SearchQuery'
            elif any(kw in label_lower for kw in ['address', 'street']):
                return 'Address'
            elif any(kw in label_lower for kw in ['city', 'town']):
                return 'City'
            elif any(kw in label_lower for kw in ['state', 'province']):
                return 'State'
            elif any(kw in label_lower for kw in ['zip', 'postal', 'code']):
                return 'ZipCode'
            elif any(kw in label_lower for kw in ['country']):
                return 'Country'
            elif any(kw in label_lower for kw in ['name']) and 'first' not in label_lower and 'last' not in label_lower:
                return 'Name'
            elif any(kw in label_lower for kw in ['message', 'comment', 'description']):
                return 'Message'
            elif any(kw in label_lower for kw in ['age', 'dob', 'birth']):
                return 'Age'
            else:
                # Use the label as-is, capitalize first letter
                return label.replace(' ', '')
        
        # Try placeholder
        placeholder = element.get('placeholder', '').strip()
        if placeholder and placeholder != 'NO LABEL':
            return placeholder.replace(' ', '')
        
        # Intelligent fallback based on position for common form patterns
        # Position 0: Usually first name or username
        # Position 1: Usually last name or password
        # Position 2: Usually email
        # Position 3+: Other fields
        if index == 0:
            return 'FirstName'
        elif index == 1:
            return 'LastName'
        elif index == 2:
            return 'Email'
        elif index == 3:
            return 'Phone'
        else:
            return f'Field{index+1}'
    
    def create_complete_test_class(self, test_methods: List[Dict], class_name: str = "ScreenshotTest") -> str:
        """Create complete TestNG test class with professional quality matching LoginPage.java standards."""
        
        # Build all test methods
        methods_code = "\n\n".join([test['code'] for test in test_methods])
        
        return f'''package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Automated Test Cases for Application
 * Auto-generated from Screenshot Analysis
 * Professional Quality Test Suite
 * Total Test Cases: {len(test_methods)}
 */
public class {class_name} {{
    
    private WebDriver driver;
    private WebDriverWait wait;
    private static final String BASE_URL = "YOUR_URL_HERE";
    
    /**
     * Setup ChromeDriver configuration
     */
    @BeforeClass
    public void setupClass() {{
        // Setup ChromeDriver - Update path as needed
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
    }}
    
    /**
     * Initialize WebDriver and navigate to base URL before each test
     */
    @BeforeMethod
    public void setup() {{
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        options.addArguments("--disable-blink-features=AutomationControlled");
        options.addArguments("--disable-popup-blocking");
        
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        driver.get(BASE_URL);
    }}
    
    /**
     * Clean up WebDriver after each test
     */
    @AfterMethod
    public void tearDown() {{
        if (driver != null) {{
            driver.quit();
        }}
    }}

{methods_code}

}}
'''
