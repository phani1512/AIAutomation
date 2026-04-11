"""
Universal Input Pattern Handler
Handles "enter {value} in {field}" patterns for any field dynamically.
"""
import re


class UniversalPatternHandler:
    """Handles universal input patterns like 'enter X in Y' for any field."""
    
    def __init__(self, locator_utils):
        """Initialize with locator_utils for selector generation."""
        self.locator_utils = locator_utils
    
    def handle_universal_input_pattern(self, prompt: str, language: str, comprehensive_mode: bool, preserve_placeholder: bool = False) -> str:
        """UNIVERSAL handler for 'enter {value} in {field}' pattern - works for ANY field dynamically.
        
        Examples:
            "enter john@email.com in email" → extracts value="john@email.com", field="email"
            "enter john123 in username" → extracts value="john123", field="username"
            "enter secret in password" → extracts value="secret", field="password"
            "type 555-1234 in phone" → extracts value="555-1234", field="phone"
        
        Args:
            prompt: User's prompt with pattern "enter VALUE in FIELD"
            language: Target language (python, java, javascript, csharp)
            comprehensive_mode: Whether to generate comprehensive code
            preserve_placeholder: Whether to keep {VALUE} placeholder for Test Builder
        
        Returns:
            Generated code string, or None if pattern doesn't match
        """
        # Pattern: "enter/type/input VALUE in FIELD"
        pattern = r'(?:enter|type|input|fill)\s+(.+?)\s+in\s+(.+?)(?:\s+field|\s+box)?$'
        match = re.search(pattern, prompt, re.IGNORECASE)
        
        if not match:
            return None
        
        # Extract VALUE and FIELD
        value = match.group(1).strip()
        field_name = match.group(2).strip()
        
        # Strip surrounding quotes if present
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        
        print(f"[UNIVERSAL INPUT] ✅ Detected pattern: enter '{value}' in '{field_name}'")
        
        # Generic placeholder words that should use {VALUE} placeholder instead
        generic_placeholders = [
            'text', 'data', 'value', 'information', 'content', 'input',
            'string', 'characters', 'words', 'details', 'info'
        ]
        
        # Check if value is a generic placeholder word or if preserve_placeholder is True
        if value.lower() in generic_placeholders or preserve_placeholder:
            value = "{VALUE}"
            print(f"[UNIVERSAL INPUT] Using {{VALUE}} placeholder")
        
        # Generate dynamic field selector (multiple fallback strategies)
        selectors = self.locator_utils.generate_field_selectors(field_name)
        
        print(f"[UNIVERSAL INPUT] Generated {len(selectors)} fallback selectors for '{field_name}'")
        for i, sel in enumerate(selectors[:3], 1):  # Show first 3
            print(f"[UNIVERSAL INPUT]   {i}. {sel}")
        print(f"[UNIVERSAL INPUT] Generating {language} code with fallback support (comprehensive={comprehensive_mode})")
        
        # Generate code based on language with MULTIPLE FALLBACK SELECTORS
        code = self._generate_with_fallbacks(field_name, value, selectors, language, comprehensive_mode)
        
        if code:
            print(f"[UNIVERSAL INPUT] ✅ Generated code successfully")
        return code
    
    def _generate_with_fallbacks(self, field_name: str, value: str, selectors: list, language: str, comprehensive_mode: bool) -> str:
        """Generate code with fallback selectors for any language."""
        if language == 'python':
            return self._generate_python(field_name, value, selectors, comprehensive_mode)
        elif language == 'java':
            return self._generate_java(field_name, value, selectors, comprehensive_mode)
        elif language == 'javascript':
            return self._generate_javascript(field_name, value, selectors, comprehensive_mode)
        elif language == 'csharp':
            return self._generate_csharp(field_name, value, selectors, comprehensive_mode)
        return None
    
    def _generate_python(self, field_name: str, value: str, selectors: list, comprehensive_mode: bool) -> str:
        """Generate Python code that tries multiple selectors with fallback."""
        comment = f"# Enter '{value}' in {field_name} field with multiple fallback selectors\n" if comprehensive_mode else ""
        
        code_lines = [comment.rstrip()]
        code_lines.append("# Try multiple selector strategies until one works")
        code_lines.append("wait = WebDriverWait(driver, 10)")
        code_lines.append("element = None")
        code_lines.append(f"selectors = {selectors[:5]}")
        code_lines.append("for selector in selectors:")
        code_lines.append("    try:")
        code_lines.append("        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))")
        code_lines.append("        break")
        code_lines.append("    except:")
        code_lines.append("        continue")
        code_lines.append("if element:")
        code_lines.append("    element.clear()")
        code_lines.append(f"    element.send_keys(\"{value}\")")
        code_lines.append("else:")
        code_lines.append(f"    raise Exception(\"Could not find {field_name} field with any selector\")")
        
        return "\n".join(code_lines)
    
    def _generate_java(self, field_name: str, value: str, selectors: list, comprehensive_mode: bool) -> str:
        """Generate Java code that tries multiple selectors with fallback."""
        comment = f"// Enter '{value}' in {field_name} field with multiple fallback selectors\n" if comprehensive_mode else ""
        
        code_lines = [comment.rstrip()]
        code_lines.append("// Try multiple selector strategies until one works")
        code_lines.append("WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));")
        code_lines.append("WebElement element = null;")
        code_lines.append(f"String[] selectors = {{\"{selectors[0]}\", \"{selectors[1]}\", \"{selectors[2]}\", \"{selectors[3]}\", \"{selectors[4]}\"}};")
        code_lines.append("for (String selector : selectors) {")
        code_lines.append("    try {")
        code_lines.append("        element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(selector)));")
        code_lines.append("        break;")
        code_lines.append("    } catch (Exception e) {")
        code_lines.append("        continue;")
        code_lines.append("    }")
        code_lines.append("}")
        code_lines.append("if (element != null) {")
        code_lines.append("    element.clear();")
        code_lines.append(f"    element.sendKeys(\"{value}\");")
        code_lines.append("} else {")
        code_lines.append(f"    throw new Exception(\"Could not find {field_name} field with any selector\");")
        code_lines.append("}")
        
        return "\n".join(code_lines)
    
    def _generate_javascript(self, field_name: str, value: str, selectors: list, comprehensive_mode: bool) -> str:
        """Generate JavaScript code that tries multiple selectors with fallback."""
        comment = f"// Enter '{value}' in {field_name} field with multiple fallback selectors\n" if comprehensive_mode else ""
        
        code_lines = [comment.rstrip()]
        code_lines.append("// Try multiple selector strategies until one works")
        code_lines.append(f"const selectors = {selectors[:5]};")
        code_lines.append("let element = null;")
        code_lines.append("for (const selector of selectors) {")
        code_lines.append("    try {")
        code_lines.append("        element = await driver.wait(until.elementLocated(By.css(selector)), 10000);")
        code_lines.append("        await driver.wait(until.elementIsVisible(element), 10000);")
        code_lines.append("        break;")
        code_lines.append("    } catch (e) {")
        code_lines.append("        continue;")
        code_lines.append("    }")
        code_lines.append("}")
        code_lines.append("if (element) {")
        code_lines.append("    await element.clear();")
        code_lines.append(f"    await element.sendKeys(\"{value}\");")
        code_lines.append("} else {")
        code_lines.append(f"    throw new Error(\"Could not find {field_name} field with any selector\");")
        code_lines.append("}")
        
        return "\n".join(code_lines)
    
    def _generate_csharp(self, field_name: str, value: str, selectors: list, comprehensive_mode: bool) -> str:
        """Generate C# code that tries multiple selectors with fallback."""
        comment = f"// Enter '{value}' in {field_name} field with multiple fallback selectors\n" if comprehensive_mode else ""
        
        code_lines = [comment.rstrip()]
        code_lines.append("// Try multiple selector strategies until one works")
        code_lines.append("var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));")
        code_lines.append("IWebElement element = null;")
        code_lines.append(f"string[] selectors = {{ \"{selectors[0]}\", \"{selectors[1]}\", \"{selectors[2]}\", \"{selectors[3]}\", \"{selectors[4]}\" }};")
        code_lines.append("foreach (var selector in selectors)")
        code_lines.append("{")
        code_lines.append("    try")
        code_lines.append("    {")
        code_lines.append("        element = wait.Until(ExpectedConditions.ElementToBeClickable(By.CssSelector(selector)));")
        code_lines.append("        break;")
        code_lines.append("    }")
        code_lines.append("    catch")
        code_lines.append("    {")
        code_lines.append("        continue;")
        code_lines.append("    }")
        code_lines.append("}")
        code_lines.append("if (element != null)")
        code_lines.append("{")
        code_lines.append("    element.Clear();")
        code_lines.append(f"    element.SendKeys(\"{value}\");")
        code_lines.append("}")
        code_lines.append("else")
        code_lines.append("{")
        code_lines.append(f"    throw new Exception(\"Could not find {field_name} field with any selector\");")
        code_lines.append("}")
        
        return "\n".join(code_lines)
