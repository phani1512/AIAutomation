#!/usr/bin/env python3
"""
Parameter Extraction and Substitution System for Template Entries

Allows users to override placeholders in templates dynamically:
- "get validation message for Email Address" → substitutes "Email Address" for {FIELD}
- "click Overview tab" → substitutes "Overview" for {TAB}
- "upload report.pdf" → substitutes "report.pdf" for {FILENAME}
"""
import re
import json

class TemplateParameterExtractor:
    """Extract parameters from user prompts and substitute into template code"""
    
    # Map template patterns to their placeholders
    TEMPLATE_PATTERNS = {
        # Tab operations
        r'click\s+(?:the\s+)?(.+?)\s+tab': {'placeholder': '{TAB}', 'capture_group': 1},
        r'activate\s+(?:the\s+)?(.+?)\s+tab': {'placeholder': '{TAB}', 'capture_group': 1},
        r'open\s+(?:the\s+)?(.+?)\s+tab': {'placeholder': '{TAB}', 'capture_group': 1},
        r'select\s+(?:the\s+)?(.+?)\s+tab': {'placeholder': '{TAB}', 'capture_group': 1},
        
        # File operations
        r'upload\s+(.+)': {'placeholder': '{FILENAME}', 'capture_group': 1},
        r'attach\s+(.+)': {'placeholder': '{FILENAME}', 'capture_group': 1},
        r'choose\s+file\s+(.+)': {'placeholder': '{FILENAME}', 'capture_group': 1},
        r'select\s+file\s+(.+)': {'placeholder': '{FILENAME}', 'capture_group': 1},
        
        # Search operations
        r'search\s+(?:for|table\s+for)\s+(.+)': {'placeholder': '{SEARCH_TEXT}', 'capture_group': 1},
        
        # Link operations
        r'click\s+(?:the\s+)?(.+?)\s+link': {'placeholder': '{LINK}', 'capture_group': 1},
        r'select\s+(?:the\s+)?(.+?)\s+link': {'placeholder': '{LINK}', 'capture_group': 1},
        
        # Button operations - use {VALUE} to match dataset template
        r'click\s+(?:the\s+)?(.+?)\s+button': {'placeholder': '{VALUE}', 'capture_group': 1},
        r'press\s+(?:the\s+)?(.+?)\s+button': {'placeholder': '{VALUE}', 'capture_group': 1},
        
        # Menu operations
        r'(?:click|select)\s+(?:the\s+)?(.+?)\s+menu': {'placeholder': '{MENU}', 'capture_group': 1},
        r'(?:click|select|choose)\s+(?:the\s+)?(.+?)\s+submenu': {'placeholder': '{SUBMENU}', 'capture_group': 1},
        
        # Validation messages
        r'get\s+validation\s+message\s+for\s+(.+)': {'placeholder': '{FIELD}', 'capture_group': 1},
        r'check\s+error\s+for\s+(.+)': {'placeholder': '{FIELD}', 'capture_group': 1},
        
        # **REMOVED: Password-specific pattern - use generic {VALUE} instead**
        # r'(?:enter|type)\s+password\s+(.+)': {'placeholder': '{PASSWORD}', 'capture_group': 1},
        
        # Dropdown operations (select OPTION from DROPDOWN)
        r'(?:select|choose|pick)\s+(.+?)\s+from\s+(.+?)\s+(?:dropdown|menu|list)': {'placeholder': '{OPTION}', 'capture_group': 1, 'dropdown_group': 2, 'has_dropdown': True},
        
        # NEW: Data input operations with field (enter VALUE in FIELD) - supports multi-word values
        r'(?:enter|type|input|fill)\s+(.+?)\s+in\s+(.+)': {'placeholder': '{VALUE}', 'capture_group': 1, 'field_group': 2, 'has_field': True},
        
        # State operations
        r'select\s+[\'"]([^\'"]+)[\'"]\s+from\s+(?:the\s+)?[\'"]state[\'"]': {'placeholder': '{STATE}', 'capture_group': 1},
    }
    
    # Map placeholder names to their code substitution patterns
    # This allows flexible matching of placeholder variations in dataset code
    PLACEHOLDER_SUBSTITUTIONS = {
        '{TAB}': ['{TAB}', '{tab}', '{TAB_NAME}'],
        '{FILENAME}': ['{FILENAME}', '{filename}', '{FILE_PATH}', '{FILE_NAME}'],
        '{SEARCH_TEXT}': ['{SEARCH_TEXT}', '{CRITERIA}', '{criteria}'],
        '{LINK}': ['{LINK}', '{link}', '{LINK_TEXT}'],
        '{BUTTON}': ['{BUTTON}', '{button}', '{BUTTON_TEXT}'],  # Legacy - button patterns now use {VALUE}
        '{MENU}': ['{MENU}', '{menu}', '{MENU_NAME}'],
        '{SUBMENU}': ['{SUBMENU}', '{submenu}', '{SUBMENU_NAME}'],
        '{FIELD}': ['{FIELD}', '{field}', '{FIELD_NAME}'],
        '{PASSWORD}': ['{PASSWORD}', '{password}', '{PWD}'],
        '{STATE}': ['{STATE}', '{state}', '{STATE_NAME}'],
        '{VALUE}': ['{VALUE}', '{value}', '{TEXT}', '{text}', '{EMAIL}', '{email}', '{DATA}', '{data}'],
        '{OPTION}': ['{OPTION}', '{option}', '{OPTION_TEXT}', '{CHOICE}', '{choice}'],
        '{DROPDOWN}': ['{DROPDOWN}', '{dropdown}', '{DROPDOWN_NAME}', '{SELECT}', '{select}'],
    }
    
    def extract_parameter(self, user_prompt: str, template_prompt: str) -> dict:
        """
        Extract parameter from user prompt based on template pattern
        
        Args:
            user_prompt: User's actual prompt (e.g., "click Overview tab")
            template_prompt: Template prompt pattern (e.g., "click {tab} tab")
        
        Returns:
            dict with 'placeholder' and 'value' keys, or None if no match
        """
        user_prompt_clean = user_prompt.strip()
        
        # Try each pattern (use case-insensitive matching but capture from ORIGINAL prompt)
        for pattern, config in self.TEMPLATE_PATTERNS.items():
            match = re.search(pattern, user_prompt_clean, re.IGNORECASE)
            if match:
                # IMPORTANT: Capture from ORIGINAL prompt to preserve case for XPath selectors
                captured_value = match.group(config['capture_group']).strip()
                result = {
                    'placeholder': config['placeholder'],
                    'value': captured_value,
                    'pattern': pattern
                }
                
                # Handle patterns that extract field information (e.g., "enter VALUE in FIELD")
                if config.get('has_field') and 'field_group' in config:
                    try:
                        field_name = match.group(config['field_group']).strip()
                        result['field'] = field_name
                    except IndexError:
                        pass
                
                # Handle patterns that extract dropdown information (e.g., "select OPTION from DROPDOWN")
                if config.get('has_dropdown') and 'dropdown_group' in config:
                    try:
                        dropdown_name = match.group(config['dropdown_group']).strip()
                        result['dropdown'] = dropdown_name
                    except IndexError:
                        pass
                
                return result
        
        return None
    
    def substitute_in_code(self, code: str, placeholder: str, value: str) -> str:
        """
        Substitute placeholder with value in code
        
        Args:
            code: Template code with placeholders
            placeholder: Standardized placeholder (e.g., '{TAB}')
            value: Extracted value (e.g., "Overview")
        
        Returns:
            Code with substituted value
        """
        # Get all possible variations of this placeholder
        variations = self.PLACEHOLDER_SUBSTITUTIONS.get(placeholder, [placeholder])
        
        # Replace all variations in the code
        substituted_code = code
        for variation in variations:
            # Case-sensitive replacement
            substituted_code = substituted_code.replace(variation, value)
        
        return substituted_code
    
    def process_template_match(self, user_prompt: str, template_entry: dict, preserve_value_placeholder: bool = False) -> dict:
        """
        Process a template entry with parameter extraction and substitution
        
        Args:
            user_prompt: User's actual prompt
            template_entry: Template dataset entry
            preserve_value_placeholder: If True, keeps {VALUE} placeholder (for input fields where value comes from UI)
        
        Returns:
            Modified entry with substituted code, or original entry if no extraction
        """
        # Extract parameter from user prompt
        extracted = self.extract_parameter(user_prompt, template_entry.get('prompt', ''))
        
        if not extracted:
            # No parameter extracted, return as-is
            return template_entry
        
        # Create a copy to avoid modifying original
        result = template_entry.copy()
        
        # For input fields: if preserve_value_placeholder=True, DON'T substitute {VALUE}
        # This allows UI to provide the actual value later
        # For buttons/tabs: always substitute because value is in the prompt itself
        should_preserve_value = (preserve_value_placeholder and 
                                extracted['placeholder'] == '{VALUE}' and
                                'field' in extracted)  # Input field pattern
        
        if not should_preserve_value:
            # Substitute VALUE in code (for buttons, tabs, links, etc.)
            result['code'] = self.substitute_in_code(
                template_entry['code'],
                extracted['placeholder'],
                extracted['value']
            )
        
        # Always substitute FIELD placeholder (the field name itself)
        if 'field' in extracted:
            result['code'] = self.substitute_in_code(
                result['code'],
                '{FIELD}',
                extracted['field']
            )
        
        # If dropdown was extracted, also substitute DROPDOWN placeholder
        if 'dropdown' in extracted:
            result['code'] = self.substitute_in_code(
                result['code'],
                '{DROPDOWN}',
                extracted['dropdown']
            )
        
        # Substitute in xpath if present
        if 'xpath' in result and result['xpath']:
            if not should_preserve_value:
                result['xpath'] = self.substitute_in_code(
                    template_entry['xpath'],
                    extracted['placeholder'],
                    extracted['value']
                )
            
            # Also substitute FIELD in xpath if present
            if 'field' in extracted:
                result['xpath'] = self.substitute_in_code(
                    result['xpath'],
                    '{FIELD}',
                    extracted['field']
                )
            
            # Also substitute DROPDOWN in xpath if present
            if 'dropdown' in extracted:
                result['xpath'] = self.substitute_in_code(
                    result['xpath'],
                    '{DROPDOWN}',
                    extracted['dropdown']
                )
        
        # CRITICAL FIX: Substitute in fallback_selectors array if present
        # Works for ALL placeholders: {VALUE}, {TAB}, {LINK}, {MENU}, {FILENAME}, etc.
        if 'fallback_selectors' in result and result['fallback_selectors']:
            substituted_selectors = []
            for selector in template_entry.get('fallback_selectors', []):
                # For input fields with preserve_value_placeholder: keep {VALUE} in selectors
                # For buttons/tabs: substitute the value
                new_selector = selector
                if not should_preserve_value:
                    new_selector = self.substitute_in_code(
                        selector,
                        extracted['placeholder'],  # Works for {VALUE}, {TAB}, {LINK}, etc.
                        extracted['value']
                    )
                
                # Always substitute FIELD if present
                if 'field' in extracted:
                    new_selector = self.substitute_in_code(
                        new_selector,
                        '{FIELD}',
                        extracted['field']
                    )
                
                # Also substitute DROPDOWN if present
                if 'dropdown' in extracted:
                    new_selector = self.substitute_in_code(
                        new_selector,
                        '{DROPDOWN}',
                        extracted['dropdown']
                    )
                
                substituted_selectors.append(new_selector)
            
            result['fallback_selectors'] = substituted_selectors
        
        # Add metadata about substitution
        if 'metadata' not in result:
            result['metadata'] = {}
        
        result['metadata']['parameter_substituted'] = {
            'placeholder': extracted['placeholder'],
            'value': extracted['value'],
            'user_prompt': user_prompt
        }
        
        # Add field info if present
        if 'field' in extracted:
            result['metadata']['parameter_substituted']['field'] = extracted['field']
        
        # Add dropdown info if present
        if 'dropdown' in extracted:
            result['metadata']['parameter_substituted']['dropdown'] = extracted['dropdown']
        
        return result


