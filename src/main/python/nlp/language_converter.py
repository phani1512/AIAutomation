"""Language Converter Module - Convert Selenium code between different programming languages.

This module handles conversion of Selenium code between:
- Python ↔ Java
- Python/Java → JavaScript (Playwright)
- Python/Java → Cypress
- Python/Java → C#

Extracted from inference_improved.py for better modularity and maintainability.
"""

import re


class LanguageConverter:
    """Converts Selenium code between different programming languages."""
    
    def __init__(self, method_mappings=None):
        """Initialize the language converter.
        
        Args:
            method_mappings: Optional dictionary of method mappings for different languages
        """
        self.method_mappings = method_mappings or {}
    
    def convert_code_to_language(self, code: str, language: str) -> str:
        """Convert code to target language. Dataset now has Python code by default.
        
        Args:
            code: Source code to convert
            language: Target language ('python', 'java', 'javascript', 'cypress', 'csharp')
        
        Returns:
            Converted code in target language
        """
        print(f"[LANGUAGE CONVERTER] Converting to {language}")
        print(f"[LANGUAGE CONVERTER] Input code (first 100 chars): {code[:100]}...")
        
        # Detect if code is already in target language
        is_python_code = ('wait = WebDriverWait' in code or 'wait.until(EC.' in code or '.send_keys(' in code)
        is_java_code = ('WebElement' in code or 'new WebDriverWait' in code or '.sendKeys(' in code)
        
        print(f"[LANGUAGE CONVERTER] Detected: is_python={is_python_code}, is_java={is_java_code}")
        
        # If code is already Python and target is Python, return as-is
        if language == 'python' and is_python_code:
            print(f"[LANGUAGE CONVERTER] Already Python, returning as-is")
            return code
        
        # If code is already Java and target is Java, return as-is
        if language == 'java' and is_java_code:
            print(f"[LANGUAGE CONVERTER] Already Java, returning as-is")
            return code
        
        # Convert Python to Java if needed
        if language == 'java' and is_python_code:
            print(f"[LANGUAGE CONVERTER] Converting Python → Java")
            converted = self._python_to_java(code)
            print(f"[LANGUAGE CONVERTER] Result (first 100 chars): {converted[:100]}...")
            return converted
        
        # Get mappings for target language
        lang_mappings = self.method_mappings.get(language, {})
        
        if language == 'python':
            # Already Python, return as-is if Python code
            if is_python_code:
                return code
            
            # Java to Python conversion (if code is Java)
            return self._java_to_python(code, lang_mappings)
        
        elif language == 'javascript':
            # Convert Python to JavaScript (Playwright) or Java to JavaScript
            if is_python_code:
                return self._python_to_javascript(code)
            else:
                return self._java_to_javascript(code)
        
        elif language == 'cypress':
            # Convert Python or Java to Cypress
            if is_python_code:
                return self._python_to_cypress(code)
            else:
                return self._java_to_cypress(code)
        
        elif language == 'csharp':
            return self._to_csharp(code, lang_mappings)
        
        # Default: return code as-is if no specific conversion
        return code
    
    def _python_to_java(self, code: str) -> str:
        """Convert Python Selenium code to Java.
        
        Args:
            code: Python Selenium code
        
        Returns:
            Java Selenium code
        """
        java_code = code
        
        # Convert wait initialization
        java_code = java_code.replace('wait = WebDriverWait(driver, 10)', 'WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10))')
        java_code = java_code.replace('wait = WebDriverWait(driver, Duration.ofSeconds(10))', 'WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10))')
        
        # Convert Expected Conditions
        java_code = java_code.replace('EC.visibility_of_element_located', 'ExpectedConditions.visibilityOfElementLocated')
        java_code = java_code.replace('EC.element_to_be_clickable', 'ExpectedConditions.elementToBeClickable')
        java_code = java_code.replace('EC.presence_of_element_located', 'ExpectedConditions.presenceOfElementLocated')
        java_code = java_code.replace('EC.visibility_of', 'ExpectedConditions.visibilityOf')
        java_code = java_code.replace('EC.invisibility_of_element', 'ExpectedConditions.invisibilityOfElementLocated')
        java_code = java_code.replace('EC.frame_to_be_available_and_switch_to_it', 'ExpectedConditions.frameToBeAvailableAndSwitchToIt')
        java_code = java_code.replace('EC.alert_is_present', 'ExpectedConditions.alertIsPresent')
        
        # Convert element methods
        java_code = java_code.replace('.send_keys(', '.sendKeys(')
        java_code = java_code.replace('.get_attribute(', '.getAttribute(')
        java_code = java_code.replace('.is_displayed()', '.isDisplayed()')
        java_code = java_code.replace('.is_enabled()', '.isEnabled()')
        java_code = java_code.replace('.is_selected()', '.isSelected()')
        java_code = java_code.replace('.find_element(', '.findElement(')
        java_code = java_code.replace('.find_elements(', '.findElements(')
        
        # Convert driver methods
        java_code = java_code.replace('driver.find_element(', 'driver.findElement(')
        java_code = java_code.replace('driver.find_elements(', 'driver.findElements(')
        java_code = java_code.replace('driver.switch_to.', 'driver.switchTo().')
        java_code = java_code.replace('driver.execute_script(', 'driver.executeScript(')
        
        # Convert By locators
        java_code = java_code.replace('By.ID, ', 'By.id(')
        java_code = java_code.replace('By.NAME, ', 'By.name(')
        java_code = java_code.replace('By.CLASS_NAME, ', 'By.className(')
        java_code = java_code.replace('By.CSS_SELECTOR, ', 'By.cssSelector(')
        java_code = java_code.replace('By.XPATH, ', 'By.xpath(')
        java_code = java_code.replace('By.LINK_TEXT, ', 'By.linkText(')
        java_code = java_code.replace('By.PARTIAL_LINK_TEXT, ', 'By.partialLinkText(')
        java_code = java_code.replace('By.TAG_NAME, ', 'By.tagName(')
        
        # Fix By.method syntax: convert (By.XPATH, "value") to (By.xpath("value"))
        java_code = re.sub(r'\(By\.([A-Z_]+),\s*"([^"]+)"\)', lambda m: f'(By.{m.group(1).lower()}("{m.group(2)}"))', java_code)
        java_code = re.sub(r'\(By\.([A-Z_]+),\s*\'([^\']+)\'\)', lambda m: f'(By.{m.group(1).lower()}(\'{m.group(2)}\'))', java_code)
        
        # Convert variable declarations
        java_code = re.sub(r'^(\s*)(\w+)\s*=\s*wait\.until', r'\1WebElement \2 = wait.until', java_code, flags=re.MULTILINE)
        java_code = re.sub(r'^(\s*)(\w+)\s*=\s*driver\.findElement', r'\1WebElement \2 = driver.findElement', java_code, flags=re.MULTILINE)
        
        # Add semicolons at end of statements if missing
        lines = java_code.split('\n')
        java_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', '//')):
                # Only add semicolon to actual code lines, not comments
                if not stripped.startswith('//') and not stripped.startswith('/*'):
                    line = line.rstrip() + ';'
            java_lines.append(line)
        java_code = '\n'.join(java_lines)
        
        return java_code
    
    def _java_to_python(self, code: str, lang_mappings: dict) -> str:
        """Convert Java Selenium code to Python.
        
        Args:
            code: Java Selenium code
            lang_mappings: Method mappings from dataset
        
        Returns:
            Python Selenium code
        """
        # Apply type conversions from dataset
        for type_conv in lang_mappings.get('type_conversions', []):
            pattern = type_conv.get('pattern')
            replacement = type_conv.get('replacement')
            if pattern and replacement:
                code = re.sub(pattern, replacement, code)
        
        # Apply method mappings from dataset
        for mapping in lang_mappings.get('method_mappings', []):
            java_method = mapping.get('java_method')
            python_method = mapping.get('python_method')
            if java_method and python_method:
                code = code.replace(java_method, python_method)
        
        return code
    
    def _python_to_javascript(self, code: str) -> str:
        """Convert Python Selenium code to JavaScript (Playwright).
        
        Args:
            code: Python Selenium code
        
        Returns:
            JavaScript (Playwright) code
        """
        js_code = code
        
        # Convert wait initialization
        js_code = js_code.replace('wait = WebDriverWait(driver, 10)', '// Playwright handles waits automatically')
        js_code = js_code.replace('wait = WebDriverWait(driver, Duration.ofSeconds(10))', '// Playwright handles waits automatically')
        
        # Convert wait.until to Playwright locators
        js_code = re.sub(r'wait\.until\(EC\.visibility_of_element_located\(\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\)', 
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').waitFor()', js_code)
        js_code = re.sub(r'wait\.until\(EC\.element_to_be_clickable\(\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').waitFor()', js_code)
        
        # Convert element interactions
        js_code = re.sub(r'driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\.click\(\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').click()', js_code)
        js_code = re.sub(r'driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\.send_keys\(([^)]+)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').fill({m.group(3)})', js_code)
        
        # Convert Select
        js_code = re.sub(r'Select\(driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\.select_by_visible_text\(([^)]+)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').selectOption({{label: {m.group(3)}}})', js_code)
        
        # Remove Python-specific imports
        js_code = re.sub(r'from selenium.*\n', '', js_code)
        js_code = re.sub(r'import .*\n', '', js_code)
        
        return js_code.strip()
    
    def _java_to_javascript(self, code: str) -> str:
        """Convert Java Selenium code to JavaScript (Playwright).
        
        Args:
            code: Java Selenium code
        
        Returns:
            JavaScript (Playwright) code
        """
        js_code = code
        
        # Convert WebDriverWait to Playwright waits (remove, Playwright has built-in waits)
        js_code = re.sub(r'WebDriverWait wait = new WebDriverWait\([^;]+;', '', js_code)
        js_code = js_code.replace('WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));', '')
        
        # Convert wait.until to Playwright locators
        js_code = re.sub(r'wait\.until\(ExpectedConditions\.visibilityOfElementLocated\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').waitFor()', js_code)
        js_code = re.sub(r'wait\.until\(ExpectedConditions\.elementToBeClickable\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').waitFor()', js_code)
        js_code = re.sub(r'wait\.until\(ExpectedConditions\.presenceOfElementLocated\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'await page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\').waitFor()', js_code)
        
        # Convert WebElement declarations
        js_code = re.sub(r'WebElement \w+ = ', 'const element = ', js_code)
        
        # Convert driver.findElement to page.locator
        js_code = re.sub(r'driver\.findElement\(By\.(\w+)\("([^"]+)"\)\)',
                        lambda m: f'page.locator(\'{self.convert_by_to_playwright(m.group(1), m.group(2))}\')', js_code)
        
        # Convert element interactions
        js_code = js_code.replace('element.click();', 'await element.click();')
        js_code = re.sub(r'\.sendKeys\("([^"]+)"\);', r'.fill("\1");', js_code)
        js_code = js_code.replace('.clear();', '.clear();')
        
        # Convert Select to Playwright select
        js_code = re.sub(r'Select select = new Select\(([^)]+)\);', '', js_code)
        js_code = re.sub(r'select\.selectByVisibleText\("([^"]+)"\);', r'await element.selectOption({label: "\1"});', js_code)
        
        # Remove Java-specific imports
        js_code = re.sub(r'import .*;\n', '', js_code)
        js_code = js_code.replace('Thread.sleep(2000);', 'await page.waitForTimeout(2000);')
        js_code = js_code.replace('Thread.sleep(500);', 'await page.waitForTimeout(500);')
        
        # Add await to element interactions
        js_code = re.sub(r'^(\s*)(element\.\w+\()', r'\1await \2', js_code, flags=re.MULTILINE)
        js_code = re.sub(r'^(\s*)(page\.locator.*\.(?:click|fill|type|selectOption))', r'\1await \2', js_code, flags=re.MULTILINE)
        
        return js_code.strip()
    
    def _python_to_cypress(self, code: str) -> str:
        """Convert Python Selenium code to Cypress.
        
        Args:
            code: Python Selenium code
        
        Returns:
            Cypress code
        """
        cy_code = code
        
        # Convert wait.until to Cypress locators
        cy_code = re.sub(r'wait\.until\(EC\.visibility_of_element_located\(\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').should(\'be.visible\')', cy_code)
        cy_code = re.sub(r'wait\.until\(EC\.element_to_be_clickable\(\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').should(\'be.visible\')', cy_code)
        
        # Convert element interactions  
        cy_code = re.sub(r'driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\.click\(\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').click()', cy_code)
        cy_code = re.sub(r'driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\.send_keys\(([^)]+)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').type({m.group(3)})', cy_code)
        
        # Convert Select
        cy_code = re.sub(r'Select\(driver\.find_element\(By\.(\w+),\s*["\']([^"\']+)["\']\)\)\.select_by_visible_text\(([^)]+)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').select({m.group(3)})', cy_code)
        
        # Remove Python-specific imports
        cy_code = re.sub(r'from selenium.*\n', '', cy_code)
        cy_code = re.sub(r'import .*\n', '', cy_code)
        
        # Add Cypress wait
        cy_code = cy_code.replace('time.sleep(2)', 'cy.wait(2000)')
        cy_code = cy_code.replace('Thread.sleep(2000)', 'cy.wait(2000)')
        
        return cy_code.strip()
    
    def _java_to_cypress(self, code: str) -> str:
        """Convert Java Selenium code to Cypress.
        
        Args:
            code: Java Selenium code
        
        Returns:
            Cypress code
        """
        cy_code = code
        
        # Convert WebDriverWait to Cypress waits
        cy_code = re.sub(r'WebDriverWait wait = new WebDriverWait\([^;]+;', '', cy_code)
        cy_code = cy_code.replace('WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));', '')
        
        # Convert wait.until to Cypress locators
        cy_code = re.sub(r'wait\.until\(ExpectedConditions\.visibilityOfElementLocated\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').should(\'be.visible\')', cy_code)
        cy_code = re.sub(r'wait\.until\(ExpectedConditions\.elementToBeClickable\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').should(\'be.visible\')', cy_code)
        cy_code = re.sub(r'wait\.until\(ExpectedConditions\.presenceOfElementLocated\(By\.(\w+)\("([^"]+)"\)\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\').should(\'exist\')', cy_code)
        
        # Convert WebElement declarations
        cy_code = re.sub(r'WebElement \w+ = ', '', cy_code)
        
        # Convert driver.findElement to cy.get
        cy_code = re.sub(r'driver\.findElement\(By\.(\w+)\("([^"]+)"\)\)',
                        lambda m: f'cy.get(\'{self.convert_by_to_cypress(m.group(1), m.group(2))}\')', cy_code)
        
        # Convert element interactions
        cy_code = re.sub(r'(\w+)\.click\(\);', r'cy.get(\'#\1\').click();', cy_code)
        cy_code = cy_code.replace('.click();', '.click();')
        cy_code = re.sub(r'\.sendKeys\("([^"]+)"\);', r'.type("\1");', cy_code)
        cy_code = cy_code.replace('.clear();', '.clear();')
        
        # Convert Select to Cypress select
        cy_code = re.sub(r'Select select = new Select\(([^)]+)\);', '', cy_code)
        cy_code = re.sub(r'select\.selectByVisibleText\("([^"]+)"\);', r'.select("\1");', cy_code)
        
        # Remove Java-specific code
        cy_code = re.sub(r'import .*;\n', '', cy_code)
        cy_code = cy_code.replace('Thread.sleep(2000);', 'cy.wait(2000);')
        cy_code = cy_code.replace('Thread.sleep(500);', 'cy.wait(500);')
        
        # Remove comments about Java
        cy_code = re.sub(r'// (Wait for|Get|Check|Click|Enter|Select|Verify) .* with wait', lambda m: f'// {m.group(1)}', cy_code)
        
        return cy_code.strip()
    
    def _to_csharp(self, code: str, lang_mappings: dict) -> str:
        """Convert code to C#.
        
        Args:
            code: Source code
            lang_mappings: Method mappings from dataset
        
        Returns:
            C# code
        """
        # Apply type conversions from dataset
        for type_conv in lang_mappings.get('type_conversions', []):
            pattern = type_conv.get('pattern')
            replacement = type_conv.get('replacement')
            if pattern and replacement:
                code = code.replace(pattern, replacement)
        
        # Apply method patterns from dataset
        for method_pattern in lang_mappings.get('method_patterns', []):
            pattern = method_pattern.get('pattern')
            if pattern and method_pattern.get('capitalize_first'):
                # Special handling for capitalization patterns
                if pattern == 'is(\\w)':
                    code = re.sub(r'is(\w)', lambda m: 'Is' + m.group(1).upper(), code)
                elif pattern == 'get(\\w)':
                    code = re.sub(r'get(\w)', lambda m: 'Get' + m.group(1).upper(), code)
                elif pattern == 'set(\\w)':
                    code = re.sub(r'set(\w)', lambda m: 'Set' + m.group(1).upper(), code)
                elif pattern == 'click(\\w)':
                    code = re.sub(r'click(\w)', lambda m: 'Click' + m.group(1).upper(), code)
        
        return code
    
    def java_to_python_by(self, java_by_method: str) -> str:
        """Convert Java By method names to Python constants.
        
        Args:
            java_by_method: Java By method name (e.g., 'id', 'className')
        
        Returns:
            Python By constant (e.g., 'By.ID', 'By.CLASS_NAME')
        """
        by_mapping = {
            'id': 'By.ID',
            'name': 'By.NAME',
            'className': 'By.CLASS_NAME',
            'cssSelector': 'By.CSS_SELECTOR',
            'xpath': 'By.XPATH',
            'linkText': 'By.LINK_TEXT',
            'partialLinkText': 'By.PARTIAL_LINK_TEXT',
            'tagName': 'By.TAG_NAME'
        }
        return by_mapping.get(java_by_method, f'By.{java_by_method.upper()}')
    
    def convert_by_to_playwright(self, by_type: str, value: str) -> str:
        """Convert Selenium By locator to Playwright selector syntax.
        
        Args:
            by_type: Selenium By type (e.g., 'ID', 'XPATH', 'CSS_SELECTOR')
            value: Locator value
        
        Returns:
            Playwright selector string
        """
        by_type_upper = by_type.upper()
        
        if by_type_upper == 'ID':
            return f'#{value}'
        elif by_type_upper == 'NAME':
            return f'[name="{value}"]'
        elif by_type_upper == 'XPATH':
            return f'xpath={value}'
        elif by_type_upper == 'CSS_SELECTOR' or by_type_upper == 'CSSSELECTOR':
            return value
        elif by_type_upper == 'CLASS_NAME' or by_type_upper == 'CLASSNAME':
            return f'.{value}'
        elif by_type_upper == 'LINK_TEXT' or by_type_upper == 'LINKTEXT':
            return f'text={value}'
        elif by_type_upper == 'PARTIAL_LINK_TEXT' or by_type_upper == 'PARTIALLINKTEXT':
            return f'text=/{value}/'
        elif by_type_upper == 'TAG_NAME' or by_type_upper == 'TAGNAME':
            return value
        else:
            # Default to CSS selector
            return value
    
    def convert_by_to_cypress(self, by_type: str, value: str) -> str:
        """Convert Selenium By locator to Cypress selector syntax.
        
        Args:
            by_type: Selenium By type (e.g., 'ID', 'XPATH', 'CSS_SELECTOR')
            value: Locator value
        
        Returns:
            Cypress selector string
        """
        by_type_upper = by_type.upper()
        
        if by_type_upper == 'ID':
            return f'#{value}'
        elif by_type_upper == 'NAME':
            return f'[name="{value}"]'
        elif by_type_upper == 'XPATH':
            # Cypress uses xpath plugin: cy.xpath('...')
            # But for cy.get() we return a CSS selector alternative or the xpath as-is
            return value
        elif by_type_upper == 'CSS_SELECTOR' or by_type_upper == 'CSSSELECTOR':
            return value
        elif by_type_upper == 'CLASS_NAME' or by_type_upper == 'CLASSNAME':
            return f'.{value}'
        elif by_type_upper == 'LINK_TEXT' or by_type_upper == 'LINKTEXT':
            return f'a:contains("{value}")'
        elif by_type_upper == 'PARTIAL_LINK_TEXT' or by_type_upper == 'PARTIALLINKTEXT':
            return f'a:contains("{value}")'
        elif by_type_upper == 'TAG_NAME' or by_type_upper == 'TAGNAME':
            return value
        else:
            # Default to CSS selector
            return value
