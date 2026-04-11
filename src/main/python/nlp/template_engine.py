"""
Template Engine - Loads code templates from JSON and generates code dynamically.
This replaces all hardcoded template methods in inference_improved.py.
"""
import json
import os
import re


class TemplateEngine:
    """Generates code from JSON templates instead of hardcoded Python methods."""
    
    def __init__(self, templates_path: str = None):
        """Load code templates from JSON file."""
        if templates_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
            templates_path = os.path.join(project_root, 'resources', 'ml_data', 'templates', 'code-templates.json')
        
        self.templates = {}
        self.prompt_patterns = []
        
        if os.path.exists(templates_path):
            with open(templates_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.prompt_patterns = data.get('prompt_patterns', {}).get('patterns', [])
        
        print(f"[TEMPLATE ENGINE] Loaded {len(self.templates)} action templates")
        print(f"[TEMPLATE ENGINE] Loaded {len(self.prompt_patterns)} prompt patterns")
    
    def match_action(self, prompt: str) -> dict:
        """Match a prompt to an action using keyword patterns.
        
        Phase 2 of Option B - Pattern-based action detection.
        
        Args:
            prompt: Natural language prompt (e.g., "click submit button")
        
        Returns:
            dict: {
                'action': 'click',
                'confidence': 0.95,
                'extraction': {'element': True, 'locator': True, 'value': False}
            }
            or None if no match found
        """
        prompt_lower = prompt.lower().strip()
        
        # Sort patterns by priority (lower number = higher priority)
        sorted_patterns = sorted(self.prompt_patterns, key=lambda p: p.get('priority', 999))
        
        for pattern in sorted_patterns:
            action = pattern.get('action')
            keywords = pattern.get('keywords', [])
            
            # Check if any keyword matches the prompt
            for keyword in keywords:
                if keyword.lower() in prompt_lower:
                    # Calculate confidence based on match quality
                    # Exact phrase match = high confidence
                    # Partial match = medium confidence
                    if prompt_lower == keyword.lower():
                        confidence = 1.0
                    elif prompt_lower.startswith(keyword.lower()):
                        confidence = 0.9
                    else:
                        confidence = 0.7
                    
                    return {
                        'action': action,
                        'confidence': confidence,
                        'extraction': pattern.get('extraction', {}),
                        'matched_keyword': keyword
                    }
        
        # No match found
        return None
    
    def generate_code(self, action: str, mode: str, language: str, **params) -> str:
        """
        Generate code from templates dynamically.
        
        Args:
            action: Action type (click, input, select, verify, navigate, wait, file_upload, search)
            mode: 'simple' or 'comprehensive'
            language: Target language (java, python, javascript, csharp)
            **params: Template parameters (locator, value, element_desc, etc.)
        
        Returns:
            Generated code string
        """
        # Get template
        template = self.templates.get(action, {}).get(mode, {}).get(language)
        
        if not template:
            print(f"[TEMPLATE ENGINE] No template found for {action}/{mode}/{language}")
            return f"// {action} action\n// Template not found"
        
        # Format By method based on language
        if 'by_method' in params:
            params['by_method'] = self._format_by_method(params['by_method'], language)
        
        if 'by_constant' in params:
            params['by_constant'] = self._format_by_constant(params.get('locator_method', 'id'), language)
        
        # Fill template with parameters
        try:
            code = template.format(**params)
            return code
        except KeyError as e:
            print(f"[TEMPLATE ENGINE] Missing parameter {e} for template {action}/{mode}/{language}")
            print(f"[TEMPLATE ENGINE] Available params: {params.keys()}")
            # Return template with missing params visible
            return template
    
    def _format_by_method(self, locator_method: str, language: str) -> str:
        """Format By locator method name for the target language."""
        method_lower = locator_method.lower()
        
        if language == 'python':
            # Python uses constants in find_element calls
            return method_lower
        
        elif language in ['java', 'javascript']:
            # Java and JavaScript use lowercase, except cssSelector
            if method_lower == 'cssselector':
                return 'cssSelector'
            return method_lower
        
        else:  # C#
            # C# capitalizes first letter
            if method_lower == 'cssselector':
                return 'CssSelector'
            elif method_lower == 'xpath':
                return 'XPath'
            else:
                return locator_method[0].upper() + locator_method[1:]
    
    def _format_by_constant(self, locator_method: str, language: str) -> str:
        """Format By constant for Python (By.ID, By.NAME, etc.)."""
        method_lower = locator_method.lower()
        
        if language == 'python':
            py_map = {
                'id': 'By.ID',
                'name': 'By.NAME',
                'cssselector': 'By.CSS_SELECTOR',
                'xpath': 'By.XPATH'
            }
            return py_map.get(method_lower, 'By.ID')
        
        # For other languages, use by_method instead
        return self._format_by_method(locator_method, language)
    
    def get_available_actions(self) -> list:
        """Get list of available actions."""
        return list(self.templates.keys())
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return ['java', 'python', 'javascript', 'csharp']


# Example usage
if __name__ == "__main__":
    engine = TemplateEngine()
    
    # Test click action
    print("="*80)
    print("TEST: Click Button (Comprehensive, Java)")
    print("="*80)
    code = engine.generate_code(
        action='click',
        mode='comprehensive',
        language='java',
        element_desc='submit button',
        by_method='id',
        locator='submitBtn'
    )
    print(code)
    print()
    
    # Test input action
    print("="*80)
    print("TEST: Input Field (Comprehensive, Python)")
    print("="*80)
    code = engine.generate_code(
        action='input',
        mode='comprehensive',
        language='python',
        field_name='email',
        by_constant='By.ID',
        locator='email',
        value='test@example.com',
        locator_method='id'
    )
    print(code)
    print()
    
    # Test JavaScript
    print("="*80)
    print("TEST: Select Dropdown (Simple, JavaScript)")
    print("="*80)
    code = engine.generate_code(
        action='select',
        mode='simple',
        language='javascript',
        by_method='id',
        locator='countrySelect',
        option='United States'
    )
    print(code)
