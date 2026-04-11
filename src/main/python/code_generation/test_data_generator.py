"""
Test Data Generator - Context-aware test data generation for ANY test case.

Generates intelligent test data for:
- Negative testing (invalid data)
- Boundary testing (min/max values)
- Variation testing (alternative valid data)

Works universally across all field types and workflows.
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from .field_analyzer import FieldAnalyzer


class TestDataGenerator:
    """Generates context-aware test data for various testing scenarios."""
    
    @staticmethod
    def generate_invalid_data(field_value: str, locator: str, action_text: str, 
                             test_context: Dict, step: int) -> Tuple[str, str]:
        """Generate context-aware invalid test data for ANY test case type.
        
        Universal approach - works for login, registration, e-commerce, applications, 
        profiles, search, data entry, and any other workflow.
        
        Args:
            field_value: Original field value
            locator: Field locator string
            action_text: Action description
            test_context: Test context dictionary
            step: Step number for variation
            
        Returns:
            Tuple[str, str]: (invalid_value, reason)
        """
        # Extract field info dynamically (no hardcoding)
        combined_text = f"{locator} {action_text} {field_value}".lower()
        inferred_type = FieldAnalyzer.infer_field_type_from_text(combined_text, field_value)
        workflow = test_context.get('workflow', 'unknown')
        
        # Generate invalid data based on detected field type (UNIVERSAL)
        
        # Authentication & Profile fields
        if inferred_type == 'email':
            options = [
                ('notanemail', 'Missing @ symbol'),
                ('user@', 'Missing domain'),
                ('@domain.com', 'Missing username'),
                ('user..name@domain.com', 'Consecutive dots'),
                ('user@domain', 'Missing TLD'),
                ('user name@domain.com', 'Contains space'),
            ]
            return options[step % len(options)]
        
        elif inferred_type == 'password':
            if workflow == 'authentication':
                return ('wrong', 'Incorrect password')
            else:  # registration, change password, etc.
                return ('abc', 'Too weak/short')
        
        elif inferred_type == 'username':
            return ('a', 'Too short username')
        
        # Contact & Personal Info
        elif inferred_type == 'phone':
            options = [
                ('123-45', 'Incomplete phone'),
                ('abcd-efgh', 'Non-numeric characters'),
                ('000-000-0000', 'Invalid phone number')
            ]
            return options[step % len(options)]
        
        elif inferred_type == 'name':
            options = [
                ('123', 'Numeric characters'),
                ('!@#', 'Special characters only'),
                ('', 'Empty name')
            ]
            return options[step % len(options)]
        
        elif inferred_type == 'address':
            return ('', 'Empty address field')
        
        # Date & Time
        elif inferred_type == 'date':
            options = [
                ('13/32/2099', 'Invalid date values'),
                ('00/00/0000', 'Zero date'),
                ('99/99/9999', 'Out of range'),
                ('not-a-date', 'Invalid format')
            ]
            return options[step % len(options)]
        
        elif inferred_type == 'time':
            return ('25:99', 'Invalid time')
        
        # E-commerce fields
        elif inferred_type == 'credit_card':
            options = [
                ('1234-5678-9012', 'Incomplete card number'),
                ('0000-0000-0000-0000', 'Invalid card'),
                ('abcd-efgh-ijkl-mnop', 'Non-numeric')
            ]
            return options[step % len(options)]
        
        elif inferred_type == 'price':
            return ('-10.50', 'Negative price')
        
        elif inferred_type == 'zip_code':
            return ('123', 'Invalid ZIP length')
        
        # Application/Government fields
        elif inferred_type == 'ssn':
            return ('123-45', 'Incomplete SSN')
        
        elif inferred_type == 'license_number':
            return ('ABC', 'Invalid format')
        
        # Numeric fields
        elif inferred_type == 'number':
            # Context-specific invalid numbers
            if 'age' in combined_text:
                return ('-5', 'Negative age')
            elif 'quantity' in combined_text or 'qty' in combined_text:
                return ('0', 'Zero quantity')
            else:
                return ('-1', 'Negative number')
        
        # Text input fields
        elif inferred_type == 'textarea':
            return ('', 'Empty description')
        
        elif inferred_type == 'search':
            return ('', 'Empty search query')
        
        elif inferred_type == 'url':
            return ('not-a-url', 'Invalid URL format')
        
        elif inferred_type == 'company':
            return ('', 'Empty company name')
        
        elif inferred_type == 'title':
            return ('', 'Empty job title')
        
        # File uploads
        elif inferred_type == 'file_upload':
            return ('invalid.xyz', 'Unsupported file type')
        
        # Selection fields
        elif inferred_type in ['select', 'checkbox', 'radio']:
            return ('', 'No selection made')
        
        # Generic fallback
        return ('', 'Empty required field')
    
    @staticmethod
    def generate_boundary_data(field_value: str, locator: str, action_text: str, 
                              test_context: Dict, step: int) -> Tuple[str, str]:
        """Generate boundary test data for ANY test case type (Universal).
        
        Works for: login, registration, e-commerce, applications, profiles, 
        search, data entry, and any other workflow.
        
        Args:
            field_value: Original field value
            locator: Field locator string
            action_text: Action description
            test_context: Test context dictionary
            step: Step number for variation
            
        Returns:
            Tuple[str, str]: (boundary_value, reason)
        """
        # Extract field info dynamically
        combined_text = f"{locator} {action_text} {field_value}".lower()
        inferred_type = FieldAnalyzer.infer_field_type_from_text(combined_text, field_value)
        max_length = FieldAnalyzer.infer_max_length(combined_text, field_value)
        
        # Generate boundary values for ALL field types
        
        # Authentication & Profile
        if inferred_type == 'email':
            if step % 2 == 0:
                return ('a@b.c', 'Minimum valid email (5 chars)')
            else:
                if max_length:
                    long_email = 'a' * (max_length - 10) + '@test.com'
                    return (long_email, f'Maximum email ({max_length} chars)')
                return ('verylongemailaddress123@example-domain.com', 'Long email')
        
        elif inferred_type == 'password':
            if step % 2 == 0:
                return ('Pass123!', 'Minimum valid (8 chars)')
            else:
                return ('P' * (max_length or 128), f'Maximum ({max_length or 128} chars)')
        
        elif inferred_type == 'username':
            if step % 2 == 0:
                return ('u', 'Minimum username')
            else:
                return ('username' * 10, 'Very long username')
        
        # Contact Info
        elif inferred_type == 'phone':
            return ('1234567890', 'Exactly 10 digits')
        
        elif inferred_type == 'name':
            if step % 2 == 0:
                return ('A', 'Single character')
            else:
                return ('A' * 100, 'Very long name')
        
        elif inferred_type == 'address':
            if step % 2 == 0:
                return ('1 A St', 'Minimum address')
            else:
                return ('1234 Very Long Street Name Avenue Suite 500' * 3, 'Very long address')
        
        # Date & Time
        elif inferred_type == 'date':
            if step % 2 == 0:
                return ('01/01/1900', 'Minimum date')
            else:
                return ('12/31/2099', 'Maximum date')
        
        elif inferred_type == 'time':
            if step % 2 == 0:
                return ('00:00', 'Midnight')
            else:
                return ('23:59', 'Last minute')
        
        # E-commerce
        elif inferred_type == 'credit_card':
            return ('4111111111111111', 'Valid test card (16 digits)')
        
        elif inferred_type == 'price':
            if step % 2 == 0:
                return ('0.01', 'Minimum price')
            else:
                return ('999999.99', 'Maximum price')
        
        elif inferred_type == 'zip_code':
            if step % 2 == 0:
                return ('00001', 'Minimum ZIP')
            else:
                return ('99999-9999', 'Maximum ZIP+4')
        
        # Application fields
        elif inferred_type == 'ssn':
            return ('000-00-0001', 'Minimum SSN value')
        
        elif inferred_type == 'license_number':
            return ('A00000000', 'Minimum license format')
        
        # Numeric fields
        elif inferred_type == 'number':
            if 'age' in combined_text:
                if step % 2 == 0:
                    return ('0', 'Minimum age')
                else:
                    return ('120', 'Maximum age')
            elif 'quantity' in combined_text or 'qty' in combined_text:
                if step % 2 == 0:
                    return ('1', 'Minimum quantity')
                else:
                    return ('999999', 'Maximum quantity')
            else:
                if step % 2 == 0:
                    return ('0', 'Minimum')
                else:
                    return ('999999999', 'Maximum')
        
        # Text fields
        elif inferred_type == 'textarea':
            if step % 2 == 0:
                return ('A', 'Single character')
            else:
                return ('X' * 5000, 'Very long text (5000 chars)')
        
        elif inferred_type == 'search':
            if step % 2 == 0:
                return ('a', 'Single char search')
            else:
                return ('search term' * 20, 'Very long query')
        
        elif inferred_type == 'url':
            if step % 2 == 0:
                return ('http://a.co', 'Minimum URL')
            else:
                return ('http://' + 'subdomain.' * 10 + 'example.com/path', 'Very long URL')
        
        elif inferred_type == 'company':
            if step % 2 == 0:
                return ('A', 'Minimum company name')
            else:
                return ('Very Long Company Name Corporation International' * 3, 'Long company')
        
        # Generic text fallback
        if step % 2 == 0:
            return ('A', 'Minimum (1 char)')
        else:
            return ('X' * (max_length or 255), f'Maximum ({max_length or 255} chars)')
    
    @staticmethod
    def generate_variation_data(field_value: str, locator: str, action_text: str, 
                               test_context: Dict, step: int) -> Tuple[str, str]:
        """Generate variation test data for ANY test case type (Universal).
        
        Works for: login, registration, e-commerce, applications, profiles,
        search, data entry, and any other workflow.
        
        Args:
            field_value: Original field value
            locator: Field locator string
            action_text: Action description
            test_context: Test context dictionary
            step: Step number for variation
            
        Returns:
            Tuple[str, str]: (variation_value, reason)
        """
        # Extract field info dynamically
        combined_text = f"{locator} {action_text} {field_value}".lower()
        inferred_type = FieldAnalyzer.infer_field_type_from_text(combined_text, field_value)
        workflow = test_context.get('workflow', 'unknown')
        business_domain = test_context.get('business_domain', 'general')
        
        # Generate variations for ALL field types
        
        # Authentication & Profile
        if inferred_type == 'email':
            variations = [
                ('test.user@company.com', 'Corporate format'),
                ('user.name+tag@email.co.uk', 'Plus addressing'),
                ('firstname.lastname@domain.io', 'Professional format'),
                ('user_123@subdomain.example.org', 'Underscores & subdomain')
            ]
            return variations[step % len(variations)]
        
        elif inferred_type == 'password':
            if workflow == 'authentication':
                return ('AlternativePass123!', 'Different valid password')
            else:
                variations = [
                    ('SecureP@ssw0rd2024', 'Complex with symbols'),
                    ('MyStr0ng!Pass', 'Mixed case'),
                    ('P@ssword123!', 'Standard secure')
                ]
                return variations[step % len(variations)]
        
        elif inferred_type == 'username':
            variations = [
                ('alternative_user', 'Underscore format'),
                ('user.name', 'Dot format'),
                ('user123', 'Numeric suffix')
            ]
            return variations[step % len(variations)]
        
        # Contact Info
        elif inferred_type == 'phone':
            variations = [
                ('(555) 123-4567', 'Parentheses format'),
                ('555-123-4567', 'Dashed format'),
                ('555.123.4567', 'Dotted format'),
                ('+1-555-123-4567', 'International')
            ]
            return variations[step % len(variations)]
        
        elif inferred_type == 'name':
            variations = [
                ('Jane Smith', 'Common name'),
                ("Michael O'Brien", 'With apostrophe'),
                ('José García', 'With accents'),
                ('Dr. Sarah Johnson', 'With title')
            ]
            return variations[step % len(variations)]
        
        elif inferred_type == 'address':
            variations = [
                ('456 Oak Avenue', 'Avenue format'),
                ('789 Main Street Apt 3B', 'With apartment'),
                ('PO Box 12345', 'PO Box format')
            ]
            return variations[step % len(variations)]
        
        # Date & Time
        elif inferred_type == 'date':
            variations = [
                ('01/15/1990', 'Alternative date'),
                ('12/25/2000', 'Holiday date'),
                ('06/30/1985', 'Mid-year')
            ]
            return variations[step % len(variations)]
        
        elif inferred_type == 'time':
            return ('15:30', 'Afternoon time')
        
        # E-commerce
        elif inferred_type == 'credit_card':
            variations = [
                ('5555555555554444', 'Mastercard test'),
                ('378282246310005', 'Amex test'),
                ('6011111111111117', 'Discover test')
            ]
            return variations[step % len(variations)]
        
        elif inferred_type == 'price':
            return ('199.99', 'Alternative price')
        
        elif inferred_type == 'zip_code':
            return ('90210', 'Different ZIP')
        
        # Application fields
        elif inferred_type == 'ssn':
            return ('123-45-6789', 'Alternative SSN format')
        
        elif inferred_type == 'license_number':
            if business_domain == 'insurance_licensing':
                return ('L987654321', 'Alternative license')
            else:
                return ('LIC-ALT-001', 'Alternative format')
        
        # Numeric fields
        elif inferred_type == 'number':
            if 'age' in combined_text:
                return ('35', 'Alternative age')
            elif 'quantity' in combined_text or 'qty' in combined_text:
                return ('5', 'Alternative quantity')
            else:
                return ('42', 'Alternative number')
        
        # Text fields
        elif inferred_type == 'textarea':
            return ('Alternative description with more details and information.', 'Longer description')
        
        elif inferred_type == 'search':
            return ('alternative query', 'Different search')
        
        elif inferred_type == 'url':
            return ('https://alternative-site.com', 'Alternative URL')
        
        elif inferred_type == 'company':
            if business_domain == 'insurance_licensing':
                return ('Alternative Insurance Agency LLC', 'Different insurance company')
            else:
                return ('XYZ Corporation Inc.', 'Alternative company')
        
        elif inferred_type == 'title':
            return ('Senior Software Engineer', 'Alternative title')
        
        # Generic variation
        return (f'Alternative {field_value}', 'Different valid input')
