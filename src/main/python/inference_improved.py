"""
Improved inference with better output formatting and cleaning.
VERSION: 2.0.4 - Enhanced Action Suggestions with Confidence Scoring
"""

import pickle
import tiktoken
import re
import json
import os
from train_simple import NGramLanguageModel
from action_suggestion_engine import ActionSuggestionEngine

class ImprovedSeleniumGenerator:
    """Enhanced Selenium code generator with better output quality."""
    
    def __init__(self, model_path: str = 'src/resources/selenium_ngram_model.pkl', silent: bool = False):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.version = "2.0.4-ENHANCED"
        
        if not silent:
            print(f"[INFERENCE] Version {self.version} - Enhanced Action Suggestions")
            print(f"Loading model from {model_path}...")
        self.model = NGramLanguageModel(n=4)
        self.model.load(model_path)
        
        # Initialize enhanced action suggestion engine
        self.action_engine = ActionSuggestionEngine()
        
        # Load datasets for element extraction
        self._load_datasets()
        
        if not silent:
            print(f"[OK] Model loaded successfully!")
            print(f"  Vocabulary size: {len(self.model.vocab)}")
            print(f"  Unique contexts: {len(self.model.ngrams)}")
            print(f"  Dataset entries: {len(self.dataset_cache)}")
            print(f"  Action engine: {len(self.action_engine.action_catalog)} element types\n")
            print()
    
    def _load_datasets(self):
        """Load all datasets to extract element mappings from prompts."""
        self.dataset_cache = {}
        
        # Determine the project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
        dataset_dir = os.path.join(project_root, 'src', 'resources')
        
        datasets = [
            'common-web-actions-dataset.json',
            'sircon_ui_dataset.json',
            'element-locator-patterns.json',
            'selenium-methods-dataset.json'
        ]
        
        for dataset_file in datasets:
            dataset_path = os.path.join(dataset_dir, dataset_file)
            if os.path.exists(dataset_path):
                try:
                    with open(dataset_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Extract prompt -> locator mappings
                        for entry in data:
                            for step in entry.get('steps', []):
                                prompt = step.get('prompt', '').strip().lower()
                                locator = step.get('locator', '')
                                code = step.get('code', '')
                                
                                if prompt and (locator or code):
                                    self.dataset_cache[prompt] = {
                                        'locator': locator,
                                        'code': code,
                                        'element_type': step.get('element_type', ''),
                                        'action': step.get('action', '')
                                    }
                                    # Debug prints removed - cache loads silently
                except Exception as e:
                    print(f"[WARNING] Could not load {dataset_file}: {e}")
    
    def _find_dataset_match(self, prompt: str):
        """Find exact or fuzzy match in dataset cache."""
        prompt_lower = prompt.lower().strip()
        
        # Try exact match first
        if prompt_lower in self.dataset_cache:
            return self.dataset_cache[prompt_lower]
        
        # Try fuzzy matching - find best match by word overlap
        best_match = None
        best_score = 0
        prompt_words = set(prompt_lower.split())
        
        for cached_prompt, data in self.dataset_cache.items():
            cached_words = set(cached_prompt.split())
            overlap = len(prompt_words & cached_words)
            total = len(prompt_words | cached_words)
            score = overlap / total if total > 0 else 0
            
            # Require at least 70% similarity
            if score > best_score and score >= 0.7:
                best_score = score
                best_match = data
        
        return best_match
    
    def _java_to_python_by(self, java_by_method: str) -> str:
        """Convert Java By method names to Python constants."""
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
    
    def _generate_from_locator(self, prompt: str, locator: str, action_type: str, element_type: str, fallback_locators: list = None) -> str:
        """Generate Python Selenium code directly from Java locator string with fallback strategies."""
        # Parse Java locator format: By.method("value")
        locator_match = re.match(r'By\.(\w+)\("([^"]+)"\)', locator)
        if not locator_match:
            locator_match = re.match(r'By\.(\w+)\(\'([^\']+)\'\)', locator)
        
        if not locator_match:
            # Fallback to generic Python format
            return f"""# {prompt}
driver.find_element(By.ID, "elementId").click()"""
        
        by_method = locator_match.group(1)  # Keep original case (id, cssSelector, linkText, etc.)
        locator_value = locator_match.group(2)
        
        # Convert Java By method names to Python constants
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
        
        python_by_method = by_mapping.get(by_method, f'By.{by_method.upper()}')
        
        # Determine if we need fallback strategies
        # Use fallback if: custom fallbacks provided OR it's a linkText/partialLinkText
        has_custom_fallbacks = fallback_locators and len(fallback_locators) > 0
        use_auto_fallback = by_method in ['linkText', 'partialLinkText']
        use_fallback = has_custom_fallbacks or use_auto_fallback
        
        # Generate Python code based on action type
        if action_type == 'sendKeys' or 'enter' in prompt.lower() or 'type' in prompt.lower():
            # Extract value from prompt
            value = self._extract_input_value(prompt)
            return f"""# Enter text in {element_type} field
driver.find_element({python_by_method}, "{locator_value}").clear()
driver.find_element({python_by_method}, "{locator_value}").send_keys("{value}")"""
        
        elif action_type == 'click' or 'click' in prompt.lower():
            if use_fallback:
                # Build fallback strategies
                strategies = []
                strategy_num = 1
                
                # Strategy 1: Primary locator
                strategies.append(f"""# Strategy {strategy_num}: Primary locator
try:
    element = wait.until(EC.element_to_be_clickable(({python_by_method}, "{locator_value}")))
    element.click()
    element_found = True
except:
    pass""")
                strategy_num += 1
                
                # Add custom fallback locators if provided
                if has_custom_fallbacks:
                    for fb_locator in fallback_locators:
                        # Parse fallback locator
                        fb_match = re.match(r'By\.(\w+)\("([^"]+)"\)', fb_locator)
                        if not fb_match:
                            fb_match = re.match(r'By\.(\w+)\(\'([^\']+)\'\)', fb_locator)
                        
                        if fb_match:
                            fb_by_method = fb_match.group(1)
                            fb_locator_value = fb_match.group(2)
                            fb_python_by = by_mapping.get(fb_by_method, f'By.{fb_by_method.upper()}')
                            
                            strategies.append(f"""
# Strategy {strategy_num}: Fallback - {fb_locator}
if not element_found:
    try:
        element = wait.until(EC.element_to_be_clickable(({fb_python_by}, "{fb_locator_value}")))
        element.click()
        element_found = True
    except:
        pass""")
                            strategy_num += 1
                
                # Add automatic fallbacks for linkText/partialLinkText
                if use_auto_fallback:
                    strategies.append(f"""
# Strategy {strategy_num}: Try as button with normalize-space
if not element_found:
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), '{locator_value}')]")))
        element.click()
        element_found = True
    except:
        pass""")
                    strategy_num += 1
                    
                    strategies.append(f"""
# Strategy {strategy_num}: Try any element with text
if not element_found:
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(normalize-space(.), '{locator_value}')]")))
    element.click()""")
                
                # Combine all strategies
                code = f"""# Click {element_type} - trying multiple strategies
element_found = False
wait = WebDriverWait(driver, 5)

{chr(10).join(strategies)}"""
                return code
            else:
                return f"""# Click {element_type}
driver.find_element({python_by_method}, "{locator_value}").click()"""
        
        elif action_type == 'getText' or 'get' in prompt.lower() or 'retrieve' in prompt.lower():
            return f"""# Get text from {element_type}
text = driver.find_element({python_by_method}, "{locator_value}").text"""
        
        else:
            # Default to click with same fallback logic
            if use_fallback:
                # Build fallback strategies (same as click action)
                strategies = []
                strategy_num = 1
                
                # Strategy 1: Primary locator
                strategies.append(f"""# Strategy {strategy_num}: Primary locator
try:
    element = wait.until(EC.element_to_be_clickable(({python_by_method}, "{locator_value}")))
    element.click()
    element_found = True
except:
    pass""")
                strategy_num += 1
                
                # Add custom fallback locators if provided
                if has_custom_fallbacks:
                    for fb_locator in fallback_locators:
                        fb_match = re.match(r'By\.(\w+)\("([^"]+)"\)', fb_locator)
                        if not fb_match:
                            fb_match = re.match(r'By\.(\w+)\(\'([^\']+)\'\)', fb_locator)
                        
                        if fb_match:
                            fb_by_method = fb_match.group(1)
                            fb_locator_value = fb_match.group(2)
                            fb_python_by = by_mapping.get(fb_by_method, f'By.{fb_by_method.upper()}')
                            
                            strategies.append(f"""
# Strategy {strategy_num}: Fallback - {fb_locator}
if not element_found:
    try:
        element = wait.until(EC.element_to_be_clickable(({fb_python_by}, "{fb_locator_value}")))
        element.click()
        element_found = True
    except:
        pass""")
                            strategy_num += 1
                
                # Add automatic fallbacks for linkText/partialLinkText
                if use_auto_fallback:
                    strategies.append(f"""
# Strategy {strategy_num}: Try as button with normalize-space
if not element_found:
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), '{locator_value}')]")))
        element.click()
        element_found = True
    except:
        pass""")
                    strategy_num += 1
                    
                    strategies.append(f"""
# Strategy {strategy_num}: Try any element with text
if not element_found:
    element = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(normalize-space(.), '{locator_value}')]")))
    element.click()""")
                
                code = f"""# {prompt} - trying multiple strategies
element_found = False
wait = WebDriverWait(driver, 5)

{chr(10).join(strategies)}"""
                return code
            else:
                return f"""# {prompt}
driver.find_element({python_by_method}, "{locator_value}").click()"""
    
    def clean_output(self, text: str) -> str:
        """Clean and format the generated output."""
        # Remove excessive special characters
        text = re.sub(r'[|:><]+\s*[|:><]+', ' ', text)
        
        # Remove standalone symbols
        text = re.sub(r'\s+[|:><]\s+', ' ', text)
        
        # Clean up entry patterns
        text = re.sub(r'entry[:|]\s*entry', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove trailing symbols
        text = re.sub(r'[|:><]+$', '', text)
        
        return text.strip()
    
    def extract_code_snippet(self, text: str) -> str:
        """Extract valid code patterns from generated text."""
        # Look for Java/Selenium patterns
        patterns = [
            r'driver\.\w+\([^)]*\)',
            r'By\.\w+\([^)]*\)',
            r'WebElement\s+\w+',
            r'findElement\([^)]*\)',
            r'sendKeys\([^)]*\)',
            r'click\(\)',
            r'@\w+',
        ]
        
        snippets = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            snippets.extend(matches)
        
        return ' '.join(snippets) if snippets else text
    
    def generate_clean(self, prompt: str, max_tokens: int = 30, temperature: float = 0.3):
        """Generate with cleaning and formatting using template-based approach."""
        
        # Check if prompt contains multiple actions separated by "and"
        if ' and ' in prompt.lower():
            # Split the compound prompt into individual actions
            actions = self._split_compound_prompt(prompt)
            if len(actions) > 1:
                # Generate code for each action and combine
                combined_code = []
                for i, action in enumerate(actions, 1):
                    code = self.generate_clean(action.strip(), max_tokens, temperature)
                    # Add step comment (Python style since we generate Python code now)
                    combined_code.append(f"# Step {i}: {action.strip()}")
                    combined_code.append(code)
                    combined_code.append("")  # Empty line between steps
                return "\n".join(combined_code).strip()
        
        # Parse the prompt for common patterns
        prompt_lower = prompt.lower()
        
        # FIRST: Try to find exact match in dataset
        dataset_match = self._find_dataset_match(prompt)
        print(f"[DATASET] Prompt: '{prompt}'")
        print(f"[DATASET] Match found: {dataset_match is not None}")
        if dataset_match:
            print(f"[DATASET] Locator: {dataset_match.get('locator')}")
            print(f"[DATASET] Action: {dataset_match.get('action')}")
        
        if dataset_match and dataset_match.get('locator'):
            locator = dataset_match['locator']
            action_type = dataset_match.get('action', 'click')
            element_type = dataset_match.get('element_type', 'element')
            fallback_locators = dataset_match.get('fallback_locators', [])
            
            # Convert Java locator to Python and generate code with fallback support
            return self._generate_from_locator(prompt, locator, action_type, element_type, fallback_locators)
        
        # Template-based generation for common actions
        if 'click' in prompt_lower:
            element_id = self._extract_element_name(prompt)
            # Determine element type for better variable naming
            if 'button' in prompt_lower or 'btn' in prompt_lower:
                element_var = 'button'
                element_comment = 'button'
            elif 'link' in prompt_lower:
                element_var = 'link'
                element_comment = 'link'
            elif 'tab' in prompt_lower:
                element_var = 'tab'
                element_comment = 'tab'
            else:
                element_var = 'element'
                element_comment = 'element'
            
            # Check locator type and generate appropriate code
            if element_id.startswith('xpath:'):
                # Remove 'xpath:' prefix, keeping the XPath expression as-is
                xpath = element_id[6:]  # Remove 'xpath:' prefix
                # Escape quotes in xpath for Java string
                xpath_escaped = xpath.replace('"', '\\"')
                return f"""// Click {element_comment}
driver.findElement(By.xpath("{xpath_escaped}")).click();"""
            elif element_id.startswith('css:'):
                # CSS Selector
                css = element_id[4:]  # Remove 'css:' prefix
                return f"""// Click {element_comment}
driver.findElement(By.cssSelector("{css}")).click();"""
            elif element_id.startswith('name:'):
                # Name attribute
                name = element_id[5:]  # Remove 'name:' prefix
                return f"""// Click {element_comment}
driver.findElement(By.name("{name}")).click();"""
            else:
                # Default to By.id
                return f"""// Click {element_comment}
driver.findElement(By.id("{element_id}")).click();"""
        
        elif 'enter' in prompt_lower or 'type' in prompt_lower or 'input' in prompt_lower:
            # Extract the value to enter
            value = self._extract_input_value(prompt)
            
            # Determine field type and element locator
            element_id = self._extract_element_name(prompt)
            by_locator, locator_value = self._extract_locator(prompt)
            
            # Determine field name for comment
            if 'email' in prompt_lower:
                field_name = 'email'
                if not element_id or element_id == 'elementId':
                    element_id = 'email'
            elif 'password' in prompt_lower:
                field_name = 'password'
                if not element_id or element_id == 'elementId':
                    element_id = 'password'
            elif 'username' in prompt_lower or 'user' in prompt_lower:
                field_name = 'username'
                if not element_id or element_id == 'elementId':
                    element_id = 'username'
            elif 'first name' in prompt_lower or 'firstname' in prompt_lower:
                field_name = 'first name'
                if not element_id or element_id == 'elementId':
                    element_id = 'firstName'
            elif 'last name' in prompt_lower or 'lastname' in prompt_lower:
                field_name = 'last name'
                if not element_id or element_id == 'elementId':
                    element_id = 'lastName'
            else:
                field_name = 'input'
            
            # Use extracted locator if available - GENERATE PYTHON CODE
            if by_locator and locator_value:
                # Convert Java By method to Python constant
                python_by = self._java_to_python_by(by_locator)
                return f"""# Enter text in {field_name} field
driver.find_element({python_by}, "{locator_value}").clear()
driver.find_element({python_by}, "{locator_value}").send_keys("{value}")"""
            else:
                return f"""# Enter text in {field_name} field
driver.find_element(By.ID, "{element_id}").clear()
driver.find_element(By.ID, "{element_id}").send_keys("{value}")"""
        
        elif 'select' in prompt_lower and 'dropdown' in prompt_lower:
            element_id = self._extract_element_name(prompt)
            return f"""// Select from dropdown
WebElement dropdown = driver.findElement(By.id("{element_id}"));
Select select = new Select(dropdown);
select.selectByVisibleText("Option");"""
        
        elif 'verify' in prompt_lower or 'check' in prompt_lower or 'assert' in prompt_lower:
            if 'title' in prompt_lower:
                return """// Verify page title
String actualTitle = driver.getTitle();
Assert.assertEquals("Expected Title", actualTitle);"""
            elif 'success' in prompt_lower or 'message' in prompt_lower:
                return """// Verify success message
WebElement successMessage = driver.findElement(By.id("successMsg"));
Assert.assertTrue(successMessage.isDisplayed());
String messageText = successMessage.getText();
Assert.assertTrue(messageText.contains("Success"));"""
            elif 'text' in prompt_lower:
                element_id = self._extract_element_name(prompt)
                return f"""// Verify element text
WebElement element = driver.findElement(By.id("{element_id}"));
String actualText = element.getText();
Assert.assertEquals("Expected Text", actualText);"""
            else:
                return """// Verify element
WebElement element = driver.findElement(By.id("elementId"));
Assert.assertTrue(element.isDisplayed());"""
        
        elif 'navigate' in prompt_lower or 'open' in prompt_lower or 'go to' in prompt_lower:
            return """// Navigate to URL
driver.get("https://example.com");"""
        
        elif 'wait' in prompt_lower:
            return """// Wait for element
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("elementId")));"""
        
        # Fallback to AI generation
        tokens = self.tokenizer.encode(prompt)
        generated_tokens = self.model.generate(
            tokens,
            max_length=max_tokens,
            temperature=temperature
        )
        generated_text = self.tokenizer.decode(generated_tokens)
        cleaned = self.clean_output(generated_text)
        code_snippet = self.extract_code_snippet(cleaned)
        
        # If AI generation is poor, return a generic template
        if not code_snippet or len(code_snippet) < 10:
            return f"""// {prompt}
driver.findElement(By.id("elementId")).click();"""
        
        return code_snippet
    
    def _extract_element_name(self, prompt: str) -> str:
        """Extract element name from prompt using dataset first, then fallback to rules."""
        prompt_lower = prompt.lower()
        
        # Try to find in dataset first
        dataset_match = self._find_dataset_match(prompt)
        if dataset_match:
            locator = dataset_match.get('locator', '')
            
            # Extract element ID or XPath from locator string
            if locator:
                # Extract from By.id("element-id")
                id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', locator)
                if id_match:
                    return id_match.group(1)
                
                # Extract from By.xpath("xpath")
                xpath_match = re.search(r'By\.xpath\s*\(\s*"([^"]+)"\s*\)', locator)
                if xpath_match:
                    return f"xpath:{xpath_match.group(1)}"
                
                # Extract from By.cssSelector("css")
                css_match = re.search(r'By\.cssSelector\s*\(\s*"([^"]+)"\s*\)', locator)
                if css_match:
                    return f"css:{css_match.group(1)}"
                
                # Extract from By.name("name")
                name_match = re.search(r'By\.name\s*\(\s*"([^"]+)"\s*\)', locator)
                if name_match:
                    return f"name:{name_match.group(1)}"
        
        # Fallback to hardcoded rules for producer-specific elements
        if 'producer-email' in prompt_lower or 'producer email' in prompt_lower:
            return 'producer-email'
        elif 'producer-password' in prompt_lower or 'producer password' in prompt_lower:
            return 'producer-password'
        elif 'producer-login' in prompt_lower or 'producer login' in prompt_lower:
            # Button uses class="button primary-btn" and type="submit"
            # Return xpath for better stability with dynamic elements
            return 'xpath://button[@type="submit" and contains(@class, "primary-btn")]'
        
        # Common element names
        if 'login' in prompt_lower:
            return 'loginBtn' if 'button' in prompt_lower else 'username'
        elif 'submit' in prompt_lower:
            return 'submitBtn'
        elif 'success' in prompt_lower or 'message' in prompt_lower:
            return 'successMsg'
        elif 'error' in prompt_lower:
            return 'errorMsg'
        elif 'username' in prompt_lower:
            return 'username'
        elif 'password' in prompt_lower:
            return 'password'
        elif 'email' in prompt_lower:
            return 'email'
        elif 'search' in prompt_lower:
            return 'searchBox'
        elif 'country' in prompt_lower or 'dropdown' in prompt_lower:
            return 'countrySelect'
        else:
            return 'elementId'
    
    def _split_compound_prompt(self, prompt: str) -> list:
        """Split a compound prompt into individual actions."""
        import re
        
        # Split by " and " but be careful with "and" within field names or values
        # Use regex to split on " and " that's followed by action verbs
        action_verbs = ['enter', 'type', 'click', 'select', 'verify', 'wait', 'navigate', 'open', 'check']
        
        # Create pattern: " and " followed by action verb
        pattern = r'\s+and\s+(?=' + '|'.join(action_verbs) + r')'
        
        # Split the prompt
        actions = re.split(pattern, prompt, flags=re.IGNORECASE)
        
        # Clean up each action
        actions = [action.strip() for action in actions if action.strip()]
        
        return actions
    
    def _extract_input_value(self, prompt: str) -> str:
        """Extract the actual value to be entered from the prompt."""
        import re
        
        # Pattern: "enter VALUE in field"
        # Try to match: enter [something] in [field]
        patterns = [
            r'enter\s+([^\s]+(?:\s+[^\s]+)*?)\s+in\s+',  # enter VALUE in
            r'type\s+([^\s]+(?:\s+[^\s]+)*?)\s+in(?:to)?\s+',  # type VALUE in/into
            r'input\s+([^\s]+(?:\s+[^\s]+)*?)\s+in(?:to)?\s+',  # input VALUE in/into
            r'enter\s+"([^"]+)"\s+in\s+',  # enter "VALUE" in (quoted)
            r'enter\s+\'([^\']+)\'\s+in\s+',  # enter 'VALUE' in (single quoted)
        ]
        
        prompt_lower = prompt.lower()
        original_prompt = prompt  # Keep original for case-sensitive extraction
        
        for pattern in patterns:
            match = re.search(pattern, original_prompt, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Remove common words that are not part of the value
                stop_words = ['the', 'a', 'an', 'field', 'input', 'box', 'text']
                words = value.split()
                filtered_words = [w for w in words if w.lower() not in stop_words]
                if filtered_words:
                    return ' '.join(filtered_words)
                return value
        
        # If no pattern matched, try to find email or other recognizable values
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', prompt)
        if email_match:
            return email_match.group(0)
        
        # Look for quoted strings
        quoted_match = re.search(r'"([^"]+)"', prompt)
        if quoted_match:
            return quoted_match.group(1)
        
        quoted_match = re.search(r"'([^']+)'", prompt)
        if quoted_match:
            return quoted_match.group(1)
        
        # Fallback: return placeholder
        return "your_text_here"
    
    def _extract_locator(self, prompt: str) -> tuple:
        """Extract By locator type and value from prompt."""
        import re
        
        prompt_lower = prompt.lower()
        
        # Pattern: "with id VALUE", "with name VALUE", etc.
        id_match = re.search(r'with\s+id\s+([^\s,]+)', prompt_lower)
        if id_match:
            return ('id', id_match.group(1))
        
        name_match = re.search(r'with\s+name\s+([^\s,]+)', prompt_lower)
        if name_match:
            return ('name', name_match.group(1))
        
        class_match = re.search(r'with\s+class\s+([^\s,]+)', prompt_lower)
        if class_match:
            return ('className', class_match.group(1))
        
        xpath_match = re.search(r'with\s+xpath\s+(.+?)(?:\s+and|\s+then|$)', prompt_lower)
        if xpath_match:
            return ('xpath', xpath_match.group(1).strip())
        
        css_match = re.search(r'with\s+css\s+(.+?)(?:\s+and|\s+then|$)', prompt_lower)
        if css_match:
            return ('cssSelector', css_match.group(1).strip())
        
        type_match = re.search(r'with\s+type\s+([^\s,]+)', prompt_lower)
        if type_match:
            return ('cssSelector', f'[type="{type_match.group(1)}"]')
        
        # No specific locator found
        return (None, None)
    
    def suggest_locator_from_html(self, html: str) -> dict:
        """Suggest locator based on HTML element."""
        
        # Clean up HTML input - remove extra whitespace and newlines
        html = html.strip()
        
        # Extract tag name - handle various input formats
        tag_match = re.search(r'<(\w+)', html, re.IGNORECASE)
        if not tag_match:
            # If no tag found, try to find it without < (user might have entered just tag name)
            tag_match = re.search(r'^(\w+)', html)
        tag_name = tag_match.group(1) if tag_match else 'div'
        
        # Extract attributes
        id_match = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        name_match = re.search(r'\bname\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        class_match = re.search(r'\bclass\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        type_match = re.search(r'\btype\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        # Extract text content
        text_match = re.search(r'>([^<]+)<', html)
        text_content = text_match.group(1).strip() if text_match else ''
        
        locators = []
        # Check if ANY attribute exists
        has_attributes = bool(id_match or name_match or class_match or type_match or text_content)
        
        # Priority 1: ID attribute
        if id_match:
            id_value = id_match.group(1)
            locators.append(f"By.id(\"{id_value}\")")
            locators.append(f"By.cssSelector(\"#{id_value}\")")
        
        # Priority 2: Name attribute
        if name_match:
            name_value = name_match.group(1)
            locators.append(f"By.name(\"{name_value}\")")
            locators.append(f"By.cssSelector(\"{tag_name}[name='{name_value}']\")")
        
        # Priority 3: Class attribute
        if class_match:
            classes = class_match.group(1).split()
            if classes:
                locators.append(f"By.className(\"{classes[0]}\")")
                css_classes = '.'.join(classes)
                locators.append(f"By.cssSelector(\"{tag_name}.{css_classes}\")")
        
        # Priority 4: Type attribute (for input elements)
        if type_match:
            type_value = type_match.group(1)
            locators.append(f"By.cssSelector(\"{tag_name}[type='{type_value}']\")")
        
        # Priority 5: Text content (for links, buttons)
        if text_content and tag_name.lower() in ['a', 'button', 'span', 'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            locators.append(f"By.xpath(\"//{tag_name}[text()='{text_content}']\")")
            if len(text_content) > 20:
                locators.append(f"By.xpath(\"//{tag_name}[contains(text(), '{text_content[:20]}')]\")")
            if tag_name.lower() in ['a', 'button']:
                locators.append(f"By.linkText(\"{text_content}\")")
                locators.append(f"By.partialLinkText(\"{text_content[:20]}\")")
        
        # If NO attributes found, generate XPath AND CSS selectors
        if not has_attributes:
            # Generate basic XPath based on tag name
            locators.append(f"By.xpath(\"//{tag_name}\")")
            
            # Generate CSS selector based on tag name
            locators.append(f"By.cssSelector(\"{tag_name}\")")
            
            # If there's text content, create XPath with text
            if text_content:
                locators.append(f"By.xpath(\"//{tag_name}[text()='{text_content}']\")")
                locators.append(f"By.xpath(\"//{tag_name}[contains(text(), '{text_content[:20]}')]\")")
            
            # Generate positional XPath
            locators.append(f"By.xpath(\"//{tag_name}[1]\")")
            locators.append(f"By.xpath(\"(//{tag_name})[1]\")")
            
            # Generate nth-child CSS selectors
            locators.append(f"By.cssSelector(\"{tag_name}:first-of-type\")")
            locators.append(f"By.cssSelector(\"{tag_name}:nth-of-type(1)\")")
            locators.append(f"By.cssSelector(\"{tag_name}:last-of-type\")")
        
        # Generate AI suggestion
        prompt = f"HTML element with attributes from: {html[:100]}"
        ai_suggestion = self.generate_clean(prompt, max_tokens=20, temperature=0.2)
        
        return {
            'recommended_locators': locators,
            'ai_suggestion': ai_suggestion,
            'element_analysis': {
                'has_id': id_match is not None,
                'has_name': name_match is not None,
                'has_class': class_match is not None,
                'has_type': type_match is not None,
                'has_text': bool(text_content),
                'has_attributes': has_attributes,
                'tag_name': tag_name,
                'strategy': 'XPath & CSS (No Attributes)' if not has_attributes else 'CSS/ID/Name/Class'
            }
        }
    
    def suggest_action(self, element_type: str, context: str = "", language: str = "java") -> dict:
        """
        Enhanced action suggestion using ActionSuggestionEngine.
        Provides comprehensive, context-aware suggestions with confidence scoring.
        
        Args:
            element_type: Type of HTML element (button, input, etc.)
            context: Context information (element text, id, purpose, etc.)
            language: Target language for code generation (java, python, javascript)
        
        Returns:
            dict: Enhanced suggestions with confidence, test scenarios, and code samples
        """
        # Use enhanced action suggestion engine
        result = self.action_engine.suggest_action(element_type, context, language)
        
        # Add backward compatibility fields for existing API consumers
        result['ai_generated_code'] = result['code_samples'].get(language, result['code_samples'].get('java', ''))
        
        return result
    
    def suggest_action_legacy(self, element_type: str, context: str = "") -> dict:
        """
        Legacy action suggestion method (kept for backward compatibility).
        Use suggest_action() for enhanced features.
        """
        
        # Rule-based suggestions
        action_map = {
            'button': ['click()', 'submit()'],
            'input': ['sendKeys(text)', 'clear()', 'getAttribute("value")'],
            'select': ['Select(element)', 'selectByVisibleText(text)'],
            'link': ['click()', 'getAttribute("href")'],
            'checkbox': ['click()', 'isSelected()'],
            'radio': ['click()', 'isSelected()'],
            'textarea': ['sendKeys(text)', 'clear()']
        }
        
        recommended = action_map.get(element_type.lower(), ['click()'])
        
        # Generate element-type-specific code
        element_lower = element_type.lower()
        
        if element_lower == 'button':
            ai_code = """// Click button
WebElement button = driver.findElement(By.id("buttonId"));
button.click();"""
        
        elif element_lower == 'input':
            ai_code = """// Enter text in input field
WebElement inputField = driver.findElement(By.id("elementId"));
inputField.clear();
inputField.sendKeys("your_text_here");"""
        
        elif element_lower == 'select':
            ai_code = """// Select from dropdown
WebElement dropdown = driver.findElement(By.id("elementId"));
Select select = new Select(dropdown);
select.selectByVisibleText("Option");"""
        
        elif element_lower == 'link':
            ai_code = """// Click link
WebElement link = driver.findElement(By.linkText("Link Text"));
link.click();"""
        
        elif element_lower == 'checkbox':
            ai_code = """// Click checkbox
WebElement checkbox = driver.findElement(By.id("checkboxId"));
if (!checkbox.isSelected()) {
    checkbox.click();
}"""
        
        elif element_lower == 'radio':
            ai_code = """// Select radio button
WebElement radioButton = driver.findElement(By.id("radioId"));
radioButton.click();"""
        
        elif element_lower == 'textarea':
            ai_code = """// Enter text in textarea
WebElement textArea = driver.findElement(By.id("textAreaId"));
textArea.clear();
textArea.sendKeys("your_text_here");"""
        
        elif element_lower == 'verify_message':
            ai_code = """// Verify message/toast/alert
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement message = wait.until(ExpectedConditions.presenceOfElementLocated(
    By.xpath("//*[contains(@class, 'alert') and contains(text(), 'expected_message')]")
));
String messageText = message.getText();
Assert.assertTrue(messageText.contains("expected_message"), "Message verification failed");"""
        
        else:
            # Default to click action
            ai_code = f"""// Click {element_type}
WebElement element = driver.findElement(By.id("elementId"));
element.click();"""
        
        return {
            'element_type': element_type,
            'recommended_actions': recommended,
            'ai_generated_code': ai_code,
            'context': context
        }
    
    def suggest_locator(self, element_type: str, action: str, attributes: dict) -> list:
        """
        Suggest optimal locators for an element based on its attributes.
        Used by the recorder to generate intelligent locator suggestions.
        
        Args:
            element_type: HTML tag name (e.g., 'button', 'input')
            action: Action being performed (e.g., 'click', 'input')
            attributes: Dictionary of element attributes (id, name, className, etc.)
        
        Returns:
            List of suggested locators in priority order
        """
        locators = []
        
        # For input/select/textarea, prioritize name and ID (stable for forms)
        if element_type.lower() in ['input', 'select', 'textarea']:
            # Priority 1: Name (best for forms)
            if attributes.get('name'):
                locators.append(f'By.name("{attributes["name"]}")')
            
            # Priority 2: ID (secondary for inputs)
            if attributes.get('id'):
                locators.append(f'By.id("{attributes["id"]}")')
        
        # For links, prioritize linkText
        elif element_type.lower() == 'a':
            link_text = attributes.get('innerText') or attributes.get('text', '')
            link_text = link_text.strip()
            if link_text:
                locators.append(f'By.linkText("{link_text}")')
                if len(link_text) > 20:
                    locators.append(f'By.partialLinkText("{link_text[:20]}")')
        
        # For buttons and clickable elements, prioritize text-based locators
        elif element_type.lower() == 'button' or action == 'click':
            text = attributes.get('innerText') or attributes.get('text', '')
            text = text.strip() if text else ''
            if text:
                # Use normalize-space(.) to handle whitespace and nested text elements (e.g., <button><span>Text</span></button>)
                locators.append(f'By.xpath("//{element_type.lower()}[contains(normalize-space(.), \\"{text}\\")]")')
                if attributes.get('type'):
                    locators.append(f'By.xpath("//{element_type.lower()}[@type=\\"{attributes["type"]}\\" and contains(normalize-space(.), \\"{text}\\")]")')
        
        # CSS Selector with classes (good alternative)
        if attributes.get('className'):
            classes = attributes['className'].split()
            if classes:
                # Use class-based selector
                non_generic = [cls for cls in classes if cls not in ['btn', 'form-control', 'input', 'button']]
                if non_generic:
                    locators.append(f'By.cssSelector("{element_type.lower()}.{non_generic[0]}")')
                else:
                    locators.append(f'By.cssSelector("{element_type.lower()}.{classes[0]}")')
        
        # ID as fallback for non-input elements (only if no text-based locators)
        if element_type.lower() not in ['input', 'select', 'textarea'] and not any('text()' in loc for loc in locators):
            if attributes.get('id'):
                locators.append(f'By.id("{attributes["id"]}")')
        
        # Priority 4: CSS Selector (combination)
        if attributes.get('id'):
            locators.append(f'By.cssSelector("#{attributes["id"]}")')
        elif attributes.get('className'):
            classes = attributes['className'].split()
            if classes:
                locators.append(f'By.cssSelector(".{classes[0]}")')
        
        # Priority 5: Text-based XPath (relative, not absolute)
        if attributes.get('text') or attributes.get('innerText'):
            text = attributes.get('innerText') or attributes.get('text')
            text = text.strip()
            if text:
                # Use normalize-space(.) to handle whitespace and nested text
                locators.append(f'By.xpath("//{element_type}[contains(normalize-space(.), \\"{text}\\")]")')
        
        # Priority 6: Attribute-based XPath (relative)
        if attributes.get('id'):
            locators.append(f'By.xpath("//*[@id=\\"{attributes["id"]}\\"]")')
        elif attributes.get('name'):
            locators.append(f'By.xpath("//*[@name=\\"{attributes["name"]}\\"]")')
        
        # If no locators found, create a generic tag-based one
        if not locators:
            locators.append(f'By.tagName("{element_type.lower()}")')
        
        # NEVER use absolute XPath from attributes.get('xpath') - it's too fragile
        
        return locators
    
    def generate_test_method(self, description: str) -> str:
        """Generate a complete test method structure."""
        
        method_name = description.lower().replace(' ', '_')
        
        template = f"""@Test
public void test_{method_name}() {{
    // {description}
    WebDriver driver = new ChromeDriver();
    
    // Generated steps:
    {self.generate_clean(description, max_tokens=40, temperature=0.4)}
    
    driver.quit();
}}"""
        
        return template

def main():
    """Demo the improved generator."""
    
    print("\n" + "="*70)
    print("🎯 IMPROVED SELENIUM CODE GENERATOR")
    print("="*70 + "\n")
    
    generator = ImprovedSeleniumGenerator()
    
    # Test 1: Clean generation
    print("\n" + "-"*70)
    print("Test 1: Generate Click Action")
    print("-"*70)
    result = generator.generate_clean("click login button", max_tokens=20, temperature=0.3)
    print(f"Generated: {result}\n")
    
    # Test 2: Locator suggestion
    print("-"*70)
    print("Test 2: Suggest Locator from HTML")
    print("-"*70)
    html = '<button id="submit-btn" class="btn btn-primary">Submit</button>'
    locator_result = generator.suggest_locator_from_html(html)
    print(f"Recommended Locators: {locator_result['recommended_locators']}")
    print(f"AI Suggestion: {locator_result['ai_suggestion']}\n")
    
    # Test 3: Action suggestion
    print("-"*70)
    print("Test 3: Suggest Action for Element")
    print("-"*70)
    action_result = generator.suggest_action("input", "login form")
    print(f"Element Type: {action_result['element_type']}")
    print(f"Recommended: {action_result['recommended_actions']}")
    print(f"AI Code: {action_result['ai_generated_code']}\n")
    
    # Test 4: Test method generation
    print("-"*70)
    print("Test 4: Generate Test Method")
    print("-"*70)
    test_method = generator.generate_test_method("verify login functionality")
    print(test_method)
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
