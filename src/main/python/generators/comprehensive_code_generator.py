"""
Comprehensive Code Generator - Generates production-ready Selenium code with waits and error handling.
This module provides comprehensive code generation for ALL prompts, not just custom helpers.
"""
import json
import os
import re


class ComprehensiveCodeGenerator:
    """Generates comprehensive Selenium code with WebDriverWait and multiple strategies."""
    
    def __init__(self, patterns_path: str = None):
        """Initialize with custom helper patterns from dataset."""
        if patterns_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
            patterns_path = os.path.join(project_root, 'resources', 'ml_data', 'datasets', 'custom-helper-patterns.json')
        
        self.patterns = []
        if os.path.exists(patterns_path):
            with open(patterns_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', [])
        
        print(f"[COMPREHENSIVE] Loaded {len(self.patterns)} pattern categories")
    
    def enhance_to_comprehensive(self, simple_code: str, prompt: str, language: str = 'java') -> str:
        """
        Convert ANY simple code to comprehensive code with waits and error handling.
        This is the UNIVERSAL method that works for all prompts.
        
        Args:
            simple_code: Simple Selenium code (e.g., driver.findElement(By.id("btn")).click())
            prompt: Original user prompt for context
            language: Target language (java, python, javascript, csharp)
        
        Returns:
            Comprehensive code with WebDriverWait and multiple strategies
        """
        # Parse the simple code to extract action and locator
        parsed = self._parse_simple_code(simple_code)
        
        if not parsed:
            # Can't parse - return as-is
            print(f"[COMPREHENSIVE] Could not parse code: {simple_code[:100]}")
            return simple_code
        
        action = parsed['action']
        locator_method = parsed.get('locator_method', 'id')
        locator_value = parsed.get('locator_value', 'elementId')
        value = parsed.get('value')  # For sendKeys actions
        
        # Generate comprehensive code based on action
        if action == 'click':
            return self._generate_click(locator_method, locator_value, prompt, language)
        elif action == 'sendKeys':
            return self._generate_input(locator_method, locator_value, value or 'value', prompt, language)
        elif action == 'select':
            return self._generate_select(locator_method, locator_value, value or 'option', language)
        elif action == 'getText':
            return self._generate_get_text(locator_method, locator_value, language)
        elif action == 'getCount':
            return self._generate_get_count(locator_method, locator_value, language)
        elif action == 'isEnabled':
            return self._generate_is_enabled(locator_method, locator_value, language)
        elif action == 'isDisplayed':
            return self._generate_is_displayed(locator_method, locator_value, language)
        elif action == 'verify':
            return self._generate_verify(locator_method, locator_value, prompt, language)
        elif action == 'navigate':
            return self._generate_navigate(locator_value, language)
        else:
            # Default to click for unknown actions
            return self._generate_click(locator_method, locator_value, prompt, language)
    
    def _parse_simple_code(self, code: str) -> dict:
        """Parse simple Selenium code to extract action and locator."""
        code_lower = code.lower()
        
        # Detect action type
        if '.click()' in code_lower:
            action = 'click'
        elif '.sendkeys(' in code_lower or '.send_keys(' in code_lower:
            action = 'sendKeys'
            # Extract value from sendKeys("value")
            value_match = re.search(r'\.sendKeys\(["\']([^"\']+)["\']\)', code, re.IGNORECASE)
            value = value_match.group(1) if value_match else None
        elif '.gettext()' in code_lower:
            action = 'getText'
        elif '.isenabled()' in code_lower:
            action = 'isEnabled'
        elif '.isdisplayed()' in code_lower:
            action = 'isDisplayed'
        elif 'findelements(' in code_lower and ('rows' in code_lower or 'count' in code_lower or '.size()' in code_lower):
            action = 'getCount'
        elif 'select' in code_lower and '.selectbyvisibletext(' in code_lower:
            action = 'select'
            value_match = re.search(r'selectByVisibleText\(["\']([^"\']+)["\']\)', code, re.IGNORECASE)
            value = value_match.group(1) if value_match else None
        elif '.get(' in code_lower or 'navigate' in code_lower:
            action = 'navigate'
            url_match = re.search(r'\.get\(["\']([^"\']+)["\']\)', code)
            return {
                'action': 'navigate',
                'locator_value': url_match.group(1) if url_match else 'https://example.com'
            }
        elif 'assert' in code_lower or 'verify' in code_lower:
            action = 'verify'
        else:
            # Default to click
            action = 'click'
        
        # Extract locator: By.method("value") or By.method('value')
        # Support both findElement and findElements
        # Handle escaped quotes inside the locator value
        
        # Try to match By.method("value") - handle escaped quotes
        locator_match = re.search(r'By\.(\w+)\((["\'])(.+?(?<!\\))\2\)', code, re.IGNORECASE | re.DOTALL)
        if locator_match:
            locator_method = locator_match.group(1).lower()
            locator_value = locator_match.group(3)
            # Unescape any escaped quotes (\" -> ")
            locator_value = locator_value.replace('\\"', '"').replace("\\'", "'")
        else:
            # Try Python style: By.ID, "value"
            locator_match = re.search(r'By\.([A-Z_]+),\s*(["\'])(.+?)\2', code)
            if locator_match:
                method_map = {'ID': 'id', 'NAME': 'name', 'XPATH': 'xpath', 'CSS_SELECTOR': 'cssSelector'}
                locator_method = method_map.get(locator_match.group(1), 'id')
                locator_value = locator_match.group(3)
                # Unescape any escaped quotes
                locator_value = locator_value.replace('\\"', '"').replace("\\'", "'")
            else:
                # Last resort: Try to find any quoted string that looks like a locator
                # Handle escaped quotes properly
                quoted_match = re.search(r'(["\'])(.+?(?<!\\))\1', code)
                if quoted_match:
                    value = quoted_match.group(2)
                    # Unescape any escaped quotes
                    value = value.replace('\\"', '"').replace("\\'", "'")
                    if '/' in value:
                        locator_method = 'xpath'
                        locator_value = value
                    else:
                        locator_method = 'id'
                        locator_value = value
                else:
                    locator_method = 'id'
                    locator_value = 'elementId'
        
        result = {
            'action': action,
            'locator_method': locator_method,
            'locator_value': locator_value
        }
        
        if action == 'sendKeys' and 'value' in locals():
            result['value'] = value
        elif action == 'select' and 'value' in locals():
            result['value'] = value
        
        return result
    
    def _format_by_method(self, locator_method: str, language: str) -> str:
        """Format By locator method name for the target language.
        
        Java/JavaScript: id, name, xpath, cssSelector
        Python: By.ID, By.NAME, By.XPATH, By.CSS_SELECTOR  
        C#: Id, Name, XPath, CssSelector
        Cypress: CSS selector format (#id, [name="value"], xpath syntax)
        """
        method_lower = locator_method.lower()
        
        if language == 'python':
            py_map = {'id': 'By.ID', 'name': 'By.NAME', 'cssselector': 'By.CSS_SELECTOR', 'xpath': 'By.XPATH'}
            return py_map.get(method_lower, 'By.ID')
        
        elif language == 'cypress':
            # Cypress uses CSS selector format
            if method_lower == 'id':
                return '#{value}'
            elif method_lower == 'name':
                return '[name="{value}"]'
            elif method_lower == 'cssselector':
                return '{value}'
            elif method_lower == 'xpath':
                return '{value}'  # Return as-is, will be used with cy.xpath() if available
            return '#{value}'
        
        elif language in ['java', 'javascript']:
            # Java and JavaScript use lowercase, except cssSelector
            if method_lower == 'cssselector':
                return 'cssSelector'
            return method_lower
        
        else:  # C#
            # C# capitalizes first letter: Id, Name, XPath, CssSelector
            if method_lower == 'cssselector':
                return 'CssSelector'
            elif method_lower == 'xpath':
                return 'XPath'
            else:
                return locator_method[0].upper() + locator_method[1:]
    
    def _generate_click(self, locator_method: str, locator_value: str, prompt: str, language: str) -> str:
        """Generate comprehensive click code."""
        element_desc = self._extract_element_desc(prompt)
        
        if language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Click {element_desc} with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable(({by_constant}, "{locator_value}")))
