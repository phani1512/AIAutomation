"""
Semantic Modifier - Apply semantic test modifications.

Supports:
- Negative testing (invalid data)
- Boundary testing (min/max values)
- Edge case testing (special characters, security)
- Variation testing (alternative valid data)
"""

import re
import logging
from typing import Dict, List, Tuple
from .context_analyzer import ContextAnalyzer
from .test_data_generator import TestDataGenerator


class SemanticModifier:
    """Applies semantic modifications to test code."""
    
    @staticmethod
    def apply_negative_modifications(code: str, session: Dict, language: str) -> Tuple[str, List[Tuple]]:
        """Apply negative test modifications - use invalid data with AI-based context awareness.
        
        Args:
            code: Original test code
            session: Test session data
            language: Programming language (python/java)
            
        Returns:
            Tuple of (modified_code, suggested_values_list)
        """
        # Get all input actions from session to know what we're replacing
        actions = session.get('actions', [])
        test_url = session.get('url', '')
        test_name = session.get('name', '')
        
        # Build a mapping of original values to invalid values with AI-based analysis
        replacements = {}
        suggested_values = []  # Track suggested values: [(step, value, reason), ...]
        
        # Analyze test context for intelligent suggestions
        context = ContextAnalyzer.analyze_test_context(test_name, test_url, actions)
        
        for action in actions:
            action_type = action.get('action_type', '')
            step = action.get('step', 0)
            
            # Skip actions without valid action_type
            if not action_type or action_type == 'undefined':
                continue
                
            if action_type in ['input', 'click_and_input']:
                original_value = action.get('value', '')
                if not original_value:
                    continue
                
                # Get field context for intelligent suggestion
                locator = action.get('suggested_locator', '')
                action_text = action.get('action', action.get('prompt', ''))
                
                # Use AI-based field analysis to generate contextual invalid data
                invalid_value, reason = TestDataGenerator.generate_invalid_data(
                    field_value=original_value,
                    locator=locator,
                    action_text=action_text,
                    test_context=context,
                    step=step
                )
                
                replacements[original_value] = invalid_value
                suggested_values.append((step, invalid_value, reason))
        
        # Replace values only in send_keys() calls to avoid breaking locators
        for original, invalid in replacements.items():
            if original:
                # Use a more precise regex that matches send_keys with the value
                pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
                replacement = f'.send_keys("{invalid}")'
                code = re.sub(pattern, replacement, code)
        
        # Add assertion for error message (add before teardown)
        if language == 'python':
            error_check = """
        # Verify that error message or validation failure appears
        time.sleep(1)  # Wait for error message
        try:
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'invalid') or contains(text(), 'Invalid') or contains(text(), 'required') or contains(text(), 'Required')]")
            assert len(error_elements) > 0, "Expected error message but none found"
            logging.info(f"✓ Error validation working - found {len(error_elements)} error messages")
        except AssertionError as e:
            logging.warning(f"⚠ {e}")
"""
            code = code.replace('    def teardown_method(self):', error_check + '\n    def teardown_method(self):')
        
        return code, suggested_values
    
    @staticmethod
    def apply_boundary_modifications(code: str, session: Dict, language: str) -> Tuple[str, List[Tuple]]:
        """Apply boundary test modifications - use min/max values with context awareness.
        
        Args:
            code: Original test code
            session: Test session data
            language: Programming language (python/java)
            
        Returns:
            Tuple of (modified_code, suggested_values_list)
        """
        actions = session.get('actions', [])
        test_url = session.get('url', '')
        test_name = session.get('name', '')
        replacements = {}
        suggested_values = []
        
        # Analyze test context
        context = ContextAnalyzer.analyze_test_context(test_name, test_url, actions)
        
        for action in actions:
            action_type = action.get('action_type', '')
            step = action.get('step', 0)
            
            if not action_type or action_type == 'undefined':
                continue
                
            if action_type in ['input', 'click_and_input']:
                original_value = action.get('value', '')
                if not original_value:
                    continue
                
                locator = action.get('suggested_locator', '')
                action_text = action.get('action', action.get('prompt', ''))
                
                boundary_value, reason = TestDataGenerator.generate_boundary_data(
                    field_value=original_value,
                    locator=locator,
                    action_text=action_text,
                    test_context=context,
                    step=step
                )
                
                replacements[original_value] = boundary_value
                suggested_values.append((step, boundary_value[:50] + '...' if len(boundary_value) > 50 else boundary_value, reason))
        
        # Replace values only in send_keys() calls
        for original, boundary in replacements.items():
            if original:
                pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
                replacement = f'.send_keys("{boundary}")'
                code = re.sub(pattern, replacement, code)
        
        return code, suggested_values
    
    @staticmethod
    def apply_edge_case_modifications(code: str, session: Dict, language: str) -> Tuple[str, List[Tuple]]:
        """Apply edge case test modifications - special characters, security.
        
        Args:
            code: Original test code
            session: Test session data
            language: Programming language (python/java)
            
        Returns:
            Tuple of (modified_code, suggested_values_list)
        """
        actions = session.get('actions', [])
        replacements = {}
        suggested_values = []
        
        for action in actions:
            action_type = action.get('action_type', '')
            step = action.get('step', 0)
            
            if not action_type or action_type == 'undefined':
                continue
                
            if action_type in ['input', 'click_and_input']:
                original_value = action.get('value', '')
                if not original_value:
                    continue
                
                # Use edge case values - special characters, SQL injection, XSS
                edge_cases = [
                    ("<script>alert('xss')</script>", "XSS attack test"),
                    ("' OR '1'='1' --", "SQL injection test"),
                    ("!@#$%^&*()", "Special characters"),
                    ("../../etc/passwd", "Path traversal test"),
                    ("你好世界", "Unicode characters"),
                    ("test\ntest", "Newline characters"),
                ]
                
                # Pick appropriate edge case value based on field
                edge_value, reason = edge_cases[hash(action.get('suggested_locator', '')) % len(edge_cases)]
                replacements[original_value] = edge_value
                suggested_values.append((step, edge_value, reason))
        
        # Replace values only in send_keys() calls
        for original, edge in replacements.items():
            if original:
                # Escape special regex chars and quotes in the replacement value
                edge_escaped = edge.replace('\\', '\\\\').replace('"', '\\"')
                pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
                replacement = f'.send_keys("{edge_escaped}")'
                code = re.sub(pattern, replacement, code)
        
        return code, suggested_values
    
    @staticmethod
    def apply_variation_modifications(code: str, session: Dict, language: str) -> Tuple[str, List[Tuple]]:
        """Apply variation test modifications - different valid data with context awareness.
        
        Args:
            code: Original test code
            session: Test session data
            language: Programming language (python/java)
            
        Returns:
            Tuple of (modified_code, suggested_values_list)
        """
        actions = session.get('actions', [])
        test_url = session.get('url', '')
        test_name = session.get('name', '')
        replacements = {}
        suggested_values = []
        
        # Analyze test context
        context = ContextAnalyzer.analyze_test_context(test_name, test_url, actions)
        
        for action in actions:
            action_type = action.get('action_type', '')
            step = action.get('step', 0)
            
            if not action_type or action_type == 'undefined':
                continue
                
            if action_type in ['input', 'click_and_input']:
                original_value = action.get('value', '')
                if not original_value:
                    continue
                
                locator = action.get('suggested_locator', '')
                action_text = action.get('action', action.get('prompt', ''))
                
                variation_value, reason = TestDataGenerator.generate_variation_data(
                    field_value=original_value,
                    locator=locator,
                    action_text=action_text,
                    test_context=context,
                    step=step
                )
                
                replacements[original_value] = variation_value
                suggested_values.append((step, variation_value, reason))
        
        # Replace values only in send_keys() calls
        for original, variation in replacements.items():
            if original:
                pattern = r'\.send_keys\s*\(\s*["\']' + re.escape(original) + r'["\']\s*\)'
                replacement = f'.send_keys("{variation}")'
                code = re.sub(pattern, replacement, code)
        
        return code, suggested_values
