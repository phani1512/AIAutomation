"""
Smart Prompt Handler - Integrates NLP + Element Resolver + Code Generation

This enhances the code generation to:
1. Accept ANY natural language input (conversational English)
2. Parse intent using NLP processor
3. Automatically discover element locators
4. Generate working Selenium code

Usage in API:
POST /generate
{
    "prompt": "I want to click on the login button",
    "url": "https://example.com"
}

Response:
{
    "code": "driver.find_element(By.ID, 'login-button').click()",
    "parsed": {
        "action": "click",
        "element": "loginButton",
        "confidence": "high"
    },
    "element_discovered": {
        "name": "loginButton",
        "locator": "By.ID('login-button')"
    }
}
"""

import logging
from typing import Dict, Optional
from .natural_language_processor import NaturalLanguageProcessor
from self_healing.element_resolver import ElementResolver

logger = logging.getLogger(__name__)


class SmartPromptHandler:
    """
    Handles ANY natural language prompts with automatic element resolution.
    """
    
    def __init__(self, browser_executor):
        self.browser_executor = browser_executor
        self.resolver = None
        self.nlp = NaturalLanguageProcessor()
    
    def process_prompt(self, prompt: str, url: Optional[str] = None) -> Dict:
        """ANY natural language prompt and generate code.
        
        Args:
            prompt: Natural language (ANY format) - e.g.:
                   - "I want to click on the login button"
                   - "Please type test@email.com in username field"
                   - "click loginButton" (formatted)
            url: Optional URL to navigate to first
        
        Returns:
            {
                'code': 'generated Selenium code',
                'parsed': {'action': 'click', 'element': 'loginButton', ...},
                'resolved_element': {...},
                'success': True/False,
                'message': 'status message'
            }
        """
        result = {
            'code': '',
            'parsed': None,
            'resolved_element': None,
            'success': False,
            'message': ''
        }
        
        try:
            # Step 1: Parse natural language to extract intent
            logger.info(f"[SMART] Parsing natural language: {prompt}")
            parsed = self.nlp.parse(prompt)
            result['parsed'] = parsed
            
            if not parsed['element']:
                result['message'] = f"Could not understand which element to interact with from: '{prompt}'"
                logger.warning(f"[SMART] {result['message']}")
                return result
            
            logger.info(f"[SMART] Parsed → Action: {parsed['action']}, Element: {parsed['element']}, Confidence: {parsed['confidence']}")
            
            # Step 2: Initialize driver if needed
            if not self.browser_executor.driver:
                logger.info("[SMART] Initializing browser...")
                self.browser_executor.initialize_driver(headless=False)
            
            # Step 3: Navigate to URL if provided
            if url:
                logger.info(f"[SMART] Navigating to: {url}")
                self.browser_executor.driver.get(url)
                import time
                time.sleep(2)  # Wait for page load
            
            # Step 4: Initialize element resolver with current driver
            self.resolver = ElementResolver(self.browser_executor.driver)
            
            # Step 5: Format parsed result for element resolver
            formatted_prompt = self.nlp.format_for_element_resolver(parsed)
            logger.info(f"[SMART] Formatted for resolver: {formatted_prompt}")
            
            # Step 6: Resolve element from formatted prompt
            resolved = self.resolver.resolve_prompt_with_element(formatted_prompt)
            
            if not resolved['success']:
                result['message'] = f"Could not find element '{resolved['element_name']}' on page"
                logger.warning(f"[SMART] {result['message']}")
                return result
            
            result['resolved_element'] = {
                'name': resolved['element_name'],
                'locator_type': resolved['locator_type'],
                'locator_value': resolved['locator_value'],
                'original_prompt': resolved['original_prompt'],
                'generic_prompt': resolved['generic_prompt']
            }
            
            # Generate Selenium code using parsed action and value
            code = self._generate_code(parsed, resolved)
            result['code'] = code
            result['success'] = True
            result['message'] = f"Successfully resolved '{resolved['element_name']}' and generated code"
            
            logger.info(f"[SMART] Success! Generated code for: {resolved['element_name']}")
            return result
            
        except Exception as e:
            logger.error(f"[SMART] Error processing prompt: {e}")
            result['message'] = f"Error: {str(e)}"
            return result
    
    def _generate_code(self, parsed: Dict, resolved: Dict) -> str:
        """
        Generate Selenium code using AI generator with template substitution.
        
        **CRITICAL FIX**: Now uses AI generator instead of hardcoded templates!
        This enables:
        - Template parameter substitution (e.g., "click Beneficiaries button" → use template)
        - Compact mode (70% smaller code)
        - Self-healing selectors with fallbacks
        - Dynamic handling for ALL prompts
        
        Args:
            parsed: NLP parsed result with action, element, value
            resolved: Element resolver result with locator details
        """
        original_prompt = parsed.get('original_prompt', '').strip()
        
        if not original_prompt:
            logger.warning("[SMART] No original_prompt found, falling back to hardcoded generation")
            return self._generate_code_fallback(parsed, resolved)
        
        try:
            # Use AI generator to generate code from natural language prompt
            # This leverages templates, parameter substitution, and all our fixes!
            logger.info(f"[SMART] Using AI generator for: {original_prompt}")
            
            # Lazy import to avoid circular dependency
            import requests
            
            # Call /generate endpoint with compact mode and fallbacks enabled
            payload = {
                "prompt": original_prompt,
                "language": "python",
                "with_fallbacks": True,  # Enable self-healing
                "compact_mode": True      # Enable 70% smaller code
            }
            
            # Use localhost API endpoint
            response = requests.post("http://localhost:5002/generate", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                generated_code = result.get('generated', '')
                
                if generated_code:
                    logger.info(f"[SMART] ✅ AI generated {len(generated_code)} chars of code")
                    # Strip comments and return just the executable code
                    return generated_code
                else:
                    logger.warning("[SMART] AI returned empty code, using fallback")
                    return self._generate_code_fallback(parsed, resolved)
            else:
                logger.warning(f"[SMART] AI API returned {response.status_code}, using fallback")
                return self._generate_code_fallback(parsed, resolved)
                
        except Exception as e:
            logger.error(f"[SMART] AI generation failed: {e}, using fallback")
            return self._generate_code_fallback(parsed, resolved)
    
    def _generate_code_fallback(self, parsed: Dict, resolved: Dict) -> str:
        """Fallback hardcoded generation if AI fails (old implementation)."""
        locator_type = resolved['locator_type']
        locator_value = resolved['locator_value']
        element_var = f"elem_{resolved['element_name']}"
        action = parsed['action']
        value = parsed.get('value')
        
        # Map By types to string
        by_str = str(locator_type).replace('By.', 'By.')
        
        code_lines = []
        code_lines.append(f"# {parsed['original_prompt']}")
        code_lines.append(f"from selenium.webdriver.common.by import By")
        code_lines.append(f"")
        
        if action == 'click':
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"# Scroll to element (exactly like Java scrollToView)")
            code_lines.append(f"driver.execute_script(\"arguments[0].scrollIntoView(false);\", {element_var})")
            code_lines.append(f"time.sleep(0.5)")
            code_lines.append(f"{element_var}.click()")
            
        elif action == 'type':
            # Use parsed value or default
            input_value = value if value else "your_value_here"
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"# Scroll to element (exactly like Java scrollToView)")
            code_lines.append(f"driver.execute_script(\"arguments[0].scrollIntoView(false);\", {element_var})")
            code_lines.append(f"time.sleep(0.5)")
            code_lines.append(f"{element_var}.clear()")
            code_lines.append(f"time.sleep(0.2)")
            code_lines.append(f"{element_var}.send_keys('{input_value}')")
            
        elif action == 'get':
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"text = {element_var}.text")
            code_lines.append(f"print(f'Text from {resolved['element_name']}: {{text}}')")
            
        elif action == 'verify':
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"# Scroll to element (exactly like Java scrollToView)")
            code_lines.append(f"driver.execute_script(\"arguments[0].scrollIntoView(false);\", {element_var})")
            code_lines.append(f"time.sleep(0.5)")
            # Check original prompt for specific verification type
            if 'displayed' in parsed['original_prompt'].lower() or 'visible' in parsed['original_prompt'].lower():
                code_lines.append(f"assert {element_var}.is_displayed(), '{resolved['element_name']} is not displayed'")
            elif 'enabled' in parsed['original_prompt'].lower():
                code_lines.append(f"assert {element_var}.is_enabled(), '{resolved['element_name']} is not enabled'")
            else:
                code_lines.append(f"assert {element_var} is not None, '{resolved['element_name']} not found'")
        
        elif action == 'select':
            select_value = value if value else "option_text"
            code_lines.append(f"from selenium.webdriver.support.ui import Select")
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"# Scroll to element (exactly like Java scrollToView)")
            code_lines.append(f"driver.execute_script(\"arguments[0].scrollIntoView(false);\", {element_var})")
            code_lines.append(f"time.sleep(0.5)")
            code_lines.append(f"Select({element_var}).select_by_visible_text('{select_value}')")
            
        elif action == 'wait':
            code_lines.append(f"from selenium.webdriver.support.ui import WebDriverWait")
            code_lines.append(f"from selenium.webdriver.support import expected_conditions as EC")
            code_lines.append(f"wait = WebDriverWait(driver, 10)")
            code_lines.append(f"{element_var} = wait.until(EC.presence_of_element_located(({by_str}, '{locator_value}')))")
        
        elif action == 'hover':
            code_lines.append(f"from selenium.webdriver.common.action_chains import ActionChains")
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"# Scroll to element (exactly like Java scrollToView)")
            code_lines.append(f"driver.execute_script(\"arguments[0].scrollIntoView(false);\", {element_var})")
            code_lines.append(f"time.sleep(0.5)")
            code_lines.append(f"ActionChains(driver).move_to_element({element_var}).perform()")
        
        else:
            # Default to click for unknown actions
            code_lines.append(f"{element_var} = driver.find_element({by_str}, '{locator_value}')")
            code_lines.append(f"{element_var}.click()")
        
        return '\n'.join(code_lines)