element.click()'''
        
        elif language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Click {element_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.{by_method}("{locator_value}")));
element.click();'''
        
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Click {element_desc} with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(element), 10000);
await element.click();'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Click {element_desc} with wait
cy.get('{locator}').should('be.visible').click();'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Click {element_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementToBeClickable(By.{by_method}("{locator_value}")));
element.Click();'''
    
    def _generate_input(self, locator_method: str, locator_value: str, value: str, prompt: str, language: str) -> str:
        """Generate comprehensive input code."""
        field_desc = self._extract_element_desc(prompt)
        
        if language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Enter text in {field_desc} with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located(({by_constant}, "{locator_value}")))
element.clear()
element.send_keys("{value}")'''
        
        elif language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Enter text in {field_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.{by_method}("{locator_value}")));
element.clear();
element.sendKeys("{value}");'''
        
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Enter text in {field_desc} with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(element), 10000);
await element.clear();
await element.sendKeys("{value}");'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Enter text in {field_desc} with wait
cy.get('{locator}').should('be.visible').clear().type("{value}");'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, language)
            return f'''// Enter text in {field_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementIsVisible(By.{by_method}("{locator_value}")));
element.Clear();
element.SendKeys("{value}");'''
    
    def _generate_select(self, locator_method: str, locator_value: str, option: str, language: str) -> str:
        """Generate comprehensive select dropdown code."""
        if language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Select from dropdown with wait
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
dropdown = wait.until(EC.element_to_be_clickable(({by_constant}, "{locator_value}")))
select = Select(dropdown)
select.select_by_visible_text("{option}")'''
        
        elif language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Select from dropdown with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement dropdown = wait.until(ExpectedConditions.elementToBeClickable(By.{by_method}("{locator_value}")));
