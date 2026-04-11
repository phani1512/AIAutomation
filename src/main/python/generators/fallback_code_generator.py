"""
Fallback Code Generator - Self-Healing Test Automation

Generates test code with built-in fallback mechanisms:
- Tries primary locator first
- Falls back to alternative locators if element not found
- Logs which locator worked for debugging
- Supports Java, Python, JavaScript, C#

This creates "self-healing" tests that adapt if the UI changes.
"""

import re
from typing import List, Dict, Optional


class FallbackCodeGenerator:
    """Generate test code with multiple fallback locators."""
    
    def __init__(self):
        self.language_templates = {
            'java': self._generate_java_fallback,
            'python': self._generate_python_fallback,
            'javascript': self._generate_javascript_fallback,
            'csharp': self._generate_csharp_fallback
        }
    
    def generate_with_fallbacks(
        self, 
        primary_match: Dict, 
        alternatives: List[Dict], 
        language: str = 'java',
        max_fallbacks: int = 3
    ) -> str:
        """
        Generate code with fallback logic.
        
        Args:
            primary_match: Best match from dataset
            alternatives: List of alternative matches sorted by confidence
            language: Target language (java, python, javascript, csharp)
            max_fallbacks: Maximum number of fallbacks to include
            
        Returns:
            Generated code with try-catch fallback logic
        """
        generator = self.language_templates.get(language.lower(), self._generate_java_fallback)
        
        # Extract locators from matches
        locators = self._extract_locators(primary_match, alternatives, max_fallbacks)
        
        # Determine action type (click, sendKeys, select, etc.)
        action = self._determine_action(primary_match)
        
        # Generate code
        return generator(locators, action, primary_match)
    
    def _extract_locators(self, primary: Dict, alternatives: List[Dict], max_count: int) -> List[Dict]:
        """Extract unique locators from matches."""
        locators = []
        seen_xpaths = set()
        
        # Add primary locator
        primary_xpath = primary.get('xpath', '')
        if primary_xpath and primary_xpath not in seen_xpaths:
            locators.append({
                'xpath': primary_xpath,
                'strategy': primary.get('strategy', 'unknown'),
                'confidence': primary.get('confidence', 1.0),
                'prompt': primary.get('matched_prompt', '')
            })
            seen_xpaths.add(primary_xpath)
        
        # Add alternative locators
        for alt in alternatives:
            if len(locators) >= max_count:
                break
            
            alt_xpath = alt.get('xpath', '')
            if alt_xpath and alt_xpath not in seen_xpaths:
                locators.append({
                    'xpath': alt_xpath,
                    'strategy': alt.get('strategy', 'unknown'),
                    'confidence': alt.get('confidence', 0.0),
                    'prompt': alt.get('matched_prompt', '')
                })
                seen_xpaths.add(alt_xpath)
        
        return locators
    
    def _determine_action(self, match: Dict) -> Dict:
        """Determine what action to perform on the element."""
        code = match.get('code', '').lower()
        
        if '.click()' in code:
            return {'type': 'click', 'params': []}
        elif '.sendkeys(' in code or '.clear()' in code:
            return {'type': 'sendKeys', 'params': ['{VALUE}']}
        elif 'select' in code and 'selectbyvisibletext' in code:
            return {'type': 'select', 'params': ['{VALUE}']}
        elif '.gettext()' in code or '.getattribute(' in code:
            return {'type': 'getText', 'params': []}
        elif '.submit()' in code:
            return {'type': 'submit', 'params': []}
        else:
            return {'type': 'interact', 'params': []}
    
    def _generate_java_fallback(self, locators: List[Dict], action: Dict, primary_match: Dict) -> str:
        """Generate Java code with fallback logic."""
        if not locators:
            return primary_match.get('code', '')
        
        # If only one locator, return simple code
        if len(locators) == 1:
            return primary_match.get('code', '')
        
        action_type = action['type']
        action_params = action['params']
        
        # Build fallback structure
        lines = []
        lines.append("// Self-healing element finder with fallback locators")
        lines.append("WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));")
        lines.append("WebElement element = null;")
        lines.append("String usedLocator = null;")
        lines.append("")
        
        for i, locator in enumerate(locators):
            xpath_str = locator['xpath']
            confidence = locator['confidence']
            prompt = locator['prompt']
            
            if i == 0:
                lines.append(f"// Primary locator (confidence: {confidence:.2%})")
                lines.append(f"// Matched from: \"{prompt}\"")
                lines.append("try {")
            else:
                lines.append(f"// Fallback #{i} (confidence: {confidence:.2%})")
                lines.append(f"// Matched from: \"{prompt}\"")
                lines.append("if (element == null) {")
                lines.append("    try {")
            
            # Parse and add locator
            indent = "    " if i == 0 else "        "
            locator_code = self._parse_java_locator(xpath_str)
            lines.append(f"{indent}element = wait.until(ExpectedConditions.elementToBeClickable({locator_code}));")
            lines.append(f"{indent}usedLocator = \"Locator {i+1}: {locator_code}\";")
            
            if i == 0:
                lines.append("} catch (TimeoutException | NoSuchElementException e) {")
                lines.append("    System.out.println(\"Primary locator failed, trying fallbacks...\");")
                lines.append("}")
            else:
                lines.append("    } catch (TimeoutException | NoSuchElementException e) {")
                lines.append("        // Continue to next fallback")
                lines.append("    }")
                lines.append("}")
        
        lines.append("")
        lines.append("// Verify element was found")
        lines.append("if (element == null) {")
        lines.append("    throw new NoSuchElementException(\"All fallback locators failed\");")
        lines.append("}")
        lines.append("")
        lines.append("System.out.println(\"Element found using: \" + usedLocator);")
        lines.append("")
        
        # Add action
        if action_type == 'click':
            lines.append("element.click();")
        elif action_type == 'sendKeys':
            lines.append("element.clear();")
            lines.append("element.sendKeys(\"{VALUE}\");")
        elif action_type == 'select':
            lines.append("Select dropdown = new Select(element);")
            lines.append("dropdown.selectByVisibleText(\"{VALUE}\");")
        elif action_type == 'getText':
            lines.append("String text = element.getText();")
        elif action_type == 'submit':
            lines.append("element.submit();")
        
        return '\n'.join(lines)
    
    def _parse_java_locator(self, xpath_str: str) -> str:
        """Parse xpath string from dataset entry."""
        # Examples:
        # By.id("submit")
        # By.xpath("//button[@id='submit']")
        # By.cssSelector(".login-btn")
        
        if not xpath_str or xpath_str == 'N/A':
            return 'By.xpath("//body")'  # Fallback
        
        # If already in By.xxx format, return as-is
        if xpath_str.startswith('By.'):
            return xpath_str
        
        # Otherwise assume it's a raw xpath
        return f'By.xpath("{xpath_str}")'
    
    def _generate_python_fallback(self, locators: List[Dict], action: Dict, primary_match: Dict) -> str:
        """Generate Python code with fallback logic."""
        if not locators or len(locators) == 1:
            return primary_match.get('code', '')
        
        lines = []
        lines.append("# Self-healing element finder with fallback locators")
        lines.append("from selenium.common.exceptions import TimeoutException, NoSuchElementException")
        lines.append("from selenium.webdriver.support.ui import WebDriverWait")
        lines.append("from selenium.webdriver.support import expected_conditions as EC")
        lines.append("")
        lines.append("element = None")
        lines.append("used_locator = None")
        lines.append("")
        
        for i, locator in enumerate(locators):
            xpath_str = self._parse_python_locator(locator['xpath'])
            confidence = locator['confidence']
            
            if i == 0:
                lines.append(f"# Primary locator (confidence: {confidence:.2%})")
                lines.append("try:")
            else:
                lines.append(f"# Fallback #{i} (confidence: {confidence:.2%})")
                lines.append("if element is None:")
                lines.append("    try:")
            
            indent = "    " if i == 0 else "        "
            lines.append(f"{indent}wait = WebDriverWait(driver, 10)")
            lines.append(f"{indent}element = wait.until(EC.element_to_be_clickable({xpath_str}))")
            lines.append(f"{indent}used_locator = 'Locator {i+1}'")
            
            if i == 0:
                lines.append("except (TimeoutException, NoSuchElementException):")
                lines.append("    print('Primary locator failed, trying fallbacks...')")
            else:
                lines.append("    except (TimeoutException, NoSuchElementException):")
                lines.append("        pass")
        
        lines.append("")
        lines.append("if element is None:")
        lines.append("    raise NoSuchElementException('All fallback locators failed')")
        lines.append("")
        lines.append("print(f'Element found using: {used_locator}')")
        lines.append("")
        
        # Add action
        action_type = action['type']
        if action_type == 'click':
            lines.append("element.click()")
        elif action_type == 'sendKeys':
            lines.append("element.clear()")
            lines.append("element.send_keys('{VALUE}')")
        
        return '\n'.join(lines)
    
    def _parse_python_locator(self, xpath_str: str) -> str:
        """Convert Java By.xxx to Python locator format."""
        if not xpath_str or xpath_str == 'N/A':
            return '(By.XPATH, "//body")'
        
        # Parse Java format to Python
        if 'By.id(' in xpath_str:
            id_val = re.search(r'By\.id\(["\'](.+?)["\']\)', xpath_str)
            if id_val:
                return f'(By.ID, "{id_val.group(1)}")'
        
        if 'By.xpath(' in xpath_str:
            xpath_val = re.search(r'By\.xpath\(["\'](.+?)["\']\)', xpath_str)
            if xpath_val:
                return f'(By.XPATH, "{xpath_val.group(1)}")'
        
        if 'By.cssSelector(' in xpath_str:
            css_val = re.search(r'By\.cssSelector\(["\'](.+?)["\']\)', xpath_str)
            if css_val:
                return f'(By.CSS_SELECTOR, "{css_val.group(1)}")'
        
        if 'By.name(' in xpath_str:
            name_val = re.search(r'By\.name\(["\'](.+?)["\']\)', xpath_str)
            if name_val:
                return f'(By.NAME, "{name_val.group(1)}")'
        
        # Default to xpath
        return f'(By.XPATH, "{xpath_str}")'
    
    def _generate_javascript_fallback(self, locators: List[Dict], action: Dict, primary_match: Dict) -> str:
        """Generate JavaScript/WebDriverIO code with fallback logic."""
        if not locators or len(locators) == 1:
            # Convert Java code to JavaScript
            java_code = primary_match.get('code', '')
            return self._convert_java_to_javascript(java_code)
        
        lines = []
        lines.append("// Self-healing element finder with fallback locators")
        lines.append("const { By, until } = require('selenium-webdriver');")
        lines.append("")
        lines.append("let element = null;")
        lines.append("let usedLocator = null;")
        lines.append("")
        
        for i, locator in enumerate(locators):
            xpath_str = self._parse_javascript_locator(locator['xpath'])
            confidence = locator['confidence']
            
            if i == 0:
                lines.append(f"// Primary locator (confidence: {confidence:.2%})")
                lines.append("try {")
            else:
                lines.append(f"// Fallback #{i} (confidence: {confidence:.2%})")
                lines.append("if (!element) {")
                lines.append("    try {")
            
            indent = "    " if i == 0 else "        "
            lines.append(f"{indent}element = await driver.wait(until.elementLocated({xpath_str}), 10000);")
            lines.append(f"{indent}usedLocator = 'Locator {i+1}';")
            
            if i == 0:
                lines.append("} catch (error) {")
                lines.append("    console.log('Primary locator failed, trying fallbacks...');")
                lines.append("}")
            else:
                lines.append("    } catch (error) {")
                lines.append("        // Continue to next fallback")
                lines.append("    }")
                lines.append("}")
        
        lines.append("")
        lines.append("if (!element) {")
        lines.append("    throw new Error('All fallback locators failed');")
        lines.append("}")
        lines.append("")
        lines.append("console.log('Element found using: ' + usedLocator);")
        lines.append("")
        
        # Add action
        action_type = action['type']
        if action_type == 'click':
            lines.append("await element.click();")
        elif action_type == 'sendKeys':
            lines.append("await element.clear();")
            lines.append("await element.sendKeys('{VALUE}');")
        
        return '\n'.join(lines)
    
    def _parse_javascript_locator(self, xpath_str: str) -> str:
        """Convert Java By.xxx to JavaScript locator format."""
        if not xpath_str or xpath_str == 'N/A':
            return 'By.xpath("//body")'
        
        if xpath_str.startswith('By.'):
            # Convert Java By.id("x") to By.id("x")
            return xpath_str
        
        return f'By.xpath("{xpath_str}")'
    
    def _convert_java_to_javascript(self, java_code: str) -> str:
        """Simple Java to JavaScript conversion."""
        js_code = java_code
        js_code = js_code.replace('WebDriverWait', 'await driver.wait')
        js_code = js_code.replace('driver.findElement', 'await driver.findElement')
        js_code = js_code.replace('.click()', 'await .click()')
        js_code = js_code.replace('.sendKeys(', 'await .sendKeys(')
        return js_code
    
    def _generate_csharp_fallback(self, locators: List[Dict], action: Dict, primary_match: Dict) -> str:
        """Generate C# code with fallback logic."""
        if not locators or len(locators) == 1:
            # Convert Java code to C#
            java_code = primary_match.get('code', '')
            return self._convert_java_to_csharp(java_code)
        
        lines = []
        lines.append("// Self-healing element finder with fallback locators")
        lines.append("WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));")
        lines.append("IWebElement element = null;")
        lines.append("string usedLocator = null;")
        lines.append("")
        
        for i, locator in enumerate(locators):
            xpath_str = locator['xpath']
            confidence = locator['confidence']
            
            if i == 0:
                lines.append(f"// Primary locator (confidence: {confidence:.2%})")
                lines.append("try")
                lines.append("{")
            else:
                lines.append(f"// Fallback #{i} (confidence: {confidence:.2%})")
                lines.append("if (element == null)")
                lines.append("{")
                lines.append("    try")
                lines.append("    {")
            
            indent = "    " if i == 0 else "        "
            locator_code = self._parse_csharp_locator(xpath_str)
            lines.append(f"{indent}element = wait.Until(ExpectedConditions.ElementToBeClickable({locator_code}));")
            lines.append(f"{indent}usedLocator = \"Locator {i+1}\";")
            
            if i == 0:
                lines.append("}")
                lines.append("catch (WebDriverTimeoutException)")
                lines.append("{")
                lines.append("    Console.WriteLine(\"Primary locator failed, trying fallbacks...\");")
                lines.append("}")
            else:
                lines.append("    }")
                lines.append("    catch (WebDriverTimeoutException)")
                lines.append("    {")
                lines.append("        // Continue to next fallback")
                lines.append("    }")
                lines.append("}")
        
        lines.append("")
        lines.append("if (element == null)")
        lines.append("{")
        lines.append("    throw new NoSuchElementException(\"All fallback locators failed\");")
        lines.append("}")
        lines.append("")
        lines.append("Console.WriteLine($\"Element found using: {usedLocator}\");")
        lines.append("")
        
        # Add action
        action_type = action['type']
        if action_type == 'click':
            lines.append("element.Click();")
        elif action_type == 'sendKeys':
            lines.append("element.Clear();")
            lines.append("element.SendKeys(\"{VALUE}\");")
        elif action_type == 'select':
            lines.append("SelectElement dropdown = new SelectElement(element);")
            lines.append("dropdown.SelectByText(\"{VALUE}\");")
        
        return '\n'.join(lines)
    
    def _parse_csharp_locator(self, xpath_str: str) -> str:
        """Parse xpath string for C# format."""
        if not xpath_str or xpath_str == 'N/A':
            return 'By.XPath("//body")'
        
        if xpath_str.startswith('By.'):
            # Convert method names to Pascal case (id -> Id, xpath -> XPath, etc.)
            xpath_str = xpath_str.replace('By.id(', 'By.Id(')
            xpath_str = xpath_str.replace('By.xpath(', 'By.XPath(')
            xpath_str = xpath_str.replace('By.name(', 'By.Name(')
            xpath_str = xpath_str.replace('By.cssSelector(', 'By.CssSelector(')
            xpath_str = xpath_str.replace('By.className(', 'By.ClassName(')
            xpath_str = xpath_str.replace('By.linkText(', 'By.LinkText(')
            xpath_str = xpath_str.replace('By.partialLinkText(', 'By.PartialLinkText(')
            xpath_str = xpath_str.replace('By.tagName(', 'By.TagName(')
            return xpath_str
        
        return f'By.XPath("{xpath_str}")'
    
    def _convert_java_to_csharp(self, java_code: str) -> str:
        """Simple Java to C# conversion."""
        csharp_code = java_code
        # Method name capitalization
        csharp_code = csharp_code.replace('.click()', '.Click()')
        csharp_code = csharp_code.replace('.sendKeys(', '.SendKeys(')
        csharp_code = csharp_code.replace('.clear()', '.Clear()')
        csharp_code = csharp_code.replace('.getText()', '.Text')
        csharp_code = csharp_code.replace('WebElement ', 'IWebElement ')
        csharp_code = csharp_code.replace('Duration.ofSeconds(', 'TimeSpan.FromSeconds(')
        return csharp_code