# Example usage
def example_usage():
    """
    Show how SmartPromptHandler works with NATURAL LANGUAGE.
    """
    from browser.browser_executor import BrowserExecutor
    
    # Initialize
    browser_executor = BrowserExecutor()
    handler = SmartPromptHandler(browser_executor)
    
    # Natural language prompts (conversational English!)
    prompts = [
        ("I want to click on the login button", "https://www.saucedemo.com/"),
        ("Please type testuser in the username field", None),
        ("Can you enter secret_sauce in the password box?", None),
        ("Hit the login button", None),
    ]
    
    print("\n" + "=" * 80)
    print("SMART PROMPT HANDLER - NATURAL LANGUAGE EXAMPLES")
    print("=" * 80)
    
    for prompt, url in prompts:
        print(f"\n📝 Natural Prompt: '{prompt}'")
        if url:
            print(f"🌐 URL: {url}")
        
        result = handler.process_prompt(prompt, url)
        
        if result['success']:
            print(f"✅ {result['message']}")
            
            # Show NLP parsing
            print(f"\n🧠 Understood:")
            parsed = result['parsed']
            print(f"   Action: {parsed['action']}")
            print(f"   Element: {parsed['element']}")
            if parsed.get('value'):
                print(f"   Value: {parsed['value']}")
            print(f"   Confidence: {parsed['confidence']}")
            
            # Show element resolution
            print(f"\n📍 Found Element:")
            elem = result['resolved_element']
            print(f"   Name: {elem['name']}")
            print(f"   Locator: {elem['locator_type']}('{elem['locator_value']}')")
            
            # Show generated code
            print(f"\n💻 Generated Code:")
            print("   " + "\n   ".join(result['code'].split('\n')))
        else:
            print(f"❌ {result['message']}")
    
    print("\n" + "=" * 80)
    
    # Cleanup
    if browser_executor.driver:
        browser_executor.driver.quit()


if __name__ == "__main__":
    example_usage()