Select select = new Select(dropdown);
select.selectByVisibleText("{option}");'''
        
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Select from dropdown with wait
let dropdown = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(dropdown), 10000);
let option = await dropdown.findElement(By.xpath("//option[text()='{option}']"));
await option.click();'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Select from dropdown with wait
cy.get('{locator}').should('be.visible').select("{option}");'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Select from dropdown with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement dropdown = wait.Until(ExpectedConditions.ElementToBeClickable(By.{by_method}("{locator_value}")));
SelectElement select = new SelectElement(dropdown);
select.SelectByText("{option}");'''
    
    def _generate_verify(self, locator_method: str, locator_value: str, prompt: str, language: str) -> str:
        """Generate comprehensive verification code."""
        element_desc = self._extract_element_desc(prompt)
        
        if language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Verify {element_desc} with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located(({by_constant}, "{locator_value}")))
assert element.is_displayed()'''
        
        elif language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Verify {element_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.{by_method}("{locator_value}")));
Assert.assertTrue(element.isDisplayed());'''
        
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Verify {element_desc} with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(element), 10000);
assert(await element.isDisplayed());'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Verify {element_desc} with wait
cy.get('{locator}').should('be.visible');'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Verify {element_desc} with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementIsVisible(By.{by_method}("{locator_value}")));
Assert.IsTrue(element.Displayed);'''
    
    def _generate_navigate(self, url: str, language: str) -> str:
        """Generate comprehensive navigation code."""
        if language == 'python':
            return f'''# Navigate to URL with wait for page load
from selenium.webdriver.support.ui import WebDriverWait

driver.get("{url}")
wait = WebDriverWait(driver, 10)
wait.until(lambda d: d.execute_script("return document.readyState") == "complete")'''
        
        elif language == 'java':
            return f'''// Navigate to URL with wait for page load
driver.get("{url}");
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(driver -> ((JavascriptExecutor) driver).executeScript("return document.readyState").equals("complete"));'''
        
        elif language == 'javascript':
            return f'''// Navigate to URL with wait for page load
await driver.get("{url}");
await driver.wait(async () => {{
    let readyState = await driver.executeScript("return document.readyState");
    return readyState === "complete";
}}, 10000);'''
        
        elif language == 'cypress':
            return f'''// Navigate to URL with wait for page load
cy.visit("{url}");
cy.document().should('have.property', 'readyState', 'complete');'''
        
        else:  # C#
            return f'''// Navigate to URL with wait for page load
driver.Navigate().GoToUrl("{url}");
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
wait.Until(d => ((IJavaScriptExecutor)d).ExecuteScript("return document.readyState").Equals("complete"));'''
    
    def _generate_get_text(self, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive getText code with wait."""
        if language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Get text with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.{by_method}("{locator_value}")));
String text = element.getText();'''
        elif language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Get text with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located(({by_constant}, "{locator_value}")))
