"""
Smart Locator Strategy Generator
Generates robust, multi-fallback locator strategies
Scores locators based on reliability and best practices
"""

from typing import Dict, List, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)

class SmartLocatorGenerator:
    """Generates intelligent, robust locator strategies with scoring."""
    
    def __init__(self, inference_model=None):
        """
        Initialize smart locator generator.
        
        Args:
            inference_model: Trained AI model for pattern matching
        """
        self.inference_model = inference_model
        
        # Locator reliability scores (higher is better)
        self.locator_scores = {
            'id': 100,
            'name': 85,
            'data-testid': 95,
            'aria-label': 80,
            'css_class_unique': 70,
            'css_attribute': 65,
            'xpath_id': 90,
            'xpath_attribute': 60,
            'xpath_text': 55,
            'xpath_position': 30
        }
    
    def generate_locator_strategy(self, element: Dict, context: Dict = None) -> List[Dict]:
        """
        Generate multi-fallback locator strategy for element.
        
        Args:
            element: Element information (type, text, position, attributes)
            context: Additional context (page type, nearby elements)
            
        Returns:
            List of locator strategies ordered by reliability
        """
        strategies = []
        
        # 1. Try ID locator (highest priority)
        if element.get('suggested_id'):
            strategies.append({
                'type': 'id',
                'value': element['suggested_id'],
                'code_java': f'By.id("{element["suggested_id"]}")',
                'code_python': f'By.ID, "{element["suggested_id"]}"',
                'score': self.locator_scores['id'],
                'description': f'Find by ID: {element["suggested_id"]}'
            })
        
        # 2. Try Name attribute
        if element.get('suggested_name'):
            strategies.append({
                'type': 'name',
                'value': element['suggested_name'],
                'code_java': f'By.name("{element["suggested_name"]}")',
                'code_python': f'By.NAME, "{element["suggested_name"]}"',
                'score': self.locator_scores['name'],
                'description': f'Find by Name: {element["suggested_name"]}'
            })
        
        # 3. Try data-testid or test attributes
        if element.get('text'):
            test_id = self._text_to_test_id(element['text'])
            strategies.append({
                'type': 'data-testid',
                'value': test_id,
                'code_java': f'By.cssSelector("[data-testid=\\"{test_id}\\"]")',
                'code_python': f'By.CSS_SELECTOR, "[data-testid=\\"{test_id}\\"]"',
                'score': self.locator_scores['data-testid'],
                'description': f'Find by test ID: {test_id}',
                'recommendation': 'Add data-testid attribute to element for better stability'
            })
        
        # 4. Try ARIA labels (good for accessibility)
        if element.get('text'):
            strategies.append({
                'type': 'aria-label',
                'value': element['text'],
                'code_java': f'By.cssSelector("[aria-label=\\"{element["text"]}\\"]")',
                'code_python': f'By.CSS_SELECTOR, "[aria-label=\\"{element["text"]}\\"]"',
                'score': self.locator_scores['aria-label'],
                'description': f'Find by ARIA label: {element["text"]}'
            })
        
        # 5. CSS selector based on type and attributes
        css_selector = self._generate_css_selector(element)
        if css_selector:
            strategies.append({
                'type': 'css',
                'value': css_selector,
                'code_java': f'By.cssSelector("{css_selector}")',
                'code_python': f'By.CSS_SELECTOR, "{css_selector}"',
                'score': self.locator_scores['css_attribute'],
                'description': f'Find by CSS: {css_selector}'
            })
        
        # 6. XPath by ID (if available)
        if element.get('suggested_id'):
            xpath_id = f'//*[@id="{element.get("suggested_id")}"]'
            strategies.append({
                'type': 'xpath',
                'value': xpath_id,
                'code_java': f'By.xpath("{xpath_id}")',
                'code_python': f'By.XPATH, "{xpath_id}"',
                'score': 95,
                'description': f'XPath by ID: {element["suggested_id"]}'
            })
        
        # 7. XPath by attributes
        xpath_attrs = self._generate_xpath_by_attributes(element)
        if xpath_attrs:
            strategies.append({
                'type': 'xpath',
                'value': xpath_attrs,
                'code_java': f'By.xpath("{xpath_attrs}")',
                'code_python': f'By.XPATH, "{xpath_attrs}"',
                'score': 70,
                'description': 'XPath by attributes'
            })
        
        # 8. XPath with text (if text available)
        if element.get('text'):
            xpath_text = self._generate_xpath_by_text(element)
            strategies.append({
                'type': 'xpath',
                'value': xpath_text,
                'code_java': f'By.xpath("{xpath_text}")',
                'code_python': f'By.XPATH, "{xpath_text}"',
                'score': self.locator_scores['xpath_text'],
                'description': f'XPath by text: {element["text"]}'
            })
            
            # 9. XPath with contains (more flexible)
            xpath_contains = self._generate_xpath_contains(element)
            strategies.append({
                'type': 'xpath',
                'value': xpath_contains,
                'code_java': f'By.xpath("{xpath_contains}")',
                'code_python': f'By.XPATH, "{xpath_contains}"',
                'score': 60,
                'description': f'XPath contains text: {element["text"]}'
            })
        
        # 10. XPath with position (last resort)
        xpath_position = self._generate_xpath_by_position(element)
        if xpath_position:
            strategies.append({
                'type': 'xpath',
                'value': xpath_position,
                'code_java': f'By.xpath("{xpath_position}")',
                'code_python': f'By.XPATH, "{xpath_position}"',
                'score': self.locator_scores['xpath_position'],
                'description': 'XPath by position (least reliable)',
                'warning': '⚠️ Position-based XPath is fragile and may break with UI changes'
            })
        
        # Use AI model to enhance/reorder strategies
        if self.inference_model and context:
            strategies = self._enhance_with_ai(strategies, element, context)
        
        # Sort by score (highest first)
        strategies.sort(key=lambda x: x['score'], reverse=True)
        
        return strategies
    
    def _text_to_test_id(self, text: str) -> str:
        """Convert text to test ID format."""
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        clean = clean.lower().strip()
        clean = re.sub(r'\s+', '-', clean)
        return f'test-{clean}' if clean else 'test-element'
    
    def _generate_css_selector(self, element: Dict) -> str:
        """Generate CSS selector for element."""
        elem_type = element.get('type', 'unknown')
        
        # Map element types to HTML tags
        tag_map = {
            'button': 'button',
            'input': 'input',
            'text_field': 'input',
            'textarea': 'textarea',
            'link': 'a',
            'checkbox': 'input[type="checkbox"]',
            'radio': 'input[type="radio"]',
            'select': 'select'
        }
        
        tag = tag_map.get(elem_type, 'div')
        
        selectors = [tag]
        
        # Add class if available
        if element.get('class'):
            classes = element['class'].split()
            if classes:
                selectors.append(f".{classes[0]}")
        
        # Add type attribute for inputs
        if elem_type in ['input', 'text_field'] and element.get('input_type'):
            return f'{tag}[type="{element["input_type"]}"]'
        
        return ''.join(selectors)
    
    def _generate_xpath_by_attributes(self, element: Dict) -> Optional[str]:
        """Generate XPath using element attributes."""
        elem_type = element.get('type', 'unknown')
        
        tag_map = {
            'button': 'button',
            'input': 'input',
            'text_field': 'input',
            'textarea': 'textarea',
            'link': 'a',
            'label': 'label'
        }
        
        tag = tag_map.get(elem_type, '*')
        conditions = []
        
        # Add attribute conditions
        if element.get('suggested_name'):
            conditions.append(f'@name="{element["suggested_name"]}"')
        
        if element.get('text') and elem_type == 'button':
            conditions.append(f'@value="{element["text"]}"')
        
        if elem_type == 'input':
            conditions.append('@type="text" or @type="password" or @type="email"')
        
        if conditions:
            return f'//{tag}[{" and ".join(conditions)}]'
        return None
    
    def _generate_xpath_contains(self, element: Dict) -> str:
        """Generate flexible XPath using contains()."""
        elem_type = element.get('type', 'unknown')
        text = element.get('text', '')
        
        tag_map = {
            'button': 'button',
            'link': 'a',
            'input': 'input',
            'label': 'label'
        }
        
        tag = tag_map.get(elem_type, '*')
        
        if elem_type in ['button', 'link', 'label']:
            return f'//{tag}[contains(., "{text}")]'
        elif elem_type == 'input' and element.get('label'):
            # XPath for input with associated label
            return f'//input[contains(@placeholder, "{element["label"]}") or preceding-sibling::label[contains(., "{element["label"]}")]]'
        else:
            return f'//{tag}[contains(@value, "{text}") or contains(@placeholder, "{text}")]'
    
    def _generate_xpath_by_text(self, element: Dict) -> str:
        """Generate XPath using visible text."""
        elem_type = element.get('type', 'unknown')
        text = element['text']
        
        tag_map = {
            'button': 'button',
            'link': 'a',
            'input': 'input',
            'label': 'label'
        }
        
        tag = tag_map.get(elem_type, '*')
        
        # Use contains for partial match (more robust)
        if elem_type == 'button':
            return f'//{tag}[contains(text(), "{text}")]'
        elif elem_type == 'input':
            return f'//{tag}[@placeholder="{text}" or @value="{text}"]'
        else:
            return f'//{tag}[contains(., "{text}")]'
    
    def _generate_xpath_by_position(self, element: Dict) -> Optional[str]:
        """Generate XPath using position (least reliable)."""
        elem_type = element.get('type', 'unknown')
        position = element.get('index', 1)
        
        tag_map = {
            'button': 'button',
            'input': 'input',
            'link': 'a'
        }
        
        tag = tag_map.get(elem_type, 'div')
        return f'(//{tag})[{position}]'
    
    def _enhance_with_ai(self, strategies: List[Dict], element: Dict, 
                        context: Dict) -> List[Dict]:
        """
        Use trained AI model to enhance locator strategies.
        
        Args:
            strategies: Initial strategies
            element: Element info
            context: Page context
            
        Returns:
            Enhanced strategies with AI suggestions
        """
        try:
            # Build prompt for AI model
            prompt = self._build_ai_prompt(element, context)
            
            # Get AI suggestions
            ai_match = self.inference_model._find_dataset_match(prompt)
            
            if ai_match and ai_match.get('locator'):
                # Boost score of AI-suggested locator type
                suggested_locator = ai_match['locator']
                
                for strategy in strategies:
                    if suggested_locator.lower() in strategy['value'].lower():
                        strategy['score'] += 15
                        strategy['ai_recommended'] = True
                        strategy['confidence'] = ai_match.get('confidence', 0.8)
        
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
        
        return strategies
    
    def _build_ai_prompt(self, element: Dict, context: Dict) -> str:
        """Build prompt for AI model."""
        elem_type = element.get('type', 'element')
        text = element.get('text', '')
        page_type = context.get('page_type', 'unknown')
        
        prompt = f"{elem_type}"
        
        if text:
            prompt += f" {text}"
        
        if page_type != 'unknown':
            prompt += f" on {page_type} page"
        
        return prompt.lower()
    
    def generate_fallback_chain(self, strategies: List[Dict], language: str = 'java') -> str:
        """
        Generate code with fallback chain (try multiple locators).
        
        Args:
            strategies: List of locator strategies
            language: Target language
            
        Returns:
            Code implementing fallback logic
        """
        if language.lower() == 'java':
            return self._java_fallback_chain(strategies)
        else:
            return self._python_fallback_chain(strategies)
    
    def _java_fallback_chain(self, strategies: List[Dict]) -> str:
        """Generate Java fallback chain."""
        # Take top 3 strategies
        top_strategies = strategies[:3]
        
        code = """WebElement element = null;
"""
        
        for i, strategy in enumerate(top_strategies):
            if i == 0:
                code += f"""try {{
    element = driver.findElement({strategy['code_java']});
"""
            else:
                code += f"""}} catch (NoSuchElementException e{i}) {{
    try {{
        element = driver.findElement({strategy['code_java']});
"""
        
        # Close all catch blocks
        code += """    } catch (NoSuchElementException e) {
        throw new NoSuchElementException("Element not found with any locator strategy");
    }
"""
        code += "}" * len(top_strategies)
        
        return code
    
    def _python_fallback_chain(self, strategies: List[Dict]) -> str:
        """Generate Python fallback chain."""
        top_strategies = strategies[:3]
        
        code = "element = None\n"
        code += "locator_strategies = [\n"
        
        for strategy in top_strategies:
            code += f"    ({strategy['code_python']}),\n"
        
        code += """]\n
for locator in locator_strategies:
    try:
        element = driver.find_element(*locator)
        break
    except NoSuchElementException:
        continue

if element is None:
    raise NoSuchElementException("Element not found with any locator strategy")
"""
        
        return code
    
    def score_locator(self, locator_type: str, value: str, element: Dict) -> float:
        """
        Score a locator based on reliability factors.
        
        Args:
            locator_type: Type of locator (id, css, xpath, etc.)
            value: Locator value
            element: Element info
            
        Returns:
            Score from 0-100
        """
        base_score = self.locator_scores.get(locator_type, 50)
        
        # Penalize dynamic-looking IDs
        if locator_type == 'id' and re.search(r'\d{4,}|random|temp|gen', value):
            base_score -= 30
        
        # Penalize long XPaths
        if locator_type == 'xpath' and len(value) > 100:
            base_score -= 20
        
        # Boost if contains semantic text
        if element.get('text') and element['text'].lower() in value.lower():
            base_score += 10
        
        # Penalize position-based selectors
        if ':nth-child' in value or 'nth-of-type' in value:
            base_score -= 15
        
        return max(0, min(100, base_score))
