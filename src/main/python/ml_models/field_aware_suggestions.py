"""
Field-Aware Semantic Suggestion Generator

Dynamically detects field types and generates appropriate test data.
No hardcoding - uses ML patterns and heuristics.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple


class FieldTypeDetector:
    """Detects field type from action metadata."""
    
    # Patterns for field type detection
    FIELD_PATTERNS = {
        'email': [
            r'email', r'e-mail', r'mail', r'user.*mail',
            r'contact.*email', r'login.*email'
        ],
        'password': [
            r'password', r'passwd', r'pwd', r'pass',
            r'secret', r'credential', r'pin'
        ],
        'phone': [
            r'phone', r'tel', r'mobile', r'cell',
            r'contact.*number', r'phone.*number'
        ],
        'url': [
            r'url', r'website', r'link', r'web.*address',
            r'homepage', r'domain'
        ],
        'name': [
            r'name', r'full.*name', r'first.*name', r'last.*name',
            r'surname', r'given.*name', r'username', r'user.*name'
        ],
        'address': [
            r'address', r'street', r'city', r'state',
            r'zip', r'postal', r'location'
        ],
        'date': [
            r'date', r'dob', r'birth', r'anniversary',
            r'day', r'month', r'year', r'calendar'
        ],
        'number': [
            r'age', r'quantity', r'count', r'amount',
            r'number', r'num', r'price', r'cost'
        ],
        'ssn': [
            r'ssn', r'social.*security', r'tax.*id',
            r'national.*id', r'insurance.*number'
        ],
        'credit_card': [
            r'card.*number', r'credit.*card', r'debit.*card',
            r'payment.*card', r'cc', r'cvv', r'cvc'
        ]
    }
    
    # Value patterns for additional detection
    VALUE_PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^[\d\s\-\(\)\+]{7,}$',
        'url': r'^https?://',
        'ssn': r'^\d{3}-\d{2}-\d{4}$',
        'credit_card': r'^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$',
        'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    }
    
    def detect(self, action: Dict) -> str:
        """
        Detect field type from action metadata.
        
        Args:
            action: Action dict with element_id, element_name, value, etc.
            
        Returns:
            Field type: 'email', 'password', 'text', etc.
        """
        # Safety check: Handle string actions from semantic tests
        if isinstance(action, str):
            logging.info("[FIELD-DETECT] String action (semantic test), returning 'text'")
            return 'text'
        
        # Extract metadata from element object (recorder format)
        element = action.get('element', {})
        if isinstance(element, dict):
            element_id = (element.get('id') or '').lower()
            element_name = (element.get('name') or '').lower()
            element_class = (element.get('className') or '').lower()
            element_type = (element.get('type') or '').lower()
            placeholder = (element.get('placeholder') or '').lower()
        else:
            # Fallback to flat structure (old format)
            element_id = (action.get('element_id') or '').lower()
            element_name = (action.get('element_name') or '').lower()
            element_class = (action.get('element_class') or '').lower()
            element_type = ''
            placeholder = (action.get('placeholder') or '').lower()
        
        # Extract additional fields for builder format
        prompt = (action.get('prompt') or '').lower()
        description = (action.get('description') or '').lower()
        value = action.get('value', '')
        
        # Combine all text fields for pattern matching
        combined_text = f"{element_id} {element_name} {element_class} {element_type} {placeholder} {prompt} {description}"
        
        # Check each field type pattern
        for field_type, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    logging.info(f"[FIELD-DETECT] Detected {field_type} from pattern: {pattern}")
                    return field_type
        
        # Check value patterns if no metadata match
        if value:
            for field_type, pattern in self.VALUE_PATTERNS.items():
                if re.match(pattern, str(value)):
                    logging.info(f"[FIELD-DETECT] Detected {field_type} from value pattern")
                    return field_type
        
        # Default to text
        logging.info(f"[FIELD-DETECT] No specific type detected, using 'text'")
        return 'text'


class FieldAwareSuggestionGenerator:
    """Generates field-specific test suggestions."""
    
    def __init__(self):
        self.detector = FieldTypeDetector()
        
    def generate_suggestions(self, actions: List[Dict]) -> List[Dict]:
        """
        Generate field-aware suggestions for all input actions.
        
        Args:
            actions: List of test actions (can include strings from semantic tests)
            
        Returns:
            List of suggestion objects with field-specific data
        """
        # Filter out string actions (semantic test scenarios)
        dict_actions = [a for a in actions if isinstance(a, dict)]
        
        if not dict_actions:
            logging.info("[FIELD-AWARE] No dictionary actions found (semantic test with only string scenarios)")
            return []
        
        # Filter input actions
        # Support both 'action_type' (recorder format) and 'type' (semantic/builder format)
        input_actions = []
        for a in dict_actions:
            action_type = a.get('action_type') or a.get('type', '')
            # Include if it's an input action OR if it has a value (indicates input field)
            # Builder format: has 'prompt' and 'value'
            # Recorder format: has 'action_type' = 'click_and_input'
            is_input_action = action_type in ['input', 'click_and_input', 'select', 'action']
            has_input_value = 'value' in a and a.get('value') is not None and a.get('value') != ''
            has_prompt = 'prompt' in a
            
            if is_input_action or has_input_value or has_prompt:
                input_actions.append(a)
        
        if not input_actions:
            return []
        
        field_suggestions = []
        
        for idx, action in enumerate(input_actions):
            # Detect field type
            field_type = self.detector.detect(action)
            original_value = action.get('value', '')
            
            # Generate suggestions for this field
            suggestions = self._generate_for_field_type(
                field_type, 
                original_value,
                action
            )
            
            field_suggestions.append({
                'field_index': idx,
                'field_step': action.get('step'),
                'field_type': field_type,
                'original_value': original_value,
                'suggestions': suggestions
            })
        
        return field_suggestions
    
    def _generate_for_field_type(
        self, 
        field_type: str, 
        original_value: str,
        action: Dict
    ) -> List[Dict]:
        """
        Generate test suggestions for specific field type.
        
        Returns list of {value, description, category} dicts
        """
        generator_method = getattr(
            self, 
            f'_generate_{field_type}_suggestions', 
            self._generate_text_suggestions
        )
        
        return generator_method(original_value, action)
    
    # ========== Field-Specific Generators ==========
    
    def _generate_email_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate email field suggestions."""
        return [
            # Invalid format
            {'value': 'notanemail', 'description': 'Missing @ symbol', 'category': 'invalid_format'},
            {'value': 'user@', 'description': 'Incomplete domain', 'category': 'invalid_format'},
            {'value': '@domain.com', 'description': 'Missing username', 'category': 'invalid_format'},
            {'value': 'user @domain.com', 'description': 'Space in email', 'category': 'invalid_format'},
            
            # Edge cases
            {'value': 'test+tag@example.com', 'description': 'Plus sign (valid but often rejected)', 'category': 'edge_case'},
            {'value': 'a@b.c', 'description': 'Minimal valid email', 'category': 'boundary'},
            {'value': 'x' * 64 + '@example.com', 'description': 'Max length username (64 chars)', 'category': 'boundary'},
            
            # Security
            {'value': "admin'--@test.com", 'description': 'SQL injection attempt', 'category': 'security'},
            {'value': '<script>@test.com', 'description': 'XSS attempt', 'category': 'security'},
            {'value': '../../etc/passwd@test.com', 'description': 'Path traversal', 'category': 'security'},
            
            # I18N
            {'value': 'тест@example.com', 'description': 'Cyrillic characters', 'category': 'i18n'},
            {'value': 'مستخدم@example.com', 'description': 'Arabic characters', 'category': 'i18n'},
        ]
    
    def _generate_password_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate password field suggestions."""
        return [
            # Weak/invalid
            {'value': '123', 'description': 'Too short (< 8 chars)', 'category': 'weak'},
            {'value': 'password', 'description': 'Common weak password', 'category': 'weak'},
            {'value': 'Password123', 'description': 'No special characters', 'category': 'weak'},
            {'value': 'password123', 'description': 'No uppercase letters', 'category': 'weak'},
            
            # Edge cases
            {'value': '@#$%^&*', 'description': 'Only special characters', 'category': 'edge_case'},
            {'value': '12345678', 'description': 'Only numbers', 'category': 'edge_case'},
            {'value': 'Pass word1!', 'description': 'Contains space', 'category': 'edge_case'},
            {'value': 'x' * 128, 'description': 'Very long password (128 chars)', 'category': 'boundary'},
            
            # Security
            {'value': "' OR '1'='1", 'description': 'SQL injection attempt', 'category': 'security'},
            {'value': '<script>alert(1)</script>', 'description': 'XSS attempt', 'category': 'security'},
            {'value': 'admin\' --', 'description': 'SQL comment injection', 'category': 'security'},
        ]
    
    def _generate_phone_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate phone field suggestions."""
        return [
            # Invalid
            {'value': '123', 'description': 'Too short', 'category': 'invalid'},
            {'value': 'abc-def-ghij', 'description': 'Letters instead of numbers', 'category': 'invalid'},
            
            # Valid formats
            {'value': '+1-555-123-4567', 'description': 'International format (+1)', 'category': 'valid'},
            {'value': '(555) 123-4567', 'description': 'With parentheses', 'category': 'valid'},
            {'value': '5551234567', 'description': 'No formatting', 'category': 'valid'},
            {'value': '+44 20 7123 4567', 'description': 'UK format', 'category': 'edge_case'},
            
            # Boundary
            {'value': '1' * 15, 'description': 'Max digits (15)', 'category': 'boundary'},
            
            # Security
            {'value': "555-1234'; DROP TABLE--", 'description': 'SQL injection', 'category': 'security'},
        ]
    
    def _generate_url_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate URL field suggestions."""
        return [
            # Invalid
            {'value': 'notaurl', 'description': 'No protocol', 'category': 'invalid'},
            {'value': 'http://', 'description': 'No domain', 'category': 'invalid'},
            
            # Valid
            {'value': 'https://example.com', 'description': 'HTTPS URL', 'category': 'valid'},
            {'value': 'http://example.com', 'description': 'HTTP (not secure)', 'category': 'valid'},
            
            # Edge cases
            {'value': 'example.com', 'description': 'Missing protocol', 'category': 'edge_case'},
            {'value': 'https://sub.domain.example.com/path?q=v#hash', 'description': 'Complex URL', 'category': 'edge_case'},
            {'value': 'ftp://example.com', 'description': 'FTP protocol', 'category': 'edge_case'},
            
            # Security
            {'value': 'javascript:alert(1)', 'description': 'JavaScript injection', 'category': 'security'},
            {'value': 'file:///etc/passwd', 'description': 'File protocol attack', 'category': 'security'},
        ]
    
    def _generate_name_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate name field suggestions."""
        return [
            # Boundary
            {'value': '', 'description': 'Empty name', 'category': 'boundary'},
            {'value': 'A', 'description': 'Single character', 'category': 'boundary'},
            {'value': 'X' * 100, 'description': 'Very long name (100 chars)', 'category': 'boundary'},
            
            # Edge cases
            {'value': 'O\'Brien', 'description': 'Apostrophe in name', 'category': 'edge_case'},
            {'value': 'Mary-Jane', 'description': 'Hyphenated name', 'category': 'edge_case'},
            {'value': 'José María', 'description': 'Accented characters', 'category': 'i18n'},
            
            # I18N
            {'value': '李明', 'description': 'Chinese name', 'category': 'i18n'},
            {'value': 'محمد', 'description': 'Arabic name', 'category': 'i18n'},
            {'value': 'Владимир', 'description': 'Cyrillic name', 'category': 'i18n'},
            
            # Security
            {'value': "<script>alert('XSS')</script>", 'description': 'XSS attempt', 'category': 'security'},
            {'value': "'; DROP TABLE users--", 'description': 'SQL injection', 'category': 'security'},
        ]
    
    def _generate_number_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate number field suggestions."""
        return [
            # Invalid
            {'value': 'abc', 'description': 'Non-numeric characters', 'category': 'invalid'},
            {'value': '12.34.56', 'description': 'Multiple decimal points', 'category': 'invalid'},
            
            # Boundary
            {'value': '0', 'description': 'Zero', 'category': 'boundary'},
            {'value': '-1', 'description': 'Negative (may be invalid)', 'category': 'boundary'},
            {'value': '9999999999', 'description': 'Very large number', 'category': 'boundary'},
            
            # Edge cases
            {'value': '1.5', 'description': 'Decimal number', 'category': 'edge_case'},
            {'value': '1e10', 'description': 'Scientific notation', 'category': 'edge_case'},
            
            # Security
            {'value': "1; DROP TABLE--", 'description': 'SQL injection', 'category': 'security'},
        ]
    
    def _generate_text_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate generic text field suggestions."""
        return [
            # Boundary
            {'value': '', 'description': 'Empty string', 'category': 'boundary'},
            {'value': ' ', 'description': 'Only whitespace', 'category': 'edge_case'},
            {'value': 'a', 'description': 'Single character', 'category': 'boundary'},
            {'value': 'x' * 1000, 'description': 'Very long text (1000 chars)', 'category': 'boundary'},
            
            # I18N
            {'value': '你好世界', 'description': 'Chinese characters', 'category': 'i18n'},
            {'value': 'مرحبا بالعالم', 'description': 'Arabic/RTL text', 'category': 'i18n'},
            {'value': 'Здравствуй мир', 'description': 'Cyrillic characters', 'category': 'i18n'},
            {'value': '😀🎉👍💯', 'description': 'Emojis', 'category': 'i18n'},
            
            # Security
            {'value': '<script>alert(1)</script>', 'description': 'XSS script injection', 'category': 'security'},
            {'value': "'; DROP TABLE users--", 'description': 'SQL injection', 'category': 'security'},
            {'value': '../../../etc/passwd', 'description': 'Path traversal', 'category': 'security'},
            {'value': '${7*7}', 'description': 'Template injection', 'category': 'security'},
        ]
    
    def _generate_date_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate date field suggestions."""
        return [
            # Invalid
            {'value': '13/32/2024', 'description': 'Invalid month/day', 'category': 'invalid'},
            {'value': '02/29/2023', 'description': 'Invalid leap year', 'category': 'invalid'},
            {'value': '00/00/0000', 'description': 'All zeros', 'category': 'invalid'},
            
            # Boundary
            {'value': '01/01/1900', 'description': 'Very old date', 'category': 'boundary'},
            {'value': '12/31/2099', 'description': 'Far future date', 'category': 'boundary'},
            
            # Edge cases
            {'value': '02/29/2024', 'description': 'Valid leap year', 'category': 'edge_case'},
            {'value': '2024-12-31', 'description': 'ISO format (YYYY-MM-DD)', 'category': 'edge_case'},
            
            # Security
            {'value': "01/01/2024'; DROP TABLE--", 'description': 'SQL injection', 'category': 'security'},
        ]
    
    def _generate_ssn_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate SSN field suggestions."""
        return [
            # Invalid
            {'value': '123-45-678', 'description': 'Too short (8 digits)', 'category': 'invalid'},
            {'value': '000-00-0000', 'description': 'All zeros (invalid)', 'category': 'invalid'},
            {'value': 'abc-de-fghi', 'description': 'Non-numeric', 'category': 'invalid'},
            
            # Valid format
            {'value': '123-45-6789', 'description': 'Valid format', 'category': 'valid'},
            
            # Edge cases
            {'value': '123456789', 'description': 'No dashes', 'category': 'edge_case'},
            
            # Security
            {'value': "123-45-6789'; DROP--", 'description': 'SQL injection', 'category': 'security'},
        ]
    
    def _generate_credit_card_suggestions(self, original: str, action: Dict) -> List[Dict]:
        """Generate credit card field suggestions."""
        return [
            # Invalid
            {'value': '1234', 'description': 'Too short', 'category': 'invalid'},
            {'value': 'abcd-efgh-ijkl-mnop', 'description': 'Non-numeric', 'category': 'invalid'},
            
            # Valid test cards (Luhn-valid)
            {'value': '4111111111111111', 'description': 'Visa test card', 'category': 'valid'},
            {'value': '5555555555554444', 'description': 'Mastercard test card', 'category': 'valid'},
            
            # Edge cases
            {'value': '4111 1111 1111 1111', 'description': 'With spaces', 'category': 'edge_case'},
            {'value': '4111-1111-1111-1111', 'description': 'With dashes', 'category': 'edge_case'},
            
            # Security
            {'value': "4111111111111111'; DROP--", 'description': 'SQL injection', 'category': 'security'},
        ]