text = element.text'''
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Get text with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(element), 10000);
let text = await element.getText();'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Get text with wait
cy.get('{locator}').should('be.visible').invoke('text').then(text => {{
    cy.log('Text: ' + text);
}});'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Get text with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementIsVisible(By.{by_method}("{locator_value}")));
string text = element.Text;'''
    
    def _generate_get_count(self, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive count code with wait for multiple elements."""
        if language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Get element count with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
List<WebElement> elements = wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(By.{by_method}("{locator_value}")));
int count = elements.size();'''
        elif language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Get element count with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
elements = wait.until(EC.presence_of_all_elements_located(({by_constant}, "{locator_value}")))
count = len(elements)'''
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Get element count with wait
let elements = await driver.wait(until.elementsLocated(By.{by_method}("{locator_value}")), 10000);
let count = elements.length;'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Get element count with wait
cy.get('{locator}').should('have.length.greaterThan', 0).then($elements => {{
    cy.log('Count: ' + $elements.length);
}});'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Get element count with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
ReadOnlyCollection<IWebElement> elements = wait.Until(ExpectedConditions.PresenceOfAllElementsLocatedBy(By.{by_method}("{locator_value}")));
int count = elements.Count;'''
    
    def _generate_is_enabled(self, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive isEnabled check with wait."""
        if language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Check if element is enabled with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.presenceOfElementLocated(By.{by_method}("{locator_value}")));
boolean isEnabled = element.isEnabled();'''
        elif language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Check if element is enabled with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located(({by_constant}, "{locator_value}")))
is_enabled = element.is_enabled()'''
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Check if element is enabled with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
let isEnabled = await element.isEnabled();'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Check if element is enabled with wait
cy.get('{locator}').should('be.enabled');'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Check if element is enabled with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementExists(By.{by_method}("{locator_value}")));
bool isEnabled = element.Enabled;'''
    
    def _generate_is_displayed(self, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive isDisplayed check with wait."""
        if language == 'java':
            by_method = self._format_by_method(locator_method, 'java')
            return f'''// Check if element is displayed with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.{by_method}("{locator_value}")));
boolean isDisplayed = element.isDisplayed();'''
        elif language == 'python':
            by_constant = self._format_by_method(locator_method, 'python')
            return f'''# Check if element is displayed with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located(({by_constant}, "{locator_value}")))
is_displayed = element.is_displayed()'''
        elif language == 'javascript':
            by_method = self._format_by_method(locator_method, 'javascript')
            return f'''// Check if element is displayed with wait
let element = await driver.wait(until.elementLocated(By.{by_method}("{locator_value}")), 10000);
await driver.wait(until.elementIsVisible(element), 10000);
let isDisplayed = await element.isDisplayed();'''
        
        elif language == 'cypress':
            cypress_selector = self._format_by_method(locator_method, 'cypress')
            locator = cypress_selector.replace('{value}', locator_value)
            return f'''// Check if element is displayed with wait
cy.get('{locator}').should('be.visible');'''
        
        else:  # C#
            by_method = self._format_by_method(locator_method, 'csharp')
            return f'''// Check if element is displayed with wait
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IWebElement element = wait.Until(ExpectedConditions.ElementIsVisible(By.{by_method}("{locator_value}")));
bool isDisplayed = element.Displayed;'''

    
    def _extract_element_desc(self, prompt: str) -> str:
        """Extract a short description of the element from prompt."""
        prompt_lower = prompt.lower()
        
        # Common patterns
        if 'button' in prompt_lower:
            return 'button'
        elif 'login' in prompt_lower:
            return 'login element'
        elif 'email' in prompt_lower:
            return 'email field'
        elif 'password' in prompt_lower:
            return 'password field'
        elif 'submit' in prompt_lower:
            return 'submit button'
        elif 'dropdown' in prompt_lower or 'select' in prompt_lower:
            return 'dropdown'
        elif 'link' in prompt_lower:
            return 'link'
        elif 'tab' in prompt_lower:
            return 'tab'
        elif 'dialog' in prompt_lower:
            return 'dialog'
        elif 'table' in prompt_lower:
            return 'table'
        else:
            return 'element'
