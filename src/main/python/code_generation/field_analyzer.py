"""
Field Analyzer - Universal field type detection for ANY test case.

Supports 30+ field types across all workflows:
- Authentication (email, password, username)
- Contact (phone, name, address)
- E-commerce (credit_card, price, zip_code)
- Applications (ssn, license_number)
- Date/Time (date, time, datetime)
- And more...
"""

import re
import logging
from typing import Dict, List, Optional, Any


class FieldAnalyzer:
    """Analyzes fields to detect types and validation rules."""
    
    @staticmethod
    def infer_field_type_from_text(text: str, value: str) -> str:
        """Infer field type by analyzing text and value patterns (Universal AI approach).
        
        Works for ANY test case - not just login. Analyzes actual patterns in data.
        Supports: forms, e-commerce, applications, profiles, search, data entry, etc.
        
        Args:
            text: Combined text from locator, action text, etc.
            value: The actual field value
            
        Returns:
            str: Detected field type (email, phone, password, etc.)
        """
        text_lower = text.lower()
        
        # Priority 1: Analyze actual value patterns (most reliable)
        if value:
            # Email pattern (works for registration, profile, contact forms, etc.)
            if re.search(r'[@].*[.]', value):
                return 'email'
            
            # Phone patterns (US, international, formatted/unformatted)
            if re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', value):
                return 'phone'
            
            # Date patterns (MM/DD/YYYY, DD-MM-YYYY, ISO, etc.)
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', value) or \
               re.search(r'\d{4}-\d{2}-\d{2}', value):
                return 'date'
            
            # Time patterns (HH:MM, HH:MM:SS, 12h/24h)
            if re.search(r'\d{1,2}:\d{2}(:\d{2})?(\s?[AaPp][Mm])?', value):
                return 'time'
            
            # URL patterns (http://, https://, www., etc.)
            if re.search(r'https?://|www\.', value):
                return 'url'
            
            # Credit card patterns (for e-commerce)
            if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', value):
                return 'credit_card'
            
            # SSN patterns (for applications)
            if re.search(r'\d{3}-\d{2}-\d{4}', value):
                return 'ssn'
            
            # ZIP code patterns (US: 5 or 9 digits)
            if re.search(r'^\d{5}(-\d{4})?$', value):
                return 'zip_code'
            
            # Currency/price patterns (for e-commerce)
            if re.search(r'^\$?\d+(\.\d{2})?$', value) or re.search(r'^\d+(\.\d{2})?\s?(USD|EUR|GBP)$', value):
                return 'price'
            
            # Pure numeric (quantity, age, count, etc.)
            if value.isdigit():
                return 'number'
            
            # Boolean-like values (checkboxes, toggles)
            if value.lower() in ['true', 'false', 'yes', 'no', 'on', 'off', '1', '0']:
                return 'boolean'
        
        # Priority 2: Analyze text context (field name, label, placeholder)
        
        # Password fields (login, registration, change password, etc.)
        if any(keyword in text_lower for keyword in ['password', 'passwd', 'pwd', 'pass']):
            return 'password'
        
        # Username/userid (not email)
        if any(keyword in text_lower for keyword in ['username', 'userid', 'user-id', 'login-id']):
            return 'username'
        
        # Email (if not detected from value)
        if any(keyword in text_lower for keyword in ['email', 'e-mail', 'mail']):
            return 'email'
        
        # Phone (if not detected from value)
        if any(keyword in text_lower for keyword in ['phone', 'telephone', 'tel', 'mobile', 'cell']):
            return 'phone'
        
        # Names (first, last, full, middle)
        if any(keyword in text_lower for keyword in ['name', 'firstname', 'lastname', 'fullname']):
            return 'name'
        
        # Address fields (street, city, state, country)
        if any(keyword in text_lower for keyword in ['address', 'street', 'addr', 'city', 'town', 'state', 'province', 'country']):
            return 'address'
        
        # Date/Birth Date
        if any(keyword in text_lower for keyword in ['date', 'birth', 'dob', 'expiry', 'expiration']):
            return 'date'
        
        # File uploads (profile picture, documents, attachments)
        if any(keyword in text_lower for keyword in ['upload', 'file', 'attach', 'document', 'browse', 'image', 'photo']):
            return 'file_upload'
        
        # Dropdown/Select (category, type, status, etc.)
        if any(keyword in text_lower for keyword in ['select', 'dropdown', 'choose', 'option', 'category', 'type']):
            return 'select'
        
        # Textarea (description, comments, notes, bio)
        if any(keyword in text_lower for keyword in ['textarea', 'description', 'comment', 'note', 'message', 'bio', 'about']):
            return 'textarea'
        
        # Checkbox (terms, agreement, newsletter, preferences)
        if any(keyword in text_lower for keyword in ['checkbox', 'check', 'agree', 'accept', 'terms', 'newsletter']):
            return 'checkbox'
        
        # Radio button (gender, yes/no, single choice)
        if any(keyword in text_lower for keyword in ['radio', 'gender', 'sex', 'choice']):
            return 'radio'
        
        # Search fields (query, keyword, find)
        if any(keyword in text_lower for keyword in ['search', 'query', 'find', 'keyword', 'lookup']):
            return 'search'
        
        # Numeric fields (age, quantity, amount, count, price)
        if any(keyword in text_lower for keyword in ['age', 'quantity', 'qty', 'amount', 'count', 'number', 'price', 'cost']):
            return 'number'
        
        # License/Permit/Certification numbers (for applications)
        if any(keyword in text_lower for keyword in ['license', 'licence', 'permit', 'certification', 'certificate']):
            return 'license_number'
        
        # Company/Organization (business applications)
        if any(keyword in text_lower for keyword in ['company', 'organization', 'employer', 'business']):
            return 'company'
        
        # Title/Position (professional profiles)
        if any(keyword in text_lower for keyword in ['title', 'position', 'role', 'job']):
            return 'title'
        
        # Generic text field (fallback for anything else)
        return 'text'
    
    @staticmethod
    def infer_validation_rules(text: str, value: str) -> List[str]:
        """Infer validation rules from field characteristics.
        
        Args:
            text: Combined text from field context
            value: Field value
            
        Returns:
            List of validation rule strings
        """
        rules = []
        
        if 'required' in text or 'mandatory' in text:
            rules.append('required')
        
        if '@' in value or 'email' in text:
            rules.append('email_format')
        
        if any(char.isdigit() for char in value):
            rules.append('contains_numbers')
        
        if any(char.isupper() for char in value) and any(char.islower() for char in value):
            rules.append('mixed_case')
        
        return rules
    
    @staticmethod
    def infer_if_required(text: str, locator: str) -> bool:
        """Check if field is required based on text analysis.
        
        Args:
            text: Field context text
            locator: Field locator string
            
        Returns:
            bool: True if field appears to be required
        """
        return 'required' in text or 'mandatory' in text or '*' in locator
    
    @staticmethod
    def infer_max_length(text: str, value: str) -> Optional[int]:
        """Infer maximum length from value or text hints.
        
        Args:
            text: Field context text
            value: Field value
            
        Returns:
            Optional[int]: Maximum length if detected
        """
        text_lower = text.lower()
        
        # Look for max length hints in text
        max_match = re.search(r'max(?:imum)?[:\s]*(\d+)', text_lower)
        if max_match:
            return int(max_match.group(1))
        
        # For email, standard max is 254
        if '@' in value:
            return 254
        
        # For password, common max is 128
        if 'password' in text_lower:
            return 128
        
        # Default: infer from value length (assume 2-3x current)
        if value:
            return len(value) * 3
        
        return None
    
    @staticmethod
    def extract_field_info_from_action(action: Dict) -> Optional[Dict[str, Any]]:
        """Extract field information from action without hardcoding field types.
        
        Analyzes locator, action text, and value to infer field characteristics.
        
        Args:
            action: Action dictionary containing locator, value, etc.
            
        Returns:
            Optional[Dict]: Field information or None if cannot extract
        """
        locator = action.get('suggested_locator', action.get('selector', ''))
        action_text = action.get('action', action.get('prompt', ''))
        value = action.get('value', '')
        action_type = action.get('action_type', '')
        
        if not locator and not action_text:
            return None
        
        # Combine all available text for analysis
        combined_text = f"{locator} {action_text} {value}".lower()
        
        # Extract field characteristics dynamically
        field_info = {
            'locator': locator,
            'action_text': action_text,
            'value': value,
            'action_type': action_type,
            'inferred_type': FieldAnalyzer.infer_field_type_from_text(combined_text, value),
            'validation_rules': FieldAnalyzer.infer_validation_rules(combined_text, value),
            'is_required': FieldAnalyzer.infer_if_required(combined_text, locator),
            'max_length': FieldAnalyzer.infer_max_length(combined_text, value)
        }
        
        return field_info