def test_extractor():
    """Test the parameter extraction system"""
    extractor = TemplateParameterExtractor()
    
    test_cases = [
        ("click Overview tab", "click {tab} tab", "Overview"),
        ("click the Disclosures tab", "click {tab} tab", "Disclosures"),
        ("upload report.pdf", "attach {filename}", "report.pdf"),
        ("search for John Doe", "search for {criteria}", "John Doe"),
        ("get validation message for Email Address", "get validation message for {field}", "Email Address"),
        ("click SignOut button", "click {button} button", "SignOut"),
        ("select CA from 'state' dropdown", "select '{state}'", "CA"),
    ]
    
    print("Testing Parameter Extraction System")
    print("="*70)
    
    for i, (user_prompt, template, expected_value) in enumerate(test_cases, 1):
        extracted = extractor.extract_parameter(user_prompt, template)
        
        if extracted:
            success = extracted['value'].lower() == expected_value.lower()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} Test {i}: '{user_prompt}'")
            print(f"  Expected: {expected_value}")
            print(f"  Extracted: {extracted['value']}")
            print(f"  Placeholder: {extracted['placeholder']}")
        else:
            print(f"❌ FAIL Test {i}: '{user_prompt}' - No extraction")
        print()
    
    # Test substitution
    print("\nTesting Code Substitution")
    print("="*70)
    
    template_code = """WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[contains(text(), '{TAB}')]")));
element.click();"""
    
    substituted = extractor.substitute_in_code(template_code, '{TAB}', 'Overview')
    print("Original code:")
    print(template_code)
    print("\nSubstituted code (TAB='Overview'):")
    print(substituted)


if __name__ == "__main__":
    test_extractor()