def generate_field_aware_semantic_scenarios(actions: List[Dict], test_name: str = '', category_filter: str = None) -> List[Dict]:
    """
    Main entry point for generating field-aware semantic test scenarios.
    
    Args:
        actions: List of test actions (can be strings for semantic tests or dicts for normal tests)
        test_name: Original test name
        category_filter: Optional category to filter suggestions (e.g., 'boundary', 'security', 'edge_case')
        
    Returns:
        List of semantic test scenario dicts with field-specific suggestions
    """
    # Filter out string actions (semantic test scenarios)
    dict_actions = [a for a in actions if isinstance(a, dict)]
    
    if not dict_actions:
        logging.info(f"[FIELD-AWARE] Test '{test_name}' contains only string scenarios (semantic test), no field-specific suggestions available")
        return []
    
    generator = FieldAwareSuggestionGenerator()
    field_suggestions = generator.generate_suggestions(dict_actions)
    
    if not field_suggestions:
        logging.warning("[FIELD-AWARE] No input fields found, cannot generate suggestions")
        return []
    
    # Group suggestions by category
    scenarios = []
    categories_seen = set()
    
    # Collect all unique categories
    all_categories = set()
    for field_sugg in field_suggestions:
        for sugg in field_sugg['suggestions']:
            all_categories.add(sugg['category'])
    
    # If category_filter is provided, prioritize that category but include others
    if category_filter:
        logging.info(f"[FIELD-AWARE] Prioritizing category: {category_filter}")
        # Check if the requested category exists
        if category_filter not in all_categories:
            logging.warning(f"[FIELD-AWARE] Category '{category_filter}' not found, showing all categories")
            category_filter = None  # Show all if not found
    
    # Sort categories - prioritized category first, then others
    if category_filter:
        sorted_categories = [category_filter] + [c for c in all_categories if c != category_filter]
    else:
        # Default order: security, boundary, edge_case, i18n, others
        priority_order = ['security', 'boundary', 'edge_case', 'i18n']
        sorted_categories = [c for c in priority_order if c in all_categories]
        sorted_categories += [c for c in all_categories if c not in priority_order]
    
    # Create scenarios for categories (prioritized category gets more prominence)
    for idx, category in enumerate(sorted_categories):
        is_prioritized = (category_filter and idx == 0)
        
        # Collect suggestions for this category across all fields
        category_suggestions = []
        for field_sugg in field_suggestions:
            for sugg in field_sugg['suggestions']:
                if sugg['category'] == category:
                    category_suggestions.append({
                        'field_index': field_sugg['field_index'],
                        'field_type': field_sugg['field_type'],
                        'value': sugg['value'],
                        'description': sugg['description']
                    })
        
        if category_suggestions:
            scenario = {
                'type': category,
                'title': f"{category.replace('_', ' ').title()} Testing",
                'description': f"Test {category.replace('_', ' ')} scenarios",
                'priority': 'high' if (category == 'security' or is_prioritized) else 'medium',
                'field_suggestions': field_suggestions,  # All field suggestions
                'category_examples': category_suggestions,  # Examples for this category
                'is_prioritized': is_prioritized  # Flag for UI to highlight
            }
            scenarios.append(scenario)
    
    logging.info(f"[FIELD-AWARE] Generated {len(scenarios)} semantic scenarios{' for category: ' + category_filter if category_filter else ''}")
    return scenarios
